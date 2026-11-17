// POST /api/users: team accounts, for the owner only.
// actions: list | create {email, password, name, role} | update {email, name, role} | password {email, password} | remove {email}
const { json, readBody, supa, whoIs, need } = require("./_lib");

const ROLES = ["owner", "editor"];
const okPassword = p => typeof p === "string" && p.length >= 10;

async function authUsers() {
  const r = await supa("/auth/v1/admin/users?per_page=1000");
  return (r.data && r.data.users) || [];
}

module.exports = async (req, res) => {
  if (req.method !== "POST") return json(res, 405, { error: "POST only" });
  const missing = need("SUPABASE_URL", "SUPABASE_ANON_KEY", "SUPABASE_SERVICE_ROLE_KEY");
  if (missing.length) return json(res, 500, { error: "Team accounts are not configured yet." });
  const me = await whoIs(req);
  if (me.error) return json(res, me.status, { error: me.error });
  if (me.role !== "owner") return json(res, 403, { error: "Only the owner account can manage the team." });

  const b = await readBody(req);
  const email = String(b.email || "").trim().toLowerCase();
  const role = ROLES.includes(b.role) ? b.role : "editor";

  if (b.action === "list") {
    const [rows, users] = await Promise.all([supa("/rest/v1/cms_users?select=email,name,role,added_at&order=added_at"), authUsers()]);
    const byEmail = Object.fromEntries(users.map(u => [String(u.email || "").toLowerCase(), u]));
    return json(res, 200, { users: (rows.data || []).map(r => ({ ...r, hasLogin: !!byEmail[r.email.toLowerCase()], lastSignIn: byEmail[r.email.toLowerCase()]?.last_sign_in_at || null })) });
  }

  if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) return json(res, 400, { error: "Please enter a valid email." });

  if (b.action === "create") {
    if (!okPassword(b.password)) return json(res, 400, { error: "The password needs at least 10 characters." });
    const existing = (await authUsers()).find(u => String(u.email || "").toLowerCase() === email);
    if (!existing) {
      const r = await supa("/auth/v1/admin/users", { method: "POST", body: JSON.stringify({ email, password: b.password, email_confirm: true }) });
      if (!r.ok) return json(res, 400, { error: (r.data && (r.data.msg || r.data.message)) || "Could not create the sign-in." });
    }
    const up = await supa("/rest/v1/cms_users", { method: "POST", headers: { Prefer: "resolution=merge-duplicates" }, body: JSON.stringify({ email, name: b.name || "", role }) });
    if (!up.ok) return json(res, 400, { error: "The sign-in was made but the role could not be saved." });
    return json(res, 200, { ok: true, message: existing ? "Added to the team (this email already had a sign-in)." : "Account created." });
  }

  if (b.action === "update") {
    if (email === me.email && role !== "owner") return json(res, 400, { error: "You cannot remove your own owner role." });
    const r = await supa(`/rest/v1/cms_users?email=eq.${encodeURIComponent(email)}`, { method: "PATCH", body: JSON.stringify({ role, ...(b.name !== undefined ? { name: b.name } : {}) }) });
    return r.ok ? json(res, 200, { ok: true }) : json(res, 400, { error: "Could not update." });
  }

  if (b.action === "password") {
    if (!okPassword(b.password)) return json(res, 400, { error: "The password needs at least 10 characters." });
    const u = (await authUsers()).find(x => String(x.email || "").toLowerCase() === email);
    if (!u) return json(res, 404, { error: "That person has no sign-in yet." });
    const r = await supa(`/auth/v1/admin/users/${u.id}`, { method: "PUT", body: JSON.stringify({ password: b.password }) });
    return r.ok ? json(res, 200, { ok: true, message: "Password changed." }) : json(res, 400, { error: "Could not change the password." });
  }

  if (b.action === "remove") {
    if (email === me.email) return json(res, 400, { error: "You cannot remove your own account." });
    await supa(`/rest/v1/cms_users?email=eq.${encodeURIComponent(email)}`, { method: "DELETE" });
    const u = (await authUsers()).find(x => String(x.email || "").toLowerCase() === email);
    if (u) await supa(`/auth/v1/admin/users/${u.id}`, { method: "DELETE" });
    return json(res, 200, { ok: true, message: "Removed." });
  }

  return json(res, 400, { error: "Unknown action." });
};
