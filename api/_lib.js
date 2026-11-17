// Shared helpers for the API functions (files starting with "_" are not routes on Vercel).
const env = process.env;

const json = (res, status, body) => {
  res.statusCode = status;
  res.setHeader("Content-Type", "application/json");
  res.setHeader("Cache-Control", "no-store");
  res.end(JSON.stringify(body));
};

const readBody = req => new Promise(resolve => {
  if (req.body && typeof req.body === "object" && !Buffer.isBuffer(req.body)) return resolve(req.body);
  let raw = "";
  req.on("data", c => { raw += c; });
  req.on("end", () => { try { resolve(raw ? JSON.parse(raw) : {}); } catch (e) { resolve({}); } });
});

const readRaw = req => new Promise(resolve => {
  const chunks = [];
  req.on("data", c => chunks.push(Buffer.from(c)));
  req.on("end", () => resolve(Buffer.concat(chunks)));
});

// Supabase REST with the service key (server side only)
const supa = async (path, opts = {}) => {
  const r = await fetch(`${env.SUPABASE_URL}${path}`, {
    ...opts,
    headers: { apikey: env.SUPABASE_SERVICE_ROLE_KEY, Authorization: `Bearer ${env.SUPABASE_SERVICE_ROLE_KEY}`, "Content-Type": "application/json", ...(opts.headers || {}) },
  });
  const text = await r.text();
  let data = null; try { data = text ? JSON.parse(text) : null; } catch (e) { data = text; }
  return { ok: r.ok, status: r.status, data };
};

// Who is calling, and what role do they have?
const whoIs = async req => {
  const token = (req.headers.authorization || "").replace(/^Bearer\s+/i, "");
  if (!token) return { error: "Please sign in.", status: 401 };
  const r = await fetch(`${env.SUPABASE_URL}/auth/v1/user`, { headers: { apikey: env.SUPABASE_ANON_KEY, Authorization: `Bearer ${token}` } });
  if (!r.ok) return { error: "Your session has expired. Please sign in again.", status: 401 };
  const user = await r.json();
  const email = (user.email || "").toLowerCase();
  const row = await supa(`/rest/v1/cms_users?select=email,name,role&email=ilike.${encodeURIComponent(email)}`);
  const me = Array.isArray(row.data) && row.data[0];
  if (!me) return { error: `${email} is not an approved editor.`, status: 403 };
  return { email, role: me.role, name: me.name, userId: user.id };
};

const need = (...names) => names.filter(n => !env[n]);

module.exports = { env, json, readBody, readRaw, supa, whoIs, need };
