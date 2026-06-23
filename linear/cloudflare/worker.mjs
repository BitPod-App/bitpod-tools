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

async function hmacSha256Hex(secret, body) {
  const key = await crypto.subtle.importKey(
    "raw",
    new TextEncoder().encode(secret),
    { name: "HMAC", hash: "SHA-256" },
    false,
    ["sign"],
  );
  const signature = await crypto.subtle.sign("HMAC", key, new TextEncoder().encode(body));
  return [...new Uint8Array(signature)].map((byte) => byte.toString(16).padStart(2, "0")).join("");
}

function normalizeSignature(value) {
  return (value || "").trim().replace(/^sha256=/i, "");
}

async function verifyHmacSignature(body, signatureHeader, secret) {
  if (!secret) return false;
  const signature = normalizeSignature(signatureHeader);
  if (!signature) return false;
  const expected = await hmacSha256Hex(secret, body);
  return signature.length === expected.length && signature.toLowerCase() === expected;
}

async function verifyGitHubSignature(body, signatureHeader, secret) {
  return verifyHmacSignature(body, signatureHeader, secret);
}

async function verifyLinearSignature(body, signatureHeader, secret) {
  return verifyHmacSignature(body, signatureHeader, secret);
}

async function forward(body, request, env, path) {
  const origin = env.BOT_ORIGIN;
  if (!origin) {
    return json({ ok: false, error: "BOT_ORIGIN missing" }, 500);
  }

  const res = await fetch(`${origin}${path}`, {
    method: "POST",
    headers: {
      "content-type": request.headers.get("content-type") || "application/json",
      "x-github-event": request.headers.get("x-github-event") || "",
      "x-hub-signature-256": request.headers.get("x-hub-signature-256") || "",
      "linear-signature": request.headers.get("linear-signature") || "",
    },
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
      const body = await request.text();
      const ok = await verifyGitHubSignature(body, request.headers.get("x-hub-signature-256"), env.GITHUB_WEBHOOK_SECRET);
      if (!ok) return json({ ok: false, error: "invalid github signature" }, 401);
      return forward(body, request, env, "/github");
    }

    if (request.method === "POST" && url.pathname === "/webhooks/linear") {
      const body = await request.text();
      const ok = await verifyLinearSignature(body, request.headers.get("linear-signature"), env.LINEAR_WEBHOOK_SECRET);
      if (!ok) return json({ ok: false, error: "invalid linear signature" }, 401);
      return forward(body, request, env, "/linear");
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
