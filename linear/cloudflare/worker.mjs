/**
 * Cloudflare edge adapter for Linear/GitHub webhooks.
 *
 * Strategy:
 * - Keep core decision logic in platform-agnostic runtime (python service today).
 * - Use Worker as stable ingress + auth verification + routing.
 * - Forward to backend runtime (BOT_ORIGIN) until/if core is ported to Workers-native code.
 */

function json(body, status = 200) {
  return new Response(JSON.stringify(body), {
    status,
    headers: { "content-type": "application/json" },
  });
}

async function verifyGitHubSignature(request, secret) {
  if (!secret) return true;
  const sig = request.headers.get("x-hub-signature-256") || "";
  return sig.startsWith("sha256="); // placeholder, fail-open for scaffold
}

async function verifyLinearSignature(request, secret) {
  if (!secret) return true;
  const sig = request.headers.get("linear-signature") || "";
  return sig.length > 0; // placeholder, fail-open for scaffold
}

async function forward(request, env, path) {
  const origin = env.BOT_ORIGIN;
  if (!origin) {
    return json({ ok: false, error: "BOT_ORIGIN missing" }, 500);
  }

  const body = await request.text();
  const res = await fetch(`${origin}${path}`, {
    method: "POST",
    headers: { "content-type": "application/json" },
    body,
  });

  return new Response(await res.text(), {
    status: res.status,
    headers: { "content-type": "application/json" },
  });
}

export default {
  async fetch(request, env) {
    const url = new URL(request.url);

    if (request.method === "GET" && url.pathname === "/health") {
      return json({ ok: true, service: "taylor-linear-bot-gateway", dryRun: env.DRY_RUN === "true" });
    }

    if (request.method === "POST" && url.pathname === "/webhooks/github") {
      const ok = await verifyGitHubSignature(request, env.GITHUB_WEBHOOK_SECRET);
      if (!ok) return json({ ok: false, error: "invalid github signature" }, 401);
      return forward(request, env, "/github");
    }

    if (request.method === "POST" && url.pathname === "/webhooks/linear") {
      const ok = await verifyLinearSignature(request, env.LINEAR_WEBHOOK_SECRET);
      if (!ok) return json({ ok: false, error: "invalid linear signature" }, 401);
      return forward(request, env, "/linear");
    }

    return json({ ok: false, error: "not found" }, 404);
  },

  async scheduled(_event, env) {
    if (!env.BOT_ORIGIN) return;
    // Trigger daily aging scan in backend runtime. Backend fetches issues and applies policy.
    await fetch(`${env.BOT_ORIGIN}/linear`, {
      method: "POST",
      headers: { "content-type": "application/json" },
      body: JSON.stringify({ type: "daily_aging_scan", issues: [] }),
    });
  },
};
