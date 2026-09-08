function AgentActivity({ status }) {
  if (!status) return null;

  return (
    <div className="flex items-center gap-3 px-2 py-3 text-sm text-zinc-500">
      <div className="flex gap-1">
        <span className="h-2 w-2 animate-bounce rounded-full bg-emerald-500 [animation-delay:-0.3s]" />
        <span className="h-2 w-2 animate-bounce rounded-full bg-emerald-500 [animation-delay:-0.15s]" />
        <span className="h-2 w-2 animate-bounce rounded-full bg-emerald-500" />
      </div>

      <span>{status}</span>
    </div>
  );
}

export default AgentActivity;