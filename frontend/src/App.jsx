
import { useEffect, useRef, useState } from "react";
import { Menu, Moon, Sun } from "lucide-react";

import Sidebar from "./components/Sidebar";
import WelcomeScreen from "./components/WelcomeScreen";
import ChatInput from "./components/ChatInput";
import MessageBubble from "./components/MessageBubble";
import AgentActivity from "./components/AgentActivity";
import AuthScreen from "./components/AuthScreen";
import AccountPanel from "./components/AccountPanel";

import {
  AUTH_TOKEN_KEY,
  createConversation,
  deleteConversation,
  getConversation,
  getConversations,
  getMe,
  getProfile,
  getSettings,
  logout,
  saveConversationMessage,
  sendChatMessage,
  updateProfile,
  updateSettings,
} from "./services/api";

/* eslint-disable react-hooks/immutability */

const THEME_STORAGE_KEY = "fishai_theme";

function App() {
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const [authReady, setAuthReady] = useState(() => !localStorage.getItem(AUTH_TOKEN_KEY));
  const [user, setUser] = useState(null);
  const [profile, setProfile] = useState(null);
  const [settings, setSettings] = useState(null);
  const [accountPanel, setAccountPanel] = useState(null);
  const [workspaceError, setWorkspaceError] = useState("");

  // ==========================================
  // DARK MODE
  // ==========================================

  const [darkMode, setDarkMode] = useState(false);

  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const [agentStatus, setAgentStatus] = useState("");

  const [recentChats, setRecentChats] = useState([]);
  const [currentChatId, setCurrentChatId] =
    useState(null);

  const messagesEndRef = useRef(null);

  useEffect(() => {
    const token = localStorage.getItem(AUTH_TOKEN_KEY);
    if (!token) {
      return;
    }

    Promise.all([getMe(), getProfile(), getSettings(), getConversations()])
      .then(async ([meData, profileData, settingsData, conversationsData]) => {
        setUser(meData.user);
        setProfile(profileData.profile);
        setSettings(settingsData.settings);
        setDarkMode(Boolean(settingsData.settings.dark_mode));
        setRecentChats(conversationsData.conversations);
        const first = conversationsData.conversations[0];
        if (first) {
          const detail = await getConversation(first.id);
          setCurrentChatId(first.id);
          setMessages(detail.conversation.messages.map((item) => ({
            id: item.id,
            role: item.role,
            content: item.content,
            fishPrediction: item.metadata,
          })));
        }
      })
      .catch((error) => {
        localStorage.removeItem(AUTH_TOKEN_KEY);
        setWorkspaceError(error.message || "Could not load your workspace.");
      })
      .finally(() => setAuthReady(true));
  }, []);

  // ==========================================
  // APPLY THEME
  // ==========================================

  useEffect(() => {
    const root = document.documentElement;

    if (darkMode) {
      root.classList.add("dark");
      root.style.colorScheme = "dark";

      localStorage.setItem(THEME_STORAGE_KEY, "dark");
    } else {
      root.classList.remove("dark");
      root.style.colorScheme = "light";

      localStorage.setItem(
        THEME_STORAGE_KEY,
        "light"
      );
    }
  }, [darkMode]);

  const refreshConversations = async () => {
    const data = await getConversations();
    setRecentChats(data.conversations);
  };

  // ==========================================
  // HANDLE FISH PREDICTION
  // ==========================================

  const handleFishPrediction = async (predictionData) => {
    const chatId = currentChatId || (await createConversation("Fish image identification")).conversation.id;
    if (!currentChatId) {
      setCurrentChatId(chatId);
    }

    if (
      !predictionData?.success ||
      predictionData?.status === "NOT_FISH"
    ) {
      const rejectionContent =
        `**NOT_FISH**\n\n${
          predictionData?.message ||
          "The uploaded image does not appear to contain a fish. Please upload a clear image of a fish."
        }`;

      const rejectionMessage = {
        id: Date.now(),
        role: "assistant",
        content: rejectionContent,
        fishPrediction: predictionData,
      };

      await saveConversationMessage(chatId, "assistant", rejectionContent, predictionData);
      setMessages((previousMessages) => [...previousMessages, rejectionMessage]);
      await refreshConversations();
      return;
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

    await saveConversationMessage(chatId, "assistant", predictionContent, predictionData);
    setMessages((previousMessages) => [...previousMessages, fishMessage]);
    await refreshConversations();
  };

  // ==========================================
  // SEND MESSAGE
  // ==========================================

  const handleSend = async (message) => {
    const trimmedMessage = message.trim();

    if (!trimmedMessage) {
      return;
    }

    const chatId = currentChatId;

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
        conversation,
        chatId
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

      setCurrentChatId(data.conversation_id);

      const finalMessages = [
        ...updatedMessages,
        aiMessage,
      ];

      setMessages(finalMessages);

      await refreshConversations();
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

  const handleSelectChat = async (chatId) => {
    try {
      const data = await getConversation(chatId);
      setCurrentChatId(chatId);
      setMessages(data.conversation.messages.map((item) => ({
        id: item.id,
        role: item.role,
        content: item.content,
        fishPrediction: item.metadata,
      })));
      setInput("");
      setAgentStatus("");
    } catch (error) {
      setWorkspaceError(error.message || "Could not load that conversation.");
    }
  };

  // ==========================================
  // DELETE CHAT
  // ==========================================

  const handleDeleteChat = async (chatId) => {
    try {
      await deleteConversation(chatId);
      setRecentChats((previousChats) => previousChats.filter((chat) => chat.id !== chatId));
    } catch (error) {
      setWorkspaceError(error.message || "Could not delete that conversation.");
    }

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

  const toggleDarkMode = async () => {
    const nextMode = !darkMode;
    setDarkMode(nextMode);
    try {
      const data = await updateSettings(nextMode);
      setSettings(data.settings);
    } catch (error) {
      setWorkspaceError(error.message || "Could not save settings.");
    }
  };

  const handleAuthenticated = async (data) => {
    const [profileData, settingsData, conversationsData] = await Promise.all([
      getProfile(),
      getSettings(),
      getConversations(),
    ]);
    setUser(data.user);
    setProfile(profileData.profile);
    setSettings(settingsData.settings);
    setDarkMode(Boolean(settingsData.settings.dark_mode));
    setRecentChats(conversationsData.conversations);
  };

  const handleLogout = async () => {
    await logout();
    setUser(null);
    setProfile(null);
    setSettings(null);
    setRecentChats([]);
    setMessages([]);
    setCurrentChatId(null);
    setAccountPanel(null);
  };

  const handleProfileSaved = async (displayName) => {
    const data = await updateProfile(displayName);
    setProfile(data.profile);
    setUser(data.profile);
  };

  const handleSettingsSaved = async (nextDarkMode) => {
    const data = await updateSettings(nextDarkMode);
    setSettings(data.settings);
    setDarkMode(Boolean(data.settings.dark_mode));
  };

  const openSettings = async () => {
    try {
      const data = await getSettings();
      setSettings(data.settings);
      setDarkMode(Boolean(data.settings.dark_mode));
      setAccountPanel("settings");
    } catch (error) {
      setWorkspaceError(error.message || "Could not load settings.");
    }
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

  if (!authReady) {
    return <div className="flex min-h-screen items-center justify-center text-sm text-zinc-500">Loading FishAI...</div>;
  }

  if (!user) {
    return <AuthScreen onAuthenticated={handleAuthenticated} />;
  }

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
              onOpenProfile={() => setAccountPanel("profile")}
              onOpenSettings={openSettings}
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

            {workspaceError && (
              <p className="mx-auto max-w-4xl px-4 pt-4 text-sm text-red-600">{workspaceError}</p>
            )}

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
      {accountPanel && (
        <AccountPanel
          mode={accountPanel}
          profile={profile}
          settings={settings}
          onClose={() => setAccountPanel(null)}
          onProfileSaved={handleProfileSaved}
          onSettingsSaved={handleSettingsSaved}
          onLogout={handleLogout}
        />
      )}
    </div>
  );
}

export default App;
