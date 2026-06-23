from __future__ import annotations

import json
import os
import time
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass
from typing import Any, Callable, Dict, Iterable, List, Mapping, Optional

try:
    from linear.src.engine import Action
except ModuleNotFoundError:
    from engine import Action


GraphQLTransport = Callable[[str, Dict[str, Any]], Dict[str, Any]]


class LinearExecutionError(RuntimeError):
    """Fail-closed live Linear execution error."""


class LinearActorWrong(LinearExecutionError):
    """Raised when the authenticated Linear actor is not the expected automation actor."""


@dataclass(frozen=True)
class LinearExecutorConfig:
    enabled: bool = False
    api_key: str = ""
    oauth_access_token: str = ""
    oauth_client_id: str = ""
    oauth_client_secret: str = ""
    oauth_scope: str = "read write"
    oauth_token_url: str = "https://api.linear.app/oauth/token"
    api_url: str = "https://api.linear.app/graphql"
    expected_actor_id: str = ""
    expected_actor_name: str = ""
    expected_actor_email: str = ""

    @classmethod
    def from_env(cls) -> "LinearExecutorConfig":
        return cls(
            enabled=os.getenv("LINEAR_LIVE_EXECUTOR_ENABLED", "false").strip().lower() == "true",
            api_key=os.getenv("LINEAR_API_KEY", "").strip(),
            oauth_access_token=(
                os.getenv("LINEAR_OAUTH_ACCESS_TOKEN", "").strip()
                or os.getenv("LINEAR_ACCESS_TOKEN", "").strip()
            ),
            oauth_client_id=os.getenv("LINEAR_OAUTH_CLIENT_ID", "").strip(),
            oauth_client_secret=os.getenv("LINEAR_OAUTH_CLIENT_SECRET", "").strip(),
            oauth_scope=os.getenv("LINEAR_OAUTH_SCOPE", "read write").strip(),
            oauth_token_url=os.getenv("LINEAR_OAUTH_TOKEN_URL", "https://api.linear.app/oauth/token").strip(),
            api_url=os.getenv("LINEAR_API_URL", "https://api.linear.app/graphql").strip(),
            expected_actor_id=os.getenv("LINEAR_EXPECTED_ACTOR_ID", "").strip(),
            expected_actor_name=os.getenv("LINEAR_EXPECTED_ACTOR_NAME", "").strip(),
            expected_actor_email=os.getenv("LINEAR_EXPECTED_ACTOR_EMAIL", "").strip(),
        )


@dataclass(frozen=True)
class LinearExecutionResult:
    outcome: str
    detail: str
    actor: Dict[str, str]


