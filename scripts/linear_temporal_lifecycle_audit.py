#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import shutil
import sys
import urllib.error
import urllib.request
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Tuple

LINEAR_GRAPHQL_URL = "https://api.linear.app/graphql"
DEFAULT_ACTIVE_TO_CLOSED_DAYS = 15
DEFAULT_CLOSED_TO_PURGE_DAYS = 60
DEFAULT_PURGE_EXPORT_ROOT = "/Users/cjarguello/BitPod-App/local-workspace/local-trash-delete/local-purge/linear-temporal"
META_FILENAME = ".temporal_meta.json"


@dataclass
class Bucket:
    stage: str
    path: Path
    kind: str
    anchor: str
    slug: str = ""


@dataclass
class RemoteStatus:
    anchor: str
    kind: str
    state: str
    transition_at: Optional[datetime]
    source_url: Optional[str]
    raw: Dict[str, Any]


class LinearAPIError(RuntimeError):
    pass


class LinearClient:
    def __init__(self, api_key: str):
        self.api_key = api_key

    def _post(self, query: str, variables: Dict[str, Any]) -> Dict[str, Any]:
        req = urllib.request.Request(
            LINEAR_GRAPHQL_URL,
            data=json.dumps({"query": query, "variables": variables}).encode("utf-8"),
            headers={
                "Content-Type": "application/json",
                "Authorization": self.api_key,
            },
            method="POST",
        )
        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                payload = json.loads(resp.read().decode("utf-8"))
        except urllib.error.HTTPError as exc:
            body = exc.read().decode("utf-8", errors="replace")
            raise LinearAPIError(f"Linear API HTTP {exc.code}: {body}") from exc
        except urllib.error.URLError as exc:
            raise LinearAPIError(f"Linear API connection failed: {exc}") from exc

        if payload.get("errors"):
            raise LinearAPIError(json.dumps(payload["errors"], indent=2))
        return payload.get("data", {})

    def get_issue_status(self, identifier: str) -> Optional[RemoteStatus]:
        query = """
        query($identifier: String!) {
          issues(filter: { identifier: { eq: $identifier } }, first: 1) {
            nodes {
              identifier
              title
              url
              updatedAt
              completedAt
              canceledAt
              archivedAt
              state {
                name
                type
              }
            }
          }
        }
        """
        data = self._post(query, {"identifier": identifier})
        nodes = (((data or {}).get("issues") or {}).get("nodes") or [])
        if not nodes:
            return None
        node = nodes[0]
        transition_at = first_dt(
            node.get("completedAt"),
            node.get("canceledAt"),
            node.get("archivedAt"),
            node.get("updatedAt"),
        )
        state_type = (((node.get("state") or {}).get("type")) or "").lower()
        state = "active"
        if state_type in {"completed", "canceled"} or node.get("completedAt") or node.get("canceledAt") or node.get("archivedAt"):
            state = "closed"
        return RemoteStatus(
            anchor=identifier,
            kind="ticket",
            state=state,
            transition_at=transition_at,
            source_url=node.get("url"),
            raw=node,
        )

    def get_project_status(self, project_id: str) -> Optional[RemoteStatus]:
        query = """
        query($id: String!) {
          project(id: $id) {
            id
            name
            url
            state
            updatedAt
            completedAt
            canceledAt
            archivedAt
          }
        }
        """
        data = self._post(query, {"id": project_id})
        node = (data or {}).get("project")
        if not node:
            return None
        state_name = str(node.get("state") or "").lower()
        transition_at = first_dt(
            node.get("completedAt"),
            node.get("canceledAt"),
            node.get("archivedAt"),
            node.get("updatedAt"),
        )
        state = "active"
        if state_name in {"completed", "canceled", "archived", "done"} or node.get("completedAt") or node.get("canceledAt") or node.get("archivedAt"):
            state = "closed"
        return RemoteStatus(
            anchor=project_id,
            kind="project",
            state=state,
            transition_at=transition_at,
            source_url=node.get("url"),
            raw=node,
        )


def first_dt(*values: Optional[str]) -> Optional[datetime]:
    for value in values:
        if value:
            return parse_dt(value)
    return None


def parse_dt(value: str) -> datetime:
    normalized = value.replace("Z", "+00:00")
    return datetime.fromisoformat(normalized).astimezone(timezone.utc)


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


def load_meta(bucket: Bucket) -> Dict[str, Any]:
    path = bucket.path / META_FILENAME
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text())
    except Exception:
        return {}


