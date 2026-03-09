#!/usr/bin/env python3
import json

try:
    from linear.src.runtime import BotRuntime
except ModuleNotFoundError:
    from runtime import BotRuntime


def _issue_key(actions):
    for action in actions:
        if action.system == "linear" and action.target:
            return action.target
    return "BIT-45"


def _labels(actions):
    values = []
    for action in actions:
        if action.kind in ("set_label", "set_label_if_empty") and "value" in action.payload:
            values.append(action.payload["value"])
    return values


def main() -> int:
    rt = BotRuntime()

    # 1) PR opened -> In Progress
    opened = {
        "action": "opened",
        "pull_request": {
            "number": 101,
            "title": "BIT-45 implement linear bot v1",
            "body": "Implements policy and event handlers",
            "html_url": "https://github.com/BitPod-App/bitpod-tools/pull/101",
            "head": {"ref": "codex/bit-45-bot-v1"},
        },
    }
    step1 = rt.run_github_event(opened)
    issue_key = _issue_key(step1)

    # 2) PR ready_for_review -> In Review + QA Not Done + PM Waiting
    review = {
        "action": "ready_for_review",
        "pull_request": {
            "number": 101,
            "title": "BIT-45 implement linear bot v1",
            "body": "",
            "html_url": "https://github.com/BitPod-App/bitpod-tools/pull/101",
            "head": {"ref": "codex/bit-45-bot-v1"},
        },
    }
    step2 = rt.run_github_event(review)

    # 3) QA comment token -> QA Passed and await PM
    qa = {
        "type": "comment_created",
        "issue_key": issue_key,
        "comment_body": "QA_RESULT=PASSED\nAll checks green.",
        "pr_url": "https://github.com/BitPod-App/bitpod-tools/pull/101",
    }
    step3 = rt.run_linear_event(qa)

    # 4) PM approved label -> authorization comment
    pm = {
        "type": "pm_label_changed",
        "issue_key": issue_key,
        "pm_value": "❇️ PM: Approved",
        "pr_url": "https://github.com/BitPod-App/bitpod-tools/pull/101",
    }
    step4 = rt.run_linear_event(pm)

    # 5) PR merged -> Done when both gates satisfied
    merged = {
        "action": "closed",
        "pull_request": {
            "number": 101,
            "merged": True,
            "merge_commit_sha": "deadbeef",
            "html_url": "https://github.com/BitPod-App/bitpod-tools/pull/101",
        },
        "linear_issue": {
            "identifier": issue_key,
            "labels": ["🔷 QA: Passed", "❇️ PM: Approved"],
        },
    }
    step5 = rt.run_github_event(merged)

    out = {
        "issue_key": issue_key,
        "steps": {
            "pr_opened": [a.__dict__ for a in step1],
            "pr_ready_for_review": [a.__dict__ for a in step2],
            "qa_comment_passed": [a.__dict__ for a in step3],
            "pm_approved": [a.__dict__ for a in step4],
            "pr_merged": [a.__dict__ for a in step5],
        },
        "checks": {
            "step2_has_qa_not_done": "🔶 QA: Not Done" in _labels(step2),
            "step2_has_pm_waiting": "✴️ PM: Waiting" in _labels(step2),
            "step3_has_qa_passed": "🔷 QA: Passed" in _labels(step3),
            "step5_sets_done": any(
                a.kind == "set_status" and a.payload.get("status") == "✅ Done" for a in step5
            ),
        },
    }

    print(json.dumps(out, indent=2))

    if not all(out["checks"].values()):
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
