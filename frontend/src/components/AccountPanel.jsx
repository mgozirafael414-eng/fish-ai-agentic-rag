import { useState } from "react";

function AccountPanel({ mode, profile, settings, onClose, onProfileSaved, onSettingsSaved, onLogout }) {
  const [displayName, setDisplayName] = useState(() => profile?.display_name || "");
  const [darkMode, setDarkMode] = useState(() => Boolean(settings?.dark_mode));
  const [status, setStatus] = useState("");
  const [busy, setBusy] = useState(false);

  const handleDarkModeChange = async (event) => {
    const nextValue = event.target.checked;
    const previousValue = darkMode;
    setDarkMode(nextValue);
    setBusy(true);
    setStatus("");
    try {
      await onSettingsSaved(nextValue);
      setStatus("Settings saved.");
    } catch (error) {
      setDarkMode(previousValue);
      setStatus(error.message || "Could not save settings.");
    } finally {
      setBusy(false);
    }
  };

  const save = async (event) => {
    event.preventDefault();
    setBusy(true);
    setStatus("");
    try {
      if (mode === "profile") {
        await onProfileSaved(displayName);
        setStatus("Profile saved.");
      } else {
        await onSettingsSaved(darkMode);
        setStatus("Settings saved.");
      }
    } catch (error) {
      setStatus(error.message || "Could not save changes.");
    } finally {
      setBusy(false);
    }
  };

  return (
    <div className="absolute inset-0 z-20 flex items-center justify-center bg-black/20 px-4">
      <form onSubmit={save} className="w-full max-w-md rounded-2xl border border-zinc-200 bg-white p-6 shadow-xl dark:border-zinc-800 dark:bg-zinc-900">
        <div className="mb-5 flex items-center justify-between">
          <h2 className="text-lg font-semibold text-zinc-900 dark:text-white">{mode === "profile" ? "Profile" : "Settings"}</h2>
          <button type="button" onClick={onClose} className="text-sm text-zinc-500">Close</button>
        </div>
        {mode === "profile" ? (
          <>
            <p className="mb-4 text-sm text-zinc-500">{profile?.email}</p>
            <label className="block text-sm text-zinc-600 dark:text-zinc-300">
              Display name
              <input value={displayName} onChange={(event) => setDisplayName(event.target.value)} className="mt-1 w-full rounded-lg border border-zinc-300 px-3 py-2 dark:border-zinc-700 dark:bg-zinc-950" />
            </label>
          </>
        ) : (
          <label className="flex items-center gap-3 text-sm text-zinc-700 dark:text-zinc-300">
            <input type="checkbox" checked={darkMode} disabled={busy} onChange={handleDarkModeChange} />
            Use dark mode
          </label>
        )}
        {status && <p className="mt-4 text-sm text-emerald-600">{status}</p>}
        <div className="mt-6 flex justify-between gap-3">
          <button type="button" onClick={onLogout} className="text-sm text-red-600">Log out</button>
          <button disabled={busy} className="rounded-lg bg-emerald-600 px-4 py-2 text-sm font-medium text-white disabled:opacity-60">{busy ? "Saving..." : "Save"}</button>
        </div>
      </form>
    </div>
  );
}

export default AccountPanel;