def write_meta(bucket_path: Path, payload: Dict[str, Any]) -> None:
    (bucket_path / META_FILENAME).write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")


def cleanup_flags_for_stage(stage: str) -> Dict[str, Any]:
    if stage == "purge":
        status = "purge"
    else:
        status = "hold"
    return {"is_temporal": True, "cleanup_status": status}


def ensure_bucket_meta(bucket: Bucket, reason: str = "") -> None:
    meta = load_meta(bucket)
    changed = False
    for key, value in cleanup_flags_for_stage(bucket.stage).items():
        if meta.get(key) != value:
            meta[key] = value
            changed = True
    if meta.get("bucket_name") != bucket.path.name:
        meta["bucket_name"] = bucket.path.name
        changed = True
    if meta.get("kind") != bucket.kind:
        meta["kind"] = bucket.kind
        changed = True
    if meta.get("anchor") != bucket.anchor:
        meta["anchor"] = bucket.anchor
        changed = True
    if meta.get("slug") != bucket.slug:
        meta["slug"] = bucket.slug
        changed = True
    if reason and meta.get("meta_reason") != reason:
        meta["meta_reason"] = reason
        changed = True
    if changed:
        write_meta(bucket.path, meta)


def mark_failed(bucket_path: Path, action: str, message: str) -> None:
    meta_path = bucket_path / META_FILENAME
    meta: Dict[str, Any] = {}
    if meta_path.exists():
        try:
            meta = json.loads(meta_path.read_text())
        except Exception:
            meta = {}
    meta["is_temporal"] = True
    meta["cleanup_status"] = "failed"
    meta["failure_action"] = action
    meta["last_error"] = message
    meta["last_error_at"] = utcnow().isoformat()
    write_meta(bucket_path, meta)


def bucket_from_path(stage: str, path: Path) -> Optional[Bucket]:
    name = path.name
    if name.startswith("ticket__"):
        return Bucket(stage=stage, path=path, kind="ticket", anchor=name.split("__", 1)[1])
    if name.startswith("project__"):
        parts = name.split("__")
        if len(parts) >= 3:
            return Bucket(stage=stage, path=path, kind="project", slug=parts[1], anchor=parts[2])
    return None


def iter_buckets(stage_dir: Path, stage_name: str) -> Iterable[Bucket]:
    if not stage_dir.exists():
        return []
    buckets: List[Bucket] = []
    for child in sorted(stage_dir.iterdir()):
        if not child.is_dir():
            continue
        bucket = bucket_from_path(stage_name, child)
        if bucket:
            buckets.append(bucket)
    return buckets


def append_markdown_row(table_path: Path, row: List[str], header: List[str]) -> None:
    if not table_path.exists() or not table_path.read_text().strip():
        table_path.write_text(
            "| " + " | ".join(header) + " |\n" +
            "|" + "|".join(["---"] * len(header)) + "|\n"
        )
    with table_path.open("a") as fh:
        fh.write("| " + " | ".join(row) + " |\n")


def bucket_link(stage: str, bucket_name: str) -> str:
    return f"`{stage}/{bucket_name}`"


def latest_checkpoint_summary(bucket: Bucket) -> str:
    checkpoints = sorted(bucket.path.glob("checkpoint-*.md"))
    if not checkpoints:
        return "No checkpoint files"
    return checkpoints[-1].name


def ensure_stage_ledgers(base: Path) -> None:
    for stage in ("active", "closed", "purge"):
        stage_dir = base / stage
        stage_dir.mkdir(parents=True, exist_ok=True)
        checkpoint = stage_dir / "checkpoint_ledger.md"
        if not checkpoint.exists():
            checkpoint.write_text("| Checkpoint | Anchor | Capture date | Summary |\n|---|---|---|---|\n")
    purge_ledger = base / "purge" / "purge_ledger.md"
    if not purge_ledger.exists():
        purge_ledger.write_text("| Bucket | Anchor | Moved at | Reason |\n|---|---|---|---|\n")


def resolve_status(client: Optional[LinearClient], bucket: Bucket, fixture_statuses: Optional[Dict[str, Dict[str, Any]]] = None) -> Tuple[Optional[RemoteStatus], Optional[str]]:
    fixture_key = f"{bucket.kind}:{bucket.anchor}"
    if fixture_statuses and fixture_key in fixture_statuses:
        raw = fixture_statuses[fixture_key]
        transition_at = parse_dt(raw["transition_at"]) if raw.get("transition_at") else None
        return RemoteStatus(anchor=bucket.anchor, kind=bucket.kind, state=raw.get("state", "active"), transition_at=transition_at, source_url=raw.get("source_url"), raw=raw), None
    if client is None:
        return None, "LINEAR_API_KEY not set; remote status unavailable"
    try:
        if bucket.kind == "ticket":
            status = client.get_issue_status(bucket.anchor)
        else:
            status = client.get_project_status(bucket.anchor)
    except LinearAPIError as exc:
        return None, str(exc)
    if status is None:
        return None, f"No Linear object found for {bucket.kind} {bucket.anchor}"
    return status, None


