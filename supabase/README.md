# Connecting the HexaHessman website editor (/admin)

The editor lives at `/admin/`. Until these steps are done it runs in **draft mode**: everything works, but changes stay in that browser and nothing is published.

Supabase project: `https://bgiveyskxajsxgjeeseu.supabase.co` (already in `admin/config.js`).
GitHub repository: `HexaHessman/HexaHessman-Website`. Vercel project: `hexahessman`.

## 1. Supabase: create the tables
1. `supabase/schema.sql` already makes hexahessman@gmail.com the owner.
2. Supabase > **SQL Editor** > **New query** > paste the whole file > **Run**.

## 2. Supabase: the owner's sign-in
1. **Authentication > Users > Add user > Create new user**: the same owner email, a strong password, tick **Auto Confirm User**.
2. **Authentication > URL Configuration**: Site URL `https://hexahessman-website.vercel.app`, and add `https://hexahessman-website.vercel.app/admin/` to the Redirect URLs (for "Forgot your password?").
3. Everyone else is added later by the owner inside the editor: **Team > Add a person**.

## 3. Supabase: the two keys
**Project Settings > API Keys > "Legacy API keys"** tab (use these, not the new sb_publishable / sb_secret keys):
- **anon public**: public, safe in the page. Goes into `admin/config.js` as `supabaseAnonKey`.
- **service_role**: SECRET. Only ever goes into Vercel and GitHub (below), never into a file.

## 4. GitHub
1. A token for publishing: GitHub > your picture > **Settings > Developer settings > Personal access tokens > Fine-grained tokens > Generate new token**.
   Repository access: only `HexaHessman/HexaHessman-Website`. Permissions: **Contents: Read and write**, **Actions: Read and write**. Copy it (this is `GITHUB_TOKEN` below).
2. The repository > **Settings > Secrets and variables > Actions > New repository secret**, three times:

| Name | Value |
|---|---|
| `SUPABASE_URL` | `https://bgiveyskxajsxgjeeseu.supabase.co` |
| `SUPABASE_SERVICE_ROLE_KEY` | the service_role key |
| `VERCEL_TOKEN` | a Vercel token: vercel.com > your picture > **Account Settings > Tokens > Create** |

## 5. Vercel
Project `hexahessman-website` (the live site, which rebuilds from GitHub on every push) > **Settings > Environment Variables**, for Production:

| Name | Value |
|---|---|
| `SUPABASE_URL` | `https://bgiveyskxajsxgjeeseu.supabase.co` |
| `SUPABASE_ANON_KEY` | the anon public key |
| `SUPABASE_SERVICE_ROLE_KEY` | the service_role key |
| `GITHUB_TOKEN` | the GitHub token from step 4 |
| `GITHUB_REPO` | `HexaHessman/HexaHessman-Website` |

Then deploy the site again so the new settings are used.

## 6. First sign-in
Open `https://hexahessman-website.vercel.app/admin/` and sign in with the owner email and password.

## How publishing works
- Typing in a box saves the change in Supabase at once. Nothing on the website changes yet.
- **Publish to website** calls `/api/publish`, which checks the person is on the team and starts the GitHub workflow **Publish from CMS** (`.github/workflows/cms-publish.yml`).
- That workflow pulls the changes (`tools/cms/pull.py`), rebuilds the pages (`tools/sitegen/build.py`, which runs `tools/cms/cms.py`), commits, pushes and publishes to Vercel. About three minutes.
- The site stays plain static pages, so it stays fast and every word is visible to Google.
- Each run can be watched under the repository's **Actions** tab.

## For the developer
- `admin/seed.json` (the list of every editable word and photo) is rewritten by every build.
- A change matches whole runs of words only (a heading, a paragraph, a button), never part of a sentence.
- Any photo can be swapped for a photo or an MP4 video (it then plays muted on a loop in the same spot). The site's own clips take only videos.
- **Fonts** has four groups (tools/cms/fonts.json). A choice is saved as a change with scope `@fonts`; publishing writes `assets/cms-fonts.css`, which every page loads last.
- The "where it comes from" bar on product pages sizes itself from its legend's percentages (assets/pp-bar.js).
- A changes file downloaded in draft mode can be applied by hand: `python3 tools/cms/cms.py apply hexahessman-changes.json`.
- When a developer later rewrites a sentence in the code, any edit made to the old sentence stops matching. It is still listed in Activity and can be made again.
