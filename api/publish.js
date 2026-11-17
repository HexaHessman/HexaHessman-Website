// POST /api/publish: a team member asks for the website to be rebuilt with the latest changes.
// It starts the GitHub workflow "Publish from CMS" (.github/workflows/cms-publish.yml), which pulls the changes,
// rebuilds the pages and publishes them. Environment: SUPABASE_URL, SUPABASE_ANON_KEY, SUPABASE_SERVICE_ROLE_KEY,
// GITHUB_TOKEN, GITHUB_REPO
const { env, json, supa, whoIs, need } = require("./_lib");

module.exports = async (req, res) => {
  if (req.method !== "POST") return json(res, 405, { error: "POST only" });
  if (need("SUPABASE_URL", "SUPABASE_ANON_KEY", "SUPABASE_SERVICE_ROLE_KEY", "GITHUB_TOKEN", "GITHUB_REPO").length)
    return json(res, 500, { error: "Publishing is not connected yet (missing settings on Vercel)." });
  const me = await whoIs(req);
  if (me.error) return json(res, me.status, { error: me.error });

  await supa("/rest/v1/cms_publishes", { method: "POST", headers: { Prefer: "return=minimal" }, body: JSON.stringify({ requested_by: me.email, status: "queued" }) }).catch(() => {});
  const r = await fetch(`https://api.github.com/repos/${env.GITHUB_REPO}/dispatches`, {
    method: "POST",
    headers: { Authorization: `Bearer ${env.GITHUB_TOKEN}`, Accept: "application/vnd.github+json", "Content-Type": "application/json", "User-Agent": "hexahessman-cms" },
    body: JSON.stringify({ event_type: "cms-publish", client_payload: { by: me.email } }),
  });
  if (r.status !== 204) return json(res, 502, { error: "GitHub did not accept the publish request.", detail: (await r.text().catch(() => "")).slice(0, 300) });
  return json(res, 200, { ok: true, message: "Publishing. The website updates in about three minutes." });
};
