#!/usr/bin/env python3
import argparse
import json
import os
import urllib.request
from pathlib import Path
from typing import Optional


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SEED = ROOT / "projects" / "taylor01_claw_v1_issue_seed.json"
API_URL = "https://api.linear.app/graphql"


def load_seed(path: Path):
    with path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    issues = payload.get("issues")
    if not isinstance(issues, list) or not issues:
        raise SystemExit(f"invalid issue seed: {path}")
    return payload


def gql_request(token: str, query: str, variables: dict):
    req = urllib.request.Request(
        API_URL,
        data=json.dumps({"query": query, "variables": variables}).encode("utf-8"),
        headers={
            "Authorization": token,
            "Content-Type": "application/json",
        },
        method="POST",
    )
    with urllib.request.urlopen(req) as response:
        return json.loads(response.read().decode("utf-8"))


def resolve_team_id(token: str, team_key: str):
    query = """
    query Teams {
      teams {
        nodes {
          id
          key
          name
        }
      }
    }
    """
    payload = gql_request(token, query, {})
    nodes = payload.get("data", {}).get("teams", {}).get("nodes", [])
    for node in nodes:
        if node.get("key") == team_key:
            return node["id"]
    raise SystemExit(f"team key not found: {team_key}")


def resolve_project_id(token: str, project_name: str):
    query = """
    query Projects {
      projects {
        nodes {
          id
          name
        }
      }
    }
    """
    payload = gql_request(token, query, {})
    nodes = payload.get("data", {}).get("projects", {}).get("nodes", [])
    for node in nodes:
        if node.get("name") == project_name:
            return node["id"]
    raise SystemExit(f"project name not found: {project_name}")


def resolve_state_id(token: str, team_id: str, state_name: str) -> str:
    query = """
    query TeamStates($id: ID!) {
      team(id: $id) {
        id
        key
        name
        states {
          nodes {
            id
            name
            type
            position
          }
        }
      }
    }
    """
    payload = gql_request(token, query, {"id": team_id})
    errors = payload.get("errors")
    if errors:
        raise SystemExit(json.dumps(errors, indent=2))
    nodes = payload.get("data", {}).get("team", {}).get("states", {}).get("nodes", [])
    if not nodes:
        raise SystemExit(f"no workflow states returned for team_id={team_id}")
    for node in nodes:
        if node.get("name") == state_name:
            return node["id"]
    options = ", ".join(sorted({n.get("name", "") for n in nodes if n.get("name")}))
    raise SystemExit(f"workflow state not found: {state_name!r}. options: {options}")


def create_issue(
    token: str,
    team_id: str,
    project_id: Optional[str],
    title: str,
    description: str,
    state_id: Optional[str] = None,
):
    query = """
    mutation CreateIssue($input: IssueCreateInput!) {
      issueCreate(input: $input) {
        success
        issue {
          id
          identifier
          title
          url
        }
      }
    }
    """
    input_payload = {
        "teamId": team_id,
        "title": title,
        "description": description,
    }
    if project_id:
        input_payload["projectId"] = project_id
    if state_id:
        input_payload["stateId"] = state_id
    payload = gql_request(token, query, {"input": input_payload})
    errors = payload.get("errors")
    if errors:
        raise SystemExit(json.dumps(errors, indent=2))
    created = payload["data"]["issueCreate"]
    if not created.get("success"):
        raise SystemExit(f"issue creation failed for: {title}")
    return created["issue"]


def print_seed(seed_payload):
    print(f"seed_name={seed_payload.get('seed_name', 'unknown')}")
    for idx, issue in enumerate(seed_payload["issues"], start=1):
        print(f"\n[{idx}] {issue['title']}\n")
        print(issue["description"])


def main():
    parser = argparse.ArgumentParser(description="Create Linear issues from a JSON seed.")
    parser.add_argument("--seed", default=str(DEFAULT_SEED))
    parser.add_argument("--team-key", default="BIT")
    parser.add_argument("--project-name", default="Taylor01")
    parser.add_argument(
        "--state-name",
        default="Backlog",
        help="Workflow state name to use on create (resolved to stateId). Defaults to Backlog.",
    )
    parser.add_argument(
        "--state-id",
        default="",
        help="Workflow state ID to use on create (overrides --state-name). Recommended when toolchains have name-resolution ambiguity.",
    )
    parser.add_argument("--live", action="store_true")
    args = parser.parse_args()

    seed = load_seed(Path(args.seed))
    if not args.live:
        print_seed(seed)
        print("\nDRY RUN ONLY. Re-run with --live and LINEAR_API_KEY set to create issues.")
        return

    token = os.environ.get("LINEAR_API_KEY")
    if not token:
        raise SystemExit("LINEAR_API_KEY is required for --live")

    team_id = resolve_team_id(token, args.team_key)
    project_id = resolve_project_id(token, args.project_name)
    requested_state_id = args.state_id.strip() or None
    if requested_state_id is None:
        requested_state_id = resolve_state_id(token, team_id, args.state_name)
    for issue in seed["issues"]:
        created = create_issue(
            token=token,
            team_id=team_id,
            project_id=project_id,
            title=issue["title"],
            description=issue["description"],
            state_id=requested_state_id,
        )
        print(f"{created['identifier']}: {created['title']} -> {created['url']}")


if __name__ == "__main__":
    main()
