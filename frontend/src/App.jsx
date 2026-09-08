
import { useEffect, useRef, useState } from "react";
import { Menu, Moon, Sun } from "lucide-react";

import Sidebar from "./components/Sidebar";
import WelcomeScreen from "./components/WelcomeScreen";
import ChatInput from "./components/ChatInput";
import MessageBubble from "./components/MessageBubble";
import AgentActivity from "./components/AgentActivity";

import { sendChatMessage } from "./services/api";

const CHAT_STORAGE_KEY = "fishai_recent_chats";
const THEME_STORAGE_KEY = "fishai_theme";

function App() {
  const [sidebarOpen, setSidebarOpen] = useState(true);

  // ==========================================
  // DARK MODE
  // ==========================================

  const [darkMode, setDarkMode] = useState(() => {
    try {
      const savedTheme =
        localStorage.getItem(THEME_STORAGE_KEY);

      if (savedTheme === "dark") {
        return true;
      }

      if (savedTheme === "light") {
        return false;
      }

      return false;
    } catch (error) {
      return false;
    }
  });

  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const [agentStatus, setAgentStatus] = useState("");

  const [recentChats, setRecentChats] = useState([]);
  const [currentChatId, setCurrentChatId] =
    useState(null);

  const messagesEndRef = useRef(null);

  // ==========================================
  // APPLY THEME
  // ==========================================

  useEffect(() => {
    const root = document.documentElement;

    if (darkMode) {
      root.classList.add("dark");
      root.style.colorScheme = "dark";

      localStorage.setItem(
        THEME_STORAGE_KEY,
        "dark"
      );
    } else {
      root.classList.remove("dark");
      root.style.colorScheme = "light";

      localStorage.setItem(
        THEME_STORAGE_KEY,
        "light"
      );
    }
  }, [darkMode]);

  // ==========================================
  // LOAD RECENT CHATS
  // ==========================================

  useEffect(() => {
    try {
      const savedChats =
        localStorage.getItem(CHAT_STORAGE_KEY);

      if (savedChats) {
        const parsedChats = JSON.parse(savedChats);

        if (Array.isArray(parsedChats)) {
          setRecentChats(parsedChats);
        }
      }
    } catch (error) {
      console.error(
        "Failed to load recent chats:",
        error
      );
    }
  }, []);

  // ==========================================
  // SAVE RECENT CHATS
  // ==========================================

  useEffect(() => {
    try {
      localStorage.setItem(
        CHAT_STORAGE_KEY,
        JSON.stringify(recentChats)
      );
    } catch (error) {
      console.error(
        "Failed to save recent chats:",
        error
      );
    }
  }, [recentChats]);

  // ==========================================
  // AUTO SCROLL
  // ==========================================

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({
      behavior: "smooth",
    });
  }, [messages, agentStatus]);

  // ==========================================
  // CREATE CHAT TITLE
  // ==========================================

  const createChatTitle = (message) => {
    const cleanMessage = message.trim();

    if (cleanMessage.length <= 45) {
      return cleanMessage;
    }

    return `${cleanMessage.substring(0, 45)}...`;
  };

  // ==========================================
  // SAVE / UPDATE CHAT
  // ==========================================

  const saveChat = (chatId, chatMessages) => {
    if (!chatId || chatMessages.length === 0) {
      return;
    }

    const firstUserMessage = chatMessages.find(
      (message) => message.role === "user"
    );

    const title = firstUserMessage
      ? createChatTitle(firstUserMessage.content)
      : "New chat";

    const now = Date.now();

    setRecentChats((previousChats) => {
      const existingChat = previousChats.find(
        (chat) => chat.id === chatId
      );

      const updatedChat = {
        id: chatId,
        title: existingChat?.title || title,
        messages: chatMessages,
        createdAt:
          existingChat?.createdAt || now,
        updatedAt: now,
      };

      const otherChats = previousChats.filter(
        (chat) => chat.id !== chatId
      );

      return [updatedChat, ...otherChats];
    });
  };

  // ==========================================
  // HANDLE FISH PREDICTION
  // ==========================================

  const handleFishPrediction = (predictionData) => {
    let chatId = currentChatId;

    if (!chatId) {
      chatId = `chat_${Date.now()}`;
      setCurrentChatId(chatId);
    }

    const species =
      predictionData?.predicted_species ||
      "Unknown species";

    const confidence =
      predictionData?.confidence ?? 0;

    const confidenceLevel =
      predictionData?.confidence_level ||
      "UNKNOWN";

    const topPredictions =
      predictionData?.top_predictions || [];

    // ------------------------------------------
    // CREATE READABLE CHAT MESSAGE
    // ------------------------------------------

    let predictionContent =
      `## 🐟 Fish Identification Result\n\n` +
      `**Predicted species:** ${species}\n\n` +
      `**Confidence:** ${Number(confidence).toFixed(2)}%\n\n` +
      `**Confidence level:** ${confidenceLevel}\n`;

    // ------------------------------------------
    // ADD TOP PREDICTIONS
    // ------------------------------------------

    if (topPredictions.length > 0) {
      predictionContent +=
        `\n### Top Predictions\n\n`;

      topPredictions.forEach(
        (prediction, index) => {
          predictionContent +=
            `${index + 1}. **${prediction.species}** — ${Number(
              prediction.confidence
            ).toFixed(2)}%\n`;
        }
      );
    }

    // ------------------------------------------
    // ADD STATUS
    // ------------------------------------------

    if (predictionData?.status) {
      predictionContent +=
        `\n**Status:** ${predictionData.status}`;
    }

    // ------------------------------------------
    // STRUCTURED MESSAGE
    // ------------------------------------------

    const fishMessage = {
      id: Date.now(),
      role: "assistant",

      // This will be used later by MessageBubble
      // for the beautiful Fish Identification Card.
      type: "fish_prediction",

      content: predictionContent,

      // Keep original prediction data.
      // This allows us to build a dedicated card
      // in STEP 8.5.4 without changing the API.
      fishPrediction: predictionData,
    };

    const updatedMessages = [
      ...messages,
      fishMessage,
    ];

    setMessages(updatedMessages);

    // Save prediction inside Recent Chats
    saveChat(chatId, updatedMessages);
  };

  // ==========================================
  // SEND MESSAGE
  // ==========================================

  const handleSend = async (message) => {
    const trimmedMessage = message.trim();

    if (!trimmedMessage) {
      return;
    }

    let chatId = currentChatId;

    if (!chatId) {
      chatId = `chat_${Date.now()}`;
      setCurrentChatId(chatId);
    }

    const conversation = messages.map(
      (message) => ({
        role: message.role,
        content: message.content,
      })
    );

    const userMessage = {
      id: Date.now(),
      role: "user",
      content: trimmedMessage,
    };

    const updatedMessages = [
      ...messages,
      userMessage,
    ];

    setMessages(updatedMessages);
    setInput("");

    try {
      setAgentStatus(
        "FishAI is processing your question..."
      );

      const data = await sendChatMessage(
        trimmedMessage,
        conversation
      );

      if (!data.success) {
        throw new Error(
          data.response ||
            "Backend request failed."
        );
      }

      const aiMessage = {
        id: Date.now() + 1,
        role: "assistant",
        content: data.response,
      };

      const finalMessages = [
        ...updatedMessages,
        aiMessage,
      ];

      setMessages(finalMessages);

      saveChat(chatId, finalMessages);
    } catch (error) {
      console.error(
        "FishAI Chat Error:",
        error
      );

      const errorMessage = {
        id: Date.now() + 1,
        role: "assistant",
        content:
          "⚠️ Sorry, I could not connect to the FishAI backend.\n\nPlease make sure the FastAPI server is running on port 8000.",
      };

      const finalMessages = [
        ...updatedMessages,
        errorMessage,
      ];

      setMessages(finalMessages);

      saveChat(chatId, finalMessages);
    } finally {
      setAgentStatus("");
    }
  };

  // ==========================================
  // NEW CHAT
  // ==========================================

  const handleNewChat = () => {
    setMessages([]);
    setInput("");
    setAgentStatus("");
    setCurrentChatId(null);
  };

  // ==========================================
  // SELECT CHAT
  // ==========================================

  const handleSelectChat = (chatId) => {
    const selectedChat = recentChats.find(
      (chat) => chat.id === chatId
    );

    if (!selectedChat) {
      return;
    }

    setCurrentChatId(chatId);
    setMessages(selectedChat.messages || []);
    setInput("");
    setAgentStatus("");
  };

  // ==========================================
  // DELETE CHAT
  // ==========================================

  const handleDeleteChat = (chatId) => {
    setRecentChats((previousChats) =>
      previousChats.filter(
        (chat) => chat.id !== chatId
      )
    );

    if (currentChatId === chatId) {
      setCurrentChatId(null);
      setMessages([]);
      setInput("");
      setAgentStatus("");
    }
  };

  // ==========================================
  // REGENERATE
  // ==========================================

  const handleRegenerate = async (messageId) => {
    console.log(
      "Regenerate message:",
      messageId
    );

    setAgentStatus(
      "Regenerating response..."
    );

    await new Promise((resolve) =>
      setTimeout(resolve, 1000)
    );

    setAgentStatus("");
  };

  // ==========================================
  // SUGGESTION
  // ==========================================

  const handleSuggestion = (prompt) => {
    setInput(prompt);
  };

  // ==========================================
  // TOGGLE DARK MODE
  // ==========================================

  const toggleDarkMode = () => {
    setDarkMode(
      (previousMode) => !previousMode
    );
  };

  // ==========================================
  // SIDEBAR
  // ==========================================

  const openSidebar = () => {
    setSidebarOpen(true);
  };

  const closeSidebar = () => {
    setSidebarOpen(false);
  };

  // ==========================================
  // UI
  // ==========================================

  return (
    <div className="h-full">
      <div className="flex h-screen overflow-hidden bg-white text-zinc-900 transition-colors duration-200 dark:bg-zinc-950 dark:text-white">

        {/* SIDEBAR */}
        {sidebarOpen && (
          <div className="hidden md:block">
            <Sidebar
              onClose={closeSidebar}
              onNewChat={handleNewChat}
              recentChats={recentChats}
              currentChatId={currentChatId}
              onSelectChat={handleSelectChat}
              onDeleteChat={handleDeleteChat}
            />
          </div>
        )}

        {/* MAIN */}
        <main className="relative flex min-w-0 flex-1 flex-col">

          {/* HEADER */}
          <header className="flex h-14 shrink-0 items-center justify-between border-b border-zinc-200 bg-white px-4 transition-colors duration-200 dark:border-zinc-800 dark:bg-zinc-950">

            <button
              type="button"
              onClick={openSidebar}
              className="rounded-lg p-2 text-zinc-500 transition hover:bg-zinc-100 hover:text-zinc-900 dark:hover:bg-zinc-800 dark:hover:text-white"
              title="Open sidebar"
              aria-label="Open sidebar"
            >
              <Menu size={20} />
            </button>

            {/* LOGO */}
            <div className="flex items-center gap-2 font-semibold">
              <span className="text-xl">
                🐟
              </span>

              <span>FishAI</span>
            </div>

            {/* DARK MODE BUTTON */}
            <button
              type="button"
              onClick={toggleDarkMode}
              className="rounded-lg p-2 text-zinc-500 transition hover:bg-zinc-100 hover:text-zinc-900 dark:hover:bg-zinc-800 dark:hover:text-white"
              title={
                darkMode
                  ? "Switch to light mode"
                  : "Switch to dark mode"
              }
              aria-label={
                darkMode
                  ? "Switch to light mode"
                  : "Switch to dark mode"
              }
            >
              {darkMode ? (
                <Sun size={19} />
              ) : (
                <Moon size={19} />
              )}
            </button>
          </header>

          {/* CHAT AREA */}
          <section className="flex-1 overflow-y-auto bg-white transition-colors duration-200 dark:bg-zinc-950">

            {messages.length === 0 ? (
              <WelcomeScreen
                onSuggestion={handleSuggestion}
              />
            ) : (
              <div className="mx-auto flex w-full max-w-4xl flex-col gap-6 px-4 py-8">

                {messages.map((message) => (
                  <MessageBubble
                    key={message.id}
                    message={message}
                    onRegenerate={
                      handleRegenerate
                    }
                  />
                ))}

                <AgentActivity
                  status={agentStatus}
                />

                <div ref={messagesEndRef} />
              </div>
            )}

          </section>

          {/* PROCESSING STATUS */}
          {messages.length === 0 && (
            <AgentActivity
              status={agentStatus}
            />
          )}

          {/* CHAT INPUT */}
          <div className="border-t border-zinc-200 bg-white transition-colors duration-200 dark:border-zinc-800 dark:bg-zinc-950">

            <ChatInput
              value={input}
              setValue={setInput}
              onSend={handleSend}
              onFishPrediction={
                handleFishPrediction
              }
            />

          </div>

        </main>
      </div>
    </div>
  );
}

export default App;
