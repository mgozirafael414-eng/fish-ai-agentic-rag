import {
  Plus,
  Search,
  MessageSquare,
  BookOpen,
  Settings,
  User,
  PanelLeftClose,
  Trash2,
} from "lucide-react";


function Sidebar({
  onClose,
  onNewChat,
  recentChats = [],
  currentChatId,
  onSelectChat,
  onDeleteChat,
  onOpenProfile,
  onOpenSettings,
}) {

  // ==========================================================
  // FORMAT CHAT DATE
  // ==========================================================

  const formatDate = (timestamp) => {

    if (!timestamp) {
      return "";
    }

    const date =
      new Date(timestamp);

    const today =
      new Date();

    const isToday =
      date.toDateString() ===
      today.toDateString();

    if (isToday) {

      return date.toLocaleTimeString(
        [],
        {
          hour: "2-digit",
          minute: "2-digit",
        }
      );

    }

    return date.toLocaleDateString(
      [],
      {
        month: "short",
        day: "numeric",
      }
    );

  };


  return (

    <aside className="flex h-full w-72 flex-col border-r border-zinc-200 bg-zinc-50 dark:border-zinc-800 dark:bg-zinc-950">


      {/* ======================================================
          HEADER
      ====================================================== */}

      <div className="flex items-center justify-between p-4">

        <div className="flex items-center gap-3">


          {/* Logo */}

          <div className="flex h-9 w-9 items-center justify-center rounded-xl bg-emerald-600 text-lg shadow-sm">

            🐟

          </div>


          {/* Brand */}

          <div>

            <h1 className="font-semibold text-zinc-900 dark:text-white">

              FishAI

            </h1>

            <p className="text-xs text-zinc-500 dark:text-zinc-400">

              Intelligent Assistant

            </p>

          </div>

        </div>


        {/* Close */}

        <button
          type="button"
          onClick={
            onClose
          }
          className="rounded-lg p-2 text-zinc-500 transition hover:bg-zinc-200 hover:text-zinc-900 dark:hover:bg-zinc-800 dark:hover:text-white"
          title="Close sidebar"
          aria-label="Close sidebar"
        >

          <PanelLeftClose
            size={19}
          />

        </button>

      </div>


      {/* ======================================================
          NEW CHAT
      ====================================================== */}

      <div className="px-3">

        <button
          type="button"
          onClick={
            onNewChat
          }
          className="flex w-full items-center gap-3 rounded-xl border border-zinc-200 bg-white px-4 py-3 text-sm font-medium text-zinc-800 shadow-sm transition hover:bg-zinc-100 hover:shadow dark:border-zinc-800 dark:bg-zinc-900 dark:text-zinc-100 dark:hover:bg-zinc-800"
        >

          <Plus
            size={18}
          />

          <span>
            New chat
          </span>

        </button>

      </div>


      {/* ======================================================
          SEARCH
      ====================================================== */}

      <div className="px-3 pt-3">

        <button
          type="button"
          className="flex w-full items-center gap-3 rounded-xl px-4 py-3 text-sm text-zinc-600 transition hover:bg-zinc-200 hover:text-zinc-900 dark:text-zinc-400 dark:hover:bg-zinc-800 dark:hover:text-white"
        >

          <Search
            size={18}
          />

          <span>
            Search chats
          </span>

        </button>

      </div>


      {/* ======================================================
          WORKSPACE
      ====================================================== */}

      <div className="mt-6 px-3">

        <p className="px-3 pb-2 text-xs font-semibold uppercase tracking-wider text-zinc-400">

          Workspace

        </p>


        <button
          type="button"
          onClick={onOpenSettings}
          className="flex w-full items-center gap-3 rounded-xl px-3 py-3 text-sm text-zinc-700 transition hover:bg-zinc-200 hover:text-zinc-900 dark:text-zinc-300 dark:hover:bg-zinc-800 dark:hover:text-white"
        >

          <BookOpen
            size={18}
          />

          <span>
            Knowledge Base
          </span>

        </button>

      </div>


      {/* ======================================================
          RECENT CHATS
      ====================================================== */}

      <div className="mt-6 flex-1 overflow-y-auto px-3">


        <div className="mb-2 flex items-center justify-between px-3">

          <p className="text-xs font-semibold uppercase tracking-wider text-zinc-400">

            Recent chats

          </p>

          {recentChats.length > 0 && (

            <span className="text-xs text-zinc-400">

              {recentChats.length}

            </span>

          )}

        </div>


        {/* ==================================================
            EMPTY STATE
        ================================================== */}

        {recentChats.length === 0 && (

          <div className="px-3 py-6 text-center">

            <MessageSquare
              size={25}
              className="mx-auto mb-2 text-zinc-300 dark:text-zinc-700"
            />

            <p className="text-xs text-zinc-400">

              No recent chats

            </p>

            <p className="mt-1 text-[11px] text-zinc-400">

              Start a conversation to see it here.

            </p>

          </div>

        )}


        {/* ==================================================
            CHAT LIST
        ================================================== */}

        {recentChats.map(
          (chat) => (

            <div
              key={
                chat.id
              }
              className={`group mb-1 flex items-center rounded-xl transition ${
                currentChatId ===
                chat.id
                  ? "bg-zinc-200 dark:bg-zinc-800"
                  : "hover:bg-zinc-200 dark:hover:bg-zinc-800"
              }`}
            >


              {/* Chat */}

              <button
                type="button"
                onClick={() =>
                  onSelectChat(
                    chat.id
                  )
                }
                className="flex min-w-0 flex-1 items-center gap-3 px-3 py-3 text-left text-sm text-zinc-700 dark:text-zinc-300"
              >

                <MessageSquare
                  size={17}
                  className="shrink-0 text-zinc-400"
                />


                <div className="min-w-0 flex-1">

                  <p className="truncate font-medium">

                    {chat.title ||
                      "New chat"}

                  </p>


                  <p className="mt-0.5 text-[10px] text-zinc-400">

                    {formatDate(
                      chat.updatedAt
                    )}

                  </p>

                </div>

              </button>


              {/* Delete */}

              <button
                type="button"
                onClick={() =>
                  onDeleteChat(
                    chat.id
                  )
                }
                className="mr-1 hidden rounded-lg p-2 text-zinc-400 transition hover:bg-red-100 hover:text-red-600 group-hover:block dark:hover:bg-red-950/40"
                title="Delete chat"
                aria-label="Delete chat"
              >

                <Trash2
                  size={15}
                />

              </button>

            </div>

          )
        )}

      </div>


      {/* ======================================================
          BOTTOM MENU
      ====================================================== */}

      <div className="border-t border-zinc-200 p-3 dark:border-zinc-800">


        {/* Settings */}

        <button
          type="button"
          className="flex w-full items-center gap-3 rounded-xl px-3 py-3 text-sm text-zinc-700 transition hover:bg-zinc-200 hover:text-zinc-900 dark:text-zinc-300 dark:hover:bg-zinc-800 dark:hover:text-white"
        >

          <Settings
            size={18}
          />

          <span>
            Settings
          </span>

        </button>


        {/* Profile */}

        <button
          type="button"
          onClick={onOpenProfile}
          className="mt-1 flex w-full items-center gap-3 rounded-xl px-3 py-3 text-sm text-zinc-700 transition hover:bg-zinc-200 hover:text-zinc-900 dark:text-zinc-300 dark:hover:bg-zinc-800 dark:hover:text-white"
        >

          <User
            size={18}
          />

          <span>
            Profile
          </span>

        </button>

      </div>

    </aside>

  );

}


export default Sidebar;