def move_bucket(src: Bucket, dst_stage_dir: Path, moved_at: datetime, reason: str, dry_run: bool) -> Path:
    dst = dst_stage_dir / src.path.name
    if dry_run:
        return dst
    if dst.exists():
        raise RuntimeError(f"Destination already exists: {dst}")
    shutil.move(str(src.path), str(dst))
    meta = load_meta(Bucket(stage=src.stage, path=dst, kind=src.kind, anchor=src.anchor, slug=src.slug))
    meta.update({
        "bucket_name": dst.name,
        "kind": src.kind,
        "anchor": src.anchor,
        "slug": src.slug,
        "last_transition": {
            "from": src.stage,
            "to": dst_stage_dir.name,
            "at": moved_at.isoformat(),
            "reason": reason,
        },
    })
    meta.update(cleanup_flags_for_stage(dst_stage_dir.name))
    write_meta(dst, meta)
    return dst


def process_active_bucket(
    bucket: Bucket,
    base: Path,
    client: Optional[LinearClient],
    grace_days: int,
    dry_run: bool,
    fixture_statuses: Optional[Dict[str, Dict[str, Any]]] = None,
) -> List[str]:
    out: List[str] = []
    status, err = resolve_status(client, bucket, fixture_statuses)
    if err:
        out.append(f"HOLD {bucket.path.name}: {err}")
        return out
    if status.state != "closed":
        out.append(f"KEEP {bucket.path.name}: remote state is active")
        return out
    if not status.transition_at:
        out.append(f"HOLD {bucket.path.name}: remote state is closed but no transition timestamp available")
        return out
    age_days = (utcnow() - status.transition_at).days
    if age_days < grace_days:
        out.append(f"KEEP {bucket.path.name}: closed {age_days}d ago, waiting for {grace_days}d grace window")
        return out
    reason = f"{bucket.kind} {bucket.anchor} closed for {age_days}d (grace {grace_days}d)"
    dst = move_bucket(bucket, base / "closed", utcnow(), reason, dry_run)
    out.append(f"MOVE {bucket.path.name}: active -> closed ({reason}) -> {dst.name}")
    return out




def export_purge_bucket(bucket: Bucket, export_root: Path, dry_run: bool) -> str:
    meta = load_meta(bucket)
    if meta.get("cleanup_status") != "purge":
        return f"HOLD {bucket.path.name}: cleanup_status is not purge"
    export_root.mkdir(parents=True, exist_ok=True)
    dst = export_root / bucket.path.name
    if dry_run:
        return f"EXPORT {bucket.path.name}: purge -> local-purge -> {dst}"
    if dst.exists():
        raise RuntimeError(f"Purge export destination already exists: {dst}")
    shutil.move(str(bucket.path), str(dst))
    exported_meta = meta.copy()
    exported_meta["cleanup_status"] = "deleted"
    exported_meta["exported_to_local_purge_at"] = utcnow().isoformat()
    write_meta(dst, exported_meta)
    return f"EXPORT {bucket.path.name}: purge -> local-purge -> {dst}"


def process_purge_bucket(bucket: Bucket, export_root: Path, dry_run: bool) -> List[str]:
    return [export_purge_bucket(bucket, export_root, dry_run)]

def process_closed_bucket(bucket: Bucket, base: Path, retain_days: int, dry_run: bool) -> List[str]:
    out: List[str] = []
    meta = load_meta(bucket)
    moved = (((meta.get("last_transition") or {}).get("at")) if meta else None)
    if not moved:
        out.append(f"HOLD {bucket.path.name}: no {META_FILENAME} transition timestamp yet")
        return out
    moved_at = parse_dt(moved)
    age_days = (utcnow() - moved_at).days
    if age_days < retain_days:
        out.append(f"KEEP {bucket.path.name}: in closed for {age_days}d, retain until {retain_days}d")
        return out
    reason = f"closed retention exceeded: {age_days}d in closed (threshold {retain_days}d)"
    dst = move_bucket(bucket, base / "purge", utcnow(), reason, dry_run)
    if not dry_run:
        append_markdown_row(
            base / "purge" / "purge_ledger.md",
            [bucket_link("purge", dst.name), f"`{bucket.anchor}`", f"`{utcnow().date().isoformat()}`", reason],
            ["Bucket", "Anchor", "Moved at", "Reason"],
        )
    out.append(f"MOVE {bucket.path.name}: closed -> purge ({reason}) -> {dst.name}")
    return out


