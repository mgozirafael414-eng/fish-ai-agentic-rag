import {
  Fish,
  FileText,
  Waves,
  Sparkles,
} from "lucide-react";

function WelcomeScreen({ onSuggestion }) {
  const suggestions = [
    {
      icon: Fish,
      title: "Identify a fish species",
      description: "Upload a fish image and identify the possible species.",
      prompt: "Identify this fish species",
    },
    {
      icon: FileText,
      title: "Ask about documents",
      description: "Ask questions about your uploaded fisheries documents.",
      prompt: "What information is available in my fisheries documents?",
    },
    {
      icon: Waves,
      title: "Learn about fisheries",
      description: "Explore fish biology, habitats and fisheries.",
      prompt: "Explain fish habitats and ecosystems",
    },
    {
      icon: Sparkles,
      title: "Ask anything",
      description: "Ask general questions beyond fisheries.",
      prompt: "What is artificial intelligence?",
    },
  ];

  return (
    <div className="mx-auto flex w-full max-w-4xl flex-col items-center px-6 py-12">
      
      <div className="mb-5 flex h-16 w-16 items-center justify-center rounded-2xl bg-emerald-100 text-3xl dark:bg-emerald-950">
        🐟
      </div>

      <h2 className="text-center text-3xl font-semibold tracking-tight text-zinc-900 dark:text-white">
        How can I help you today?
      </h2>

      <p className="mt-3 max-w-xl text-center text-zinc-500">
        Ask about fish species, fisheries, documents, or anything else.
      </p>

      <div className="mt-10 grid w-full grid-cols-1 gap-4 sm:grid-cols-2">
        {suggestions.map((item) => {
          const Icon = item.icon;

          return (
            <button
              key={item.title}
              onClick={() => onSuggestion(item.prompt)}
              className="group rounded-2xl border border-zinc-200 bg-white p-5 text-left transition hover:-translate-y-0.5 hover:border-emerald-400 hover:shadow-md dark:border-zinc-800 dark:bg-zinc-900 dark:hover:border-emerald-700"
            >
              <div className="mb-4 flex h-10 w-10 items-center justify-center rounded-xl bg-zinc-100 dark:bg-zinc-800">
                <Icon
                  size={20}
                  className="text-emerald-600"
                />
              </div>

              <h3 className="font-medium text-zinc-900 dark:text-white">
                {item.title}
              </h3>

              <p className="mt-2 text-sm leading-6 text-zinc-500">
                {item.description}
              </p>
            </button>
          );
        })}
      </div>
    </div>
  );
}

export default WelcomeScreen;