#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import shutil
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

VALID_BUCKET_PREFIXES = ("ticket__", "project__")
VALID_STATUSES = {"hold", "purge", "deleted", "failed"}
STAGES = ("active", "closed", "purge")


@dataclass
class Bucket:
    stage: str
    path: Path

    @property
    def name(self) -> str:
        return self.path.name

    @property
    def meta_path(self) -> Path:
        return self.path / ".temporal_meta.json"


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def default_status_for_stage(stage: str) -> str:
    return "purge" if stage == "purge" else "hold"


def default_meta(bucket: Bucket) -> dict:
    return {
        "is_temporal": True,
        "cleanup_status": default_status_for_stage(bucket.stage),
        "bucket_name": bucket.name,
        "stage": bucket.stage,
        "last_synced_at": utc_now(),
    }


def load_meta(bucket: Bucket) -> dict | None:
    if not bucket.meta_path.exists():
        return None
    try:
        return json.loads(bucket.meta_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return None


def normalize_meta(bucket: Bucket, meta: dict | None) -> tuple[dict, list[str]]:
    notes: list[str] = []
    normalized = default_meta(bucket)
    if meta is None:
        notes.append("missing_meta")
        return normalized, notes

    if meta.get("is_temporal") is not True:
        notes.append("set_is_temporal")
    if meta.get("cleanup_status") not in VALID_STATUSES:
        notes.append("set_cleanup_status")
    if meta.get("bucket_name") not in (bucket.name, None):
        notes.append("reset_bucket_name")
    if meta.get("stage") not in (bucket.stage, None):
        notes.append("reset_stage")

    normalized.update({k: v for k, v in meta.items() if k not in {"cleanup_status", "is_temporal", "bucket_name", "stage", "last_synced_at"}})
    normalized["is_temporal"] = True
    normalized["cleanup_status"] = meta.get("cleanup_status") if meta.get("cleanup_status") in VALID_STATUSES else default_status_for_stage(bucket.stage)
    normalized["bucket_name"] = bucket.name
    normalized["stage"] = bucket.stage
    normalized["last_synced_at"] = utc_now()
    return normalized, notes


def write_meta(path: Path, payload: dict) -> None:
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def iter_buckets(temporal_root: Path) -> list[Bucket]:
    buckets: list[Bucket] = []
    for stage in STAGES:
        stage_dir = temporal_root / stage
        if not stage_dir.exists():
            continue
        for child in sorted(stage_dir.iterdir()):
            if not child.is_dir() or child.name.startswith("."):
                continue
            if not child.name.startswith(VALID_BUCKET_PREFIXES):
                continue
            buckets.append(Bucket(stage=stage, path=child))
    return buckets


def export_purge_bucket(bucket: Bucket, root: Path, execute: bool) -> tuple[str, str]:
    destination_root = root / "local-workspace" / "local-trash-delete" / "local-purge" / "linear-temporal"
    destination = destination_root / bucket.name
    source_meta, _ = normalize_meta(bucket, load_meta(bucket))

    if source_meta["cleanup_status"] != "purge":
        return "SKIP", f"cleanup_status={source_meta['cleanup_status']}"

    if destination.exists():
        failure = dict(source_meta)
        failure["cleanup_status"] = "failed"
        failure["failure_action"] = "purge_export"
        failure["last_error"] = f"destination_exists:{destination}"
        failure["last_error_at"] = utc_now()
        if execute:
            write_meta(bucket.meta_path, failure)
        return "FAIL", f"destination exists: {destination}"

    if not execute:
        return "PLAN", f"export -> {destination}"

    try:
        destination_root.mkdir(parents=True, exist_ok=True)
        shutil.move(str(bucket.path), str(destination))
        exported_meta = dict(source_meta)
        exported_meta["cleanup_status"] = "deleted"
        exported_meta["stage"] = "local-purge"
        exported_meta["deleted_at"] = utc_now()
        exported_meta["last_synced_at"] = utc_now()
        write_meta(destination / ".temporal_meta.json", exported_meta)
        return "DONE", f"exported -> {destination}"
    except Exception as exc:  # pragma: no cover - defensive path
        failure = dict(source_meta)
        failure["cleanup_status"] = "failed"
        failure["failure_action"] = "purge_export"
        failure["last_error"] = str(exc)
        failure["last_error_at"] = utc_now()
        write_meta(bucket.meta_path, failure)
        return "FAIL", str(exc)


def render_report(rows: list[str]) -> str:
    header = [
        "# Linear Temporal Lifecycle Audit",
        "",
        f"- generated_at: {utc_now()}",
        "- model: is_temporal=true + cleanup_status=hold|purge|deleted|failed",
        "- scheduler_contract: filesystem-only; no Linear lookups",
        "",
    ]
    if not rows:
        header.append("- no temporal buckets found")
        return "\n".join(header) + "\n"
    return "\n".join(header + rows) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(prog="linear_temporal_lifecycle_audit")
    parser.add_argument("--root", default="/Users/cjarguello/BitPod-App")
    parser.add_argument("--execute", action="store_true", help="Write normalized metadata and perform exports")
    parser.add_argument("--export-purge", action="store_true", help="Evaluate purge buckets for export into local-purge")
    args = parser.parse_args()

    root = Path(args.root).expanduser().resolve()
    temporal_root = root / "bitpod-tools" / "linear" / "temporal"
    buckets = iter_buckets(temporal_root)
    rows: list[str] = []

    for bucket in buckets:
        meta = load_meta(bucket)
        normalized, notes = normalize_meta(bucket, meta)
        if args.execute:
            write_meta(bucket.meta_path, normalized)
        note_suffix = f" notes={','.join(notes)}" if notes else ""
        rows.append(f"- bucket={bucket.name} stage={bucket.stage} cleanup_status={normalized['cleanup_status']} execute={'yes' if args.execute else 'no'}{note_suffix}")
        if args.export_purge and bucket.stage == "purge":
            action, detail = export_purge_bucket(bucket, root, args.execute)
            rows.append(f"  - purge_export={action} detail={detail}")

    sys.stdout.write(render_report(rows))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
