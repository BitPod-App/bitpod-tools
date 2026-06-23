import subprocess
import textwrap
import unittest
from pathlib import Path


class CloudflareWorkerTests(unittest.TestCase):
    def test_worker_verifies_and_forwards_github_signature_and_event(self):
        linear_root = Path(__file__).resolve().parents[1]
        worker = linear_root / "cloudflare" / "worker.mjs"
        script = textwrap.dedent(
            f"""
            import assert from "node:assert/strict";
            import {{ createHmac }} from "node:crypto";
            import worker from {worker.as_uri()!r};

            const body = JSON.stringify({{ action: "opened" }});
            const secret = "worker-github-secret";
            const signature = "sha256=" + createHmac("sha256", secret).update(body).digest("hex");
            const calls = [];
            globalThis.fetch = async (url, init) => {{
              calls.push({{
                url: String(url),
                body: init.body,
                githubEvent: new Headers(init.headers).get("x-github-event"),
                githubSignature: new Headers(init.headers).get("x-hub-signature-256"),
              }});
              return new Response(JSON.stringify({{ ok: true }}), {{ status: 200, headers: {{ "content-type": "application/json" }} }});
            }};

            const request = new Request("https://worker.example/webhooks/github", {{
              method: "POST",
              headers: {{
                "content-type": "application/json",
                "x-github-event": "pull_request",
                "x-hub-signature-256": signature,
              }},
              body,
            }});
            const response = await worker.fetch(request, {{
              BOT_ORIGIN: "https://bot.example",
              GITHUB_WEBHOOK_SECRET: secret,
            }});
            assert.equal(response.status, 200);
            assert.equal(calls.length, 1);
            assert.equal(calls[0].url, "https://bot.example/github");
            assert.equal(calls[0].body, body);
            assert.equal(calls[0].githubEvent, "pull_request");
            assert.equal(calls[0].githubSignature, signature);
            """
        )
        result = subprocess.run(["node", "--input-type=module", "-e", script], text=True, capture_output=True, check=False)

        self.assertEqual(result.returncode, 0, result.stderr)

    def test_worker_verifies_and_forwards_linear_signature(self):
        linear_root = Path(__file__).resolve().parents[1]
        worker = linear_root / "cloudflare" / "worker.mjs"
        script = textwrap.dedent(
            f"""
            import assert from "node:assert/strict";
            import {{ createHmac }} from "node:crypto";
            import worker from {worker.as_uri()!r};

            const body = JSON.stringify({{ type: "agent_session.created", webhookTimestamp: 1781300000000 }});
            const secret = "worker-linear-secret";
            const signature = createHmac("sha256", secret).update(body).digest("hex");
            const calls = [];
            globalThis.fetch = async (url, init) => {{
              calls.push({{
                url: String(url),
                body: init.body,
                linearSignature: new Headers(init.headers).get("linear-signature"),
              }});
              return new Response(JSON.stringify({{ ok: true }}), {{ status: 202, headers: {{ "content-type": "application/json" }} }});
            }};

            const request = new Request("https://worker.example/webhooks/linear", {{
              method: "POST",
              headers: {{ "content-type": "application/json", "linear-signature": signature }},
              body,
            }});
            const response = await worker.fetch(request, {{
              BOT_ORIGIN: "https://bot.example",
              LINEAR_WEBHOOK_SECRET: secret,
            }});
            assert.equal(response.status, 202);
            assert.equal(calls.length, 1);
            assert.equal(calls[0].url, "https://bot.example/linear");
            assert.equal(calls[0].body, body);
            assert.equal(calls[0].linearSignature, signature);
            """
        )
        result = subprocess.run(["node", "--input-type=module", "-e", script], text=True, capture_output=True, check=False)

        self.assertEqual(result.returncode, 0, result.stderr)

    def test_worker_rejects_missing_linear_secret_before_forwarding(self):
        linear_root = Path(__file__).resolve().parents[1]
        worker = linear_root / "cloudflare" / "worker.mjs"
        script = textwrap.dedent(
            f"""
            import assert from "node:assert/strict";
            import worker from {worker.as_uri()!r};

            let fetchCalled = false;
            globalThis.fetch = async () => {{
              fetchCalled = true;
              return new Response("unexpected");
            }};

            const response = await worker.fetch(
              new Request("https://worker.example/webhooks/linear", {{
                method: "POST",
                headers: {{ "content-type": "application/json", "linear-signature": "00" }},
                body: JSON.stringify({{ type: "agent_session.created" }}),
              }}),
              {{ BOT_ORIGIN: "https://bot.example" }},
            );
            assert.equal(response.status, 401);
            assert.equal(fetchCalled, false);
            """
        )
        result = subprocess.run(["node", "--input-type=module", "-e", script], text=True, capture_output=True, check=False)

        self.assertEqual(result.returncode, 0, result.stderr)


if __name__ == "__main__":
    unittest.main()