class LinearExecutor:
    """Minimal fail-closed Linear GraphQL executor.

    Live mutations are disabled unless LINEAR_LIVE_EXECUTOR_ENABLED=true, an
    OAuth app-actor client credential pair (preferred), short-lived OAuth bearer
    token, or legacy API key is present, and at least one expected actor field
    is configured and matches the authenticated Linear viewer. Only the first
    rollout actions are supported: comment, agent_activity, set_status, and set_label.
    """

    ALLOWED_KINDS = {"comment", "agent_activity", "set_status", "set_label"}

    def __init__(
        self,
        config: Optional[LinearExecutorConfig] = None,
        transport: Optional[GraphQLTransport] = None,
    ) -> None:
        self.config = config or LinearExecutorConfig.from_env()
        self._transport = transport
        self._actor_cache: Optional[Dict[str, str]] = None
        self._oauth_token_cache: Optional[Dict[str, Any]] = None

    @classmethod
    def from_env(cls) -> "LinearExecutor":
        return cls(LinearExecutorConfig.from_env())

    def execute(self, action: Action) -> LinearExecutionResult:
        self._preflight(action)
        actor = self._verified_actor()

        if action.kind == "comment":
            detail = self._create_comment(action.target, str(action.payload.get("body", "")))
        elif action.kind == "agent_activity":
            detail = self._create_agent_activity(action.target, action.payload.get("content", {}))
        elif action.kind == "set_status":
            detail = self._set_status(
                action.target,
                str(action.payload.get("status", "")),
                str(action.payload.get("source_event", "")),
            )
        elif action.kind == "set_label":
            detail = self._set_label(
                action.target,
                str(action.payload.get("value", "")),
                str(action.payload.get("group", "")),
            )
        else:  # pragma: no cover - guarded by _preflight
            raise LinearExecutionError(f"unsupported linear action: {action.kind}")

        return LinearExecutionResult("executed", detail, actor)

    def _preflight(self, action: Action) -> None:
        if action.system != "linear":
            raise LinearExecutionError(f"linear executor received non-linear action: {action.system}:{action.kind}")
        if action.kind not in self.ALLOWED_KINDS:
            raise LinearExecutionError(f"unsupported linear action: {action.kind}; allowed={sorted(self.ALLOWED_KINDS)}")
        if not self.config.enabled:
            raise LinearExecutionError("linear live executor kill switch is off; set LINEAR_LIVE_EXECUTOR_ENABLED=true to enable")
        if not (
            self.config.api_key
            or self.config.oauth_access_token
            or (self.config.oauth_client_id and self.config.oauth_client_secret)
        ) and self._transport is None:
            raise LinearExecutionError("LINEAR_OAUTH_CLIENT_ID/SECRET, LINEAR_OAUTH_ACCESS_TOKEN, or LINEAR_API_KEY is required for live Linear execution")
        if not any(
            [
                self.config.expected_actor_id,
                self.config.expected_actor_name,
                self.config.expected_actor_email,
            ]
        ):
            raise LinearExecutionError(
                "linear actor attribution check is not configured; set LINEAR_EXPECTED_ACTOR_ID, LINEAR_EXPECTED_ACTOR_NAME, or LINEAR_EXPECTED_ACTOR_EMAIL"
            )

    def _verified_actor(self) -> Dict[str, str]:
        if self._actor_cache is not None:
            return self._actor_cache

        data = self._graphql(
            """
            query LinearExecutorViewer {
              viewer {
                id
                name
                email
              }
            }
            """,
            {},
        )
        viewer = ((data.get("data") or {}).get("viewer") or {})
        actor = {
            "id": str(viewer.get("id") or ""),
            "name": str(viewer.get("name") or ""),
            "email": str(viewer.get("email") or ""),
        }
        mismatches: List[str] = []
        if self.config.expected_actor_id and actor["id"] != self.config.expected_actor_id:
            mismatches.append(f"id expected {self.config.expected_actor_id!r} got {actor['id']!r}")
        if self.config.expected_actor_name and actor["name"].casefold() != self.config.expected_actor_name.casefold():
            mismatches.append(f"name expected {self.config.expected_actor_name!r} got {actor['name']!r}")
        if self.config.expected_actor_email and actor["email"].casefold() != self.config.expected_actor_email.casefold():
            mismatches.append(f"email expected {self.config.expected_actor_email!r} got {actor['email']!r}")
        if mismatches:
            raise LinearActorWrong("LINEAR ACTOR WRONG: " + "; ".join(mismatches))
        self._actor_cache = actor
        return actor

    def _graphql(self, query: str, variables: Dict[str, Any]) -> Dict[str, Any]:
        if self._transport is not None:
            data = self._transport(query, variables)
        else:
            body = json.dumps({"query": query, "variables": variables}).encode("utf-8")
            request = urllib.request.Request(
                self.config.api_url,
                data=body,
                headers={
                    "Authorization": self._authorization_header(),
                    "Content-Type": "application/json",
                },
                method="POST",
            )
            try:
                with urllib.request.urlopen(request, timeout=20) as response:
                    data = json.loads(response.read().decode("utf-8"))
            except urllib.error.HTTPError as exc:
                detail = exc.read().decode("utf-8", errors="replace")
                raise LinearExecutionError(f"Linear GraphQL HTTP {exc.code}: {detail}") from exc
            except (urllib.error.URLError, TimeoutError) as exc:
                raise LinearExecutionError(f"Linear GraphQL request failed: {exc}") from exc

        errors = data.get("errors") if isinstance(data, dict) else None
        if errors:
            raise LinearExecutionError("Linear GraphQL error: " + json.dumps(errors, sort_keys=True))
        if not isinstance(data, dict) or "data" not in data:
            raise LinearExecutionError("Linear GraphQL response missing data")
        return data

    def _authorization_header(self) -> str:
        if self.config.oauth_access_token:
            return f"Bearer {self.config.oauth_access_token}"
        if self.config.oauth_client_id and self.config.oauth_client_secret:
            token = self._client_credentials_access_token()
            return f"Bearer {token}"
        return self.config.api_key

    def _client_credentials_access_token(self) -> str:
        now = time.time()
        if self._oauth_token_cache:
            token = str(self._oauth_token_cache.get("access_token") or "")
            expires_at = float(self._oauth_token_cache.get("expires_at") or 0)
            if token and expires_at > now + 60:
                return token
        token, expires_in = self._fetch_client_credentials_access_token()
        if not token:
            raise LinearExecutionError("Linear OAuth client_credentials response missing access_token")
        self._oauth_token_cache = {
            "access_token": token,
            "expires_at": now + max(int(expires_in or 0), 0),
        }
        return token

    def _fetch_client_credentials_access_token(self) -> tuple[str, int]:
        body = urllib.parse.urlencode(
            {
                "grant_type": "client_credentials",
                "client_id": self.config.oauth_client_id,
                "client_secret": self.config.oauth_client_secret,
                "scope": self.config.oauth_scope,
            }
        ).encode("utf-8")
        request = urllib.request.Request(
            self.config.oauth_token_url,
            data=body,
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            method="POST",
        )
        try:
            with urllib.request.urlopen(request, timeout=20) as response:
                data = json.loads(response.read().decode("utf-8"))
        except urllib.error.HTTPError as exc:
            detail = exc.read().decode("utf-8", errors="replace")
            raise LinearExecutionError(f"Linear OAuth token HTTP {exc.code}: {detail}") from exc
        except (urllib.error.URLError, TimeoutError) as exc:
            raise LinearExecutionError(f"Linear OAuth token request failed: {exc}") from exc
        return str(data.get("access_token") or ""), int(data.get("expires_in") or 0)

    def _get_issue(self, issue_ref: str) -> Dict[str, Any]:
        data = self._graphql(
            """
            query LinearExecutorIssue($id: String!) {
              issue(id: $id) {
                id
                identifier
                team { id key name }
                state { id name }
                labels { nodes { id name parent { id name } } }
              }
            }
            """,
            {"id": issue_ref},
        )
        issue = ((data.get("data") or {}).get("issue") or None)
        if not issue:
            raise LinearExecutionError(f"Linear issue not found: {issue_ref}")
        return issue

    def _create_comment(self, issue_ref: str, body: str) -> str:
        if not body.strip():
            raise LinearExecutionError("comment body is required")
        issue = self._get_issue(issue_ref)
        data = self._graphql(
            """
            mutation LinearExecutorCommentCreate($issueId: String!, $body: String!) {
              commentCreate(input: { issueId: $issueId, body: $body }) {
                success
                comment { id url user { id name email } }
              }
            }
            """,
            {"issueId": issue["id"], "body": body},
        )
        result = ((data.get("data") or {}).get("commentCreate") or {})
        if not result.get("success"):
            raise LinearExecutionError(f"Linear commentCreate failed for {issue_ref}")
        self._verify_mutation_actor(((result.get("comment") or {}).get("user") or None))
        comment = result.get("comment") or {}
        return f"linear commentCreate {issue.get('identifier', issue_ref)} comment={comment.get('id', '')}"

    def _create_agent_activity(self, agent_session_id: str, content: Any) -> str:
        session_id = str(agent_session_id or "").strip()
        if not session_id:
            raise LinearExecutionError("agentSessionId is required for agent activity")
        if not isinstance(content, Mapping) or not str(content.get("type") or "").strip():
            raise LinearExecutionError("agent activity content with type is required")
        data = self._graphql(
            """
            mutation LinearExecutorAgentActivityCreate($input: AgentActivityCreateInput!) {
              agentActivityCreate(input: $input) {
                success
                agentActivity { id }
              }
            }
            """,
            {"input": {"agentSessionId": session_id, "content": dict(content)}},
        )
        result = ((data.get("data") or {}).get("agentActivityCreate") or {})
        if not result.get("success"):
            raise LinearExecutionError(f"Linear agentActivityCreate failed for session {session_id}")
        activity = result.get("agentActivity") or {}
        return f"linear agentActivityCreate session={session_id} activity={activity.get('id', '')}"

    def _set_status(self, issue_ref: str, status_name: str, source_event: str = "") -> str:
        if not status_name.strip():
            raise LinearExecutionError("status is required")
        issue = self._get_issue(issue_ref)
        current_status = str(((issue.get("state") or {}).get("name")) or "")
        if (
            source_event == "github_cj_qa_override"
            and status_name.casefold() == "delivered"
            and current_status.casefold() != "in review"
        ):
            raise LinearExecutionError(
                f"CJ QA override may move an issue to Delivered only when it is currently In Review; "
                f"{issue_ref} is currently {current_status or 'unknown'}"
            )
        state_id = self._find_workflow_state_id(issue, status_name)
        data = self._graphql(
            """
            mutation LinearExecutorIssueSetStatus($id: String!, $stateId: String!) {
              issueUpdate(id: $id, input: { stateId: $stateId }) {
                success
                issue { id identifier state { id name } }
              }
            }
            """,
            {"id": issue["id"], "stateId": state_id},
        )
        result = ((data.get("data") or {}).get("issueUpdate") or {})
        if not result.get("success"):
            raise LinearExecutionError(f"Linear issueUpdate state failed for {issue_ref}")
        updated = result.get("issue") or {}
        return f"linear issueUpdate status {updated.get('identifier', issue_ref)} -> {status_name}"

    def _set_label(self, issue_ref: str, label_name: str, group_name: str = "") -> str:
        if not label_name.strip():
            raise LinearExecutionError("label value is required")
        issue = self._get_issue(issue_ref)
        label_id = self._find_issue_label_id(issue, label_name, group_name)
        current_label_ids = self._current_label_ids(issue, replace_group_name=group_name)
        label_ids = sorted(set(current_label_ids + [label_id]))
        data = self._graphql(
            """
            mutation LinearExecutorIssueSetLabel($id: String!, $labelIds: [String!]) {
              issueUpdate(id: $id, input: { labelIds: $labelIds }) {
                success
                issue { id identifier labels { nodes { id name } } }
              }
            }
            """,
            {"id": issue["id"], "labelIds": label_ids},
        )
        result = ((data.get("data") or {}).get("issueUpdate") or {})
        if not result.get("success"):
            raise LinearExecutionError(f"Linear issueUpdate labels failed for {issue_ref}")
        updated = result.get("issue") or {}
        qualified = f"{group_name}/{label_name}" if group_name else label_name
        return f"linear issueUpdate label {updated.get('identifier', issue_ref)} += {qualified}"

    def _find_workflow_state_id(self, issue: Mapping[str, Any], status_name: str) -> str:
        team = issue.get("team") or {}
        team_id = str(team.get("id") or "")
        data = self._graphql(
            """
            query LinearExecutorWorkflowStates {
              workflowStates(first: 250) {
                nodes { id name team { id key name } }
              }
            }
            """,
            {},
        )
        states = (((data.get("data") or {}).get("workflowStates") or {}).get("nodes") or [])
        matches = [
            state
            for state in states
            if str(state.get("name") or "").casefold() == status_name.casefold()
            and str((state.get("team") or {}).get("id") or "") == team_id
        ]
        if len(matches) != 1:
            raise LinearExecutionError(
                f"expected exactly one workflow state named {status_name!r} for team {team.get('key') or team_id}; found {len(matches)}"
            )
        return str(matches[0]["id"])

    def _find_issue_label_id(self, issue: Mapping[str, Any], label_name: str, group_name: str = "") -> str:
        team = issue.get("team") or {}
        team_id = str(team.get("id") or "")
        data = self._graphql(
            """
            query LinearExecutorIssueLabels {
              issueLabels(first: 250) {
                nodes { id name team { id key name } parent { id name } }
              }
            }
            """,
            {},
        )
        labels = (((data.get("data") or {}).get("issueLabels") or {}).get("nodes") or [])

        def team_matches(label: Mapping[str, Any]) -> bool:
            label_team = label.get("team")
            return label_team is None or str((label_team or {}).get("id") or "") == team_id

        def group_matches(label: Mapping[str, Any]) -> bool:
            if not group_name:
                return True
            parent = label.get("parent") or {}
            return str(parent.get("name") or "").casefold() == group_name.casefold()

        matches = [
            label
            for label in labels
            if str(label.get("name") or "").casefold() == label_name.casefold()
            and team_matches(label)
            and group_matches(label)
        ]
        if len(matches) != 1:
            qualifier = f" in group {group_name!r}" if group_name else ""
            raise LinearExecutionError(
                f"expected exactly one issue label named {label_name!r}{qualifier} for team {team.get('key') or team_id}; found {len(matches)}"
            )
        return str(matches[0]["id"])

    def _verify_mutation_actor(self, user: Optional[Mapping[str, Any]]) -> None:
        if not user:
            return
        actor = self._verified_actor()
        actual = {
            "id": str(user.get("id") or ""),
            "name": str(user.get("name") or ""),
            "email": str(user.get("email") or ""),
        }
        mismatches = [f"comment user {key} expected {actor[key]!r} got {actual[key]!r}" for key in actor if actual[key] and actual[key] != actor[key]]
        if mismatches:
            raise LinearActorWrong("LINEAR ACTOR WRONG: " + "; ".join(mismatches))

    def _current_label_ids(self, issue: Mapping[str, Any], replace_group_name: str = "") -> List[str]:
        labels = (((issue.get("labels") or {}).get("nodes")) or [])
        ids = []
        for label in labels:
            if not label.get("id"):
                continue
            parent = label.get("parent") or {}
            if replace_group_name and str(parent.get("name") or "").casefold() == replace_group_name.casefold():
                continue
            ids.append(str(label.get("id")))
        return ids