def main(argv: List[str]) -> int:
    parser = argparse.ArgumentParser(description="Audit and enforce Linear temporal lifecycle transitions.")
    parser.add_argument("--base", default="/Users/cjarguello/BitPod-App/bitpod-tools/linear/temporal", help="Temporal root directory")
    parser.add_argument("--active-to-closed-days", type=int, default=DEFAULT_ACTIVE_TO_CLOSED_DAYS)
    parser.add_argument("--closed-to-purge-days", type=int, default=DEFAULT_CLOSED_TO_PURGE_DAYS)
    parser.add_argument("--execute", action="store_true", help="Execute moves. Default is dry-run.")
    parser.add_argument("--apply", action="store_true", help="Deprecated alias for --execute.")
    parser.add_argument("--export-purge", action="store_true", help="Move existing temporal/purge buckets into local-workspace/local-trash-delete/local-purge/linear-temporal")
    parser.add_argument("--purge-export-only", action="store_true", help="Skip active/closed lifecycle checks and only process temporal/purge buckets")
    parser.add_argument("--purge-export-root", default=DEFAULT_PURGE_EXPORT_ROOT, help="Destination root for purge export")
    parser.add_argument("--status-file", help="JSON fixture file for local dry-run validation. Keys use kind:anchor, e.g. ticket:BIT-127 or project:0727b3f56ccd")
    args = parser.parse_args(argv)

    base = Path(args.base)
    ensure_stage_ledgers(base)
    for stage_name in ("active", "closed", "purge"):
        for bucket in iter_buckets(base / stage_name, stage_name):
            if args.apply:
                ensure_bucket_meta(bucket, reason="stage metadata normalization")
    client = LinearClient(os.environ["LINEAR_API_KEY"]) if os.environ.get("LINEAR_API_KEY") else None
    execute = bool(args.execute or args.apply)
    dry_run = not execute
    fixture_statuses: Optional[Dict[str, Dict[str, Any]]] = None
    if args.status_file:
        fixture_statuses = json.loads(Path(args.status_file).read_text())

    lines: List[str] = []
    lines.append(f"mode={'DRY-RUN' if dry_run else 'APPLY'}")
    lines.append(f"active_to_closed_days={args.active_to_closed_days}")
    lines.append(f"closed_to_purge_days={args.closed_to_purge_days}")
    lines.append(f"export_purge={str(args.export_purge).lower()}")
    if fixture_statuses is not None:
        lines.append(f"fixture_statuses=enabled ({args.status_file})")
    elif client is None:
        lines.append("linear_api=disabled (LINEAR_API_KEY missing)")
    else:
        lines.append("linear_api=enabled")

    if not args.purge_export_only:
        for bucket in iter_buckets(base / "active", "active"):
            try:
                lines.extend(process_active_bucket(bucket, base, client, args.active_to_closed_days, dry_run, fixture_statuses))
            except Exception as exc:
                if args.apply:
                    mark_failed(bucket.path, "active_to_closed", str(exc))
                lines.append(f"FAIL {bucket.path.name}: active_to_closed: {exc}")
        for bucket in iter_buckets(base / "closed", "closed"):
            try:
                lines.extend(process_closed_bucket(bucket, base, args.closed_to_purge_days, dry_run))
            except Exception as exc:
                if args.apply:
                    mark_failed(bucket.path, "active_to_closed", str(exc))
                lines.append(f"FAIL {bucket.path.name}: active_to_closed: {exc}")
    else:
        lines.append("lifecycle_checks=skipped (purge-export-only)")

    if args.export_purge:
        export_root = Path(args.purge_export_root)
        for bucket in iter_buckets(base / "purge", "purge"):
            try:
                lines.extend(process_purge_bucket(bucket, export_root, dry_run))
            except Exception as exc:
                if args.apply:
                    mark_failed(bucket.path, "active_to_closed", str(exc))
                lines.append(f"FAIL {bucket.path.name}: active_to_closed: {exc}")
    else:
        purge_count = sum(1 for _ in iter_buckets(base / "purge", "purge"))
        lines.append(f"purge_export_pending_buckets={purge_count}")

    print("\n".join(lines))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
