#!/usr/bin/env python3
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CONTRACTS = ROOT / "contracts"
EXAMPLES = ROOT / "examples"


def load_json(path: Path):
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def main():
    states = load_json(CONTRACTS / "runtime_states_v1.json")
    agents = load_json(CONTRACTS / "agent_registry_v1.json")
    tools = load_json(CONTRACTS / "tool_registry_v1.json")
    trace = load_json(EXAMPLES / "taylor_delegated_trace_v1.json")

    state_ids = {item["id"] for item in states["states"]}
    agent_ids = {item["id"] for item in agents["agents"]}
    tool_ids = {item["id"] for item in tools["tools"]}

    missing_states = [
        item["state"] for item in trace["states"] if item["state"] not in state_ids
    ]
    missing_actors = [
        item["actor"] for item in trace["states"] if item["actor"] not in agent_ids
    ]

    missing_delegates = []
    for item in trace["states"]:
        for delegation in item.get("delegations", []):
            if delegation["owner"] not in agent_ids:
                missing_delegates.append(delegation["owner"])

    missing_tools = []
    for agent in agents["agents"]:
        for tool_id in agent["allowed_tools"]:
            if tool_id not in tool_ids:
                missing_tools.append((agent["id"], tool_id))

    if missing_states or missing_actors or missing_delegates or missing_tools:
        raise SystemExit(
            "runtime artifact validation failed: "
            f"missing_states={missing_states}, "
            f"missing_actors={missing_actors}, "
            f"missing_delegates={missing_delegates}, "
            f"missing_tools={missing_tools}"
        )

    print("runtime contract artifacts PASS")


if __name__ == "__main__":
    main()
