import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import {
  Copy,
  RefreshCw,
  User,
  Bot,
} from "lucide-react";

function MessageBubble({ message, onRegenerate }) {
  const isUser = message.role === "user";

  const handleCopy = async () => {
    try {
      await navigator.clipboard.writeText(
        message.content
      );
    } catch (error) {
      console.error(
        "Failed to copy message:",
        error
      );
    }
  };

  return (
    <div
      className={`group flex w-full gap-3 ${
        isUser ? "justify-end" : "justify-start"
      }`}
    >
      {/* ASSISTANT AVATAR */}
      {!isUser && (
        <div className="mt-1 flex h-8 w-8 shrink-0 items-center justify-center rounded-lg bg-emerald-600 text-white shadow-sm">
          <Bot size={17} />
        </div>
      )}

      {/* MESSAGE CONTENT */}
      <div
        className={`min-w-0 max-w-[85%] ${
          isUser
            ? "rounded-2xl rounded-tr-md bg-emerald-600 px-4 py-3 text-white shadow-sm"
            : "text-zinc-800 dark:text-zinc-200"
        }`}
      >
        {isUser ? (
          <div className="whitespace-pre-wrap text-sm leading-7">
            {message.content}
          </div>
        ) : (
          <div className="fishai-markdown text-sm leading-7">
            <ReactMarkdown
              remarkPlugins={[remarkGfm]}
              components={{
                /* =========================
                   PARAGRAPH
                ========================= */
                p: ({ children }) => (
                  <p className="mb-4 last:mb-0">
                    {children}
                  </p>
                ),

                /* =========================
                   HEADINGS
                ========================= */
                h1: ({ children }) => (
                  <h1 className="mb-4 mt-6 text-2xl font-bold text-zinc-900 first:mt-0 dark:text-white">
                    {children}
                  </h1>
                ),

                h2: ({ children }) => (
                  <h2 className="mb-3 mt-6 text-xl font-bold text-zinc-900 first:mt-0 dark:text-white">
                    {children}
                  </h2>
                ),

                h3: ({ children }) => (
                  <h3 className="mb-3 mt-5 text-lg font-semibold text-zinc-900 first:mt-0 dark:text-white">
                    {children}
                  </h3>
                ),

                h4: ({ children }) => (
                  <h4 className="mb-2 mt-4 font-semibold text-zinc-900 dark:text-white">
                    {children}
                  </h4>
                ),

                /* =========================
                   BOLD
                ========================= */
                strong: ({ children }) => (
                  <strong className="font-semibold text-zinc-950 dark:text-white">
                    {children}
                  </strong>
                ),

                /* =========================
                   ITALIC
                ========================= */
                em: ({ children }) => (
                  <em className="italic">
                    {children}
                  </em>
                ),

                /* =========================
                   UNORDERED LIST
                ========================= */
                ul: ({ children }) => (
                  <ul className="mb-4 ml-6 list-disc space-y-1">
                    {children}
                  </ul>
                ),

                /* =========================
                   ORDERED LIST
                ========================= */
                ol: ({ children }) => (
                  <ol className="mb-4 ml-6 list-decimal space-y-1">
                    {children}
                  </ol>
                ),

                /* =========================
                   LIST ITEM
                ========================= */
                li: ({ children }) => (
                  <li className="pl-1">
                    {children}
                  </li>
                ),

                /* =========================
                   BLOCKQUOTE
                ========================= */
                blockquote: ({ children }) => (
                  <blockquote className="my-4 border-l-4 border-emerald-500 pl-4 italic text-zinc-600 dark:text-zinc-400">
                    {children}
                  </blockquote>
                ),

                /* =========================
                   HORIZONTAL LINE
                ========================= */
                hr: () => (
                  <hr className="my-6 border-zinc-200 dark:border-zinc-700" />
                ),

                /* =========================
                   LINKS
                ========================= */
                a: ({ href, children }) => (
                  <a
                    href={href}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="font-medium text-emerald-600 underline underline-offset-2 hover:text-emerald-700 dark:text-emerald-400 dark:hover:text-emerald-300"
                  >
                    {children}
                  </a>
                ),

                /* =========================
                   INLINE CODE
                ========================= */
                code: ({
                  inline,
                  className,
                  children,
                  ...props
                }) => {
                  if (inline) {
                    return (
                      <code
                        className="rounded-md bg-zinc-100 px-1.5 py-0.5 font-mono text-[13px] text-pink-600 dark:bg-zinc-800 dark:text-pink-400"
                        {...props}
                      >
                        {children}
                      </code>
                    );
                  }

                  return (
                    <code
                      className={`${className || ""} block font-mono text-[13px] leading-6`}
                      {...props}
                    >
                      {children}
                    </code>
                  );
                },

                /* =========================
                   CODE BLOCK
                ========================= */
                pre: ({ children }) => (
                  <pre className="my-4 overflow-x-auto rounded-xl bg-zinc-950 p-4 text-zinc-100 shadow-sm">
                    {children}
                  </pre>
                ),

                /* =========================
                   TABLE
                ========================= */
                table: ({ children }) => (
                  <div className="my-5 w-full overflow-x-auto rounded-xl border border-zinc-200 dark:border-zinc-700">
                    <table className="w-full min-w-[500px] border-collapse text-left text-sm">
                      {children}
                    </table>
                  </div>
                ),

                /* =========================
                   TABLE HEADER
                ========================= */
                thead: ({ children }) => (
                  <thead className="bg-zinc-100 dark:bg-zinc-800">
                    {children}
                  </thead>
                ),

                /* =========================
                   TABLE BODY
                ========================= */
                tbody: ({ children }) => (
                  <tbody className="divide-y divide-zinc-200 dark:divide-zinc-700">
                    {children}
                  </tbody>
                ),

                /* =========================
                   TABLE ROW
                ========================= */
                tr: ({ children }) => (
                  <tr className="transition hover:bg-zinc-50 dark:hover:bg-zinc-800/60">
                    {children}
                  </tr>
                ),

                /* =========================
                   TABLE HEADER CELL
                ========================= */
                th: ({ children }) => (
                  <th className="border-b border-zinc-200 px-4 py-3 font-semibold text-zinc-900 dark:border-zinc-700 dark:text-white">
                    {children}
                  </th>
                ),

                /* =========================
                   TABLE DATA CELL
                ========================= */
                td: ({ children }) => (
                  <td className="px-4 py-3 align-top text-zinc-700 dark:text-zinc-300">
                    {children}
                  </td>
                ),

                /* =========================
                   LINE BREAK
                ========================= */
                br: () => <br />,
              }}
            >
              {message.content}
            </ReactMarkdown>
          </div>
        )}

        {/* MESSAGE ACTIONS */}
        {!isUser && (
          <div className="mt-3 flex items-center gap-1 opacity-0 transition-opacity group-hover:opacity-100">
            <button
              type="button"
              onClick={handleCopy}
              className="rounded-lg p-2 text-zinc-400 transition hover:bg-zinc-100 hover:text-zinc-700 dark:hover:bg-zinc-800 dark:hover:text-zinc-200"
              title="Copy"
              aria-label="Copy message"
            >
              <Copy size={15} />
            </button>

            <button
              type="button"
              onClick={() =>
                onRegenerate?.(message.id)
              }
              className="rounded-lg p-2 text-zinc-400 transition hover:bg-zinc-100 hover:text-zinc-700 dark:hover:bg-zinc-800 dark:hover:text-zinc-200"
              title="Regenerate"
              aria-label="Regenerate response"
            >
              <RefreshCw size={15} />
            </button>
          </div>
        )}
      </div>

      {/* USER AVATAR */}
      {isUser && (
        <div className="mt-1 flex h-8 w-8 shrink-0 items-center justify-center rounded-lg bg-zinc-200 text-zinc-600 dark:bg-zinc-700 dark:text-zinc-200">
          <User size={17} />
        </div>
      )}
    </div>
  );
}

export default MessageBubble;

