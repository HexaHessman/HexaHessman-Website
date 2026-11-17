// HexaHessman website editor: connection settings.
// Leave both Supabase values empty to run in draft mode (changes stay in this browser, nothing is published).
// Both values are public (they are safe in the page); the secret keys go in Vercel and GitHub only (supabase/README.md).
window.HH_CMS_CONFIG = {
  supabaseUrl: "https://bgiveyskxajsxgjeeseu.supabase.co",      // e.g. "https://abcdefghijklmnop.supabase.co"  (Supabase > Project Settings > API > Project URL)
  supabaseAnonKey: "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImJnaXZleXNreGFqc3hnamVlc2V1Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3OTQ4ODM5ODYsImV4cCI6MjExMDQ1OTk4Nn0.awWZwbgisQTJlJ_YqcrP_NRCTVDveBI36160KxQCal4",    // the "anon public" key from the same page
};
