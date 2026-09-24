import { useState } from "react";
import { authenticate } from "../services/api";

function AuthScreen({ onAuthenticated }) {
  const [mode, setMode] = useState("login");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [displayName, setDisplayName] = useState("");
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);

  const submit = async (event) => {
    event.preventDefault();
    setBusy(true);
    setError("");
    try {
      const data = await authenticate(mode, { email, password, display_name: displayName });
      onAuthenticated(data);
    } catch (requestError) {
      setError(requestError.message);
    } finally {
      setBusy(false);
    }
  };

  return (
    <main className="flex min-h-screen items-center justify-center bg-zinc-50 px-4 dark:bg-zinc-950">
      <form onSubmit={submit} className="w-full max-w-md rounded-2xl border border-zinc-200 bg-white p-6 shadow-sm dark:border-zinc-800 dark:bg-zinc-900">
        <div className="mb-6 flex items-center gap-3">
          <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-emerald-600 text-lg">🐟</div>
          <div>
            <h1 className="font-semibold text-zinc-900 dark:text-white">FishAI</h1>
            <p className="text-sm text-zinc-500">{mode === "login" ? "Sign in to your workspace" : "Create your workspace"}</p>
          </div>
        </div>
        {mode === "register" && (
          <label className="mb-4 block text-sm text-zinc-600 dark:text-zinc-300">
            Display name
            <input value={displayName} onChange={(event) => setDisplayName(event.target.value)} className="mt-1 w-full rounded-lg border border-zinc-300 px-3 py-2 dark:border-zinc-700 dark:bg-zinc-950" />
          </label>
        )}
        <label className="mb-4 block text-sm text-zinc-600 dark:text-zinc-300">
          Email
          <input required type="email" value={email} onChange={(event) => setEmail(event.target.value)} className="mt-1 w-full rounded-lg border border-zinc-300 px-3 py-2 dark:border-zinc-700 dark:bg-zinc-950" />
        </label>
        <label className="mb-4 block text-sm text-zinc-600 dark:text-zinc-300">
          Password
          <input required minLength={8} type="password" value={password} onChange={(event) => setPassword(event.target.value)} className="mt-1 w-full rounded-lg border border-zinc-300 px-3 py-2 dark:border-zinc-700 dark:bg-zinc-950" />
        </label>
        {error && <p className="mb-4 text-sm text-red-600">{error}</p>}
        <button disabled={busy} className="w-full rounded-lg bg-emerald-600 px-4 py-2.5 text-sm font-medium text-white disabled:opacity-60">
          {busy ? "Please wait..." : mode === "login" ? "Sign in" : "Create account"}
        </button>
        <button type="button" onClick={() => { setMode(mode === "login" ? "register" : "login"); setError(""); }} className="mt-4 w-full text-sm text-emerald-700 dark:text-emerald-400">
          {mode === "login" ? "Create an account" : "Use an existing account"}
        </button>
      </form>
    </main>
  );
}

export default AuthScreen;
