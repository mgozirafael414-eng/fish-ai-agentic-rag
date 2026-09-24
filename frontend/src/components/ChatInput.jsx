
import { useRef, useState } from "react";
import {
  Paperclip,
  Mic,
  Send,
  Square,
} from "lucide-react";

import { uploadDocument } from "../services/api";
import { predictFishImage } from "../services/fishApi";

function ChatInput({
  value,
  setValue,
  onSend,
  onFishPrediction,
}) {
  const fileInputRef = useRef(null);

  const [isListening, setIsListening] =
    useState(false);

  const [uploadStatus, setUploadStatus] =
    useState("");

  // ==========================================
  // FILE UPLOAD
  // ==========================================

  const handleFileChange = async (event) => {
    const selectedFile =
      event.target.files?.[0];

    if (!selectedFile) {
      return;
    }

    const fileName =
      selectedFile.name.toLowerCase();

    const isFishImage =
      fileName.endsWith(".jpg") ||
      fileName.endsWith(".jpeg") ||
      fileName.endsWith(".png") ||
      fileName.endsWith(".webp") ||
      fileName.endsWith(".bmp");

    const isDocument =
      fileName.endsWith(".pdf") ||
      fileName.endsWith(".docx") ||
      fileName.endsWith(".txt");

    // ========================================
    // FISH IMAGE
    // ========================================

    if (isFishImage) {
      try {
        setUploadStatus(
          "🐟 Analyzing fish image..."
        );

        const data =
          await predictFishImage(
            selectedFile
          );

        // ------------------------------------
        // SEND PREDICTION TO APP
        // ------------------------------------

        if (onFishPrediction) {
          await onFishPrediction(data);
        }

        if (!data.success || data.status === "NOT_FISH") {
          setUploadStatus(
            `⚠️ ${
              data.message ||
              "The uploaded image does not appear to contain a fish."
            }`
          );
          event.target.value = "";
          return;
        }

        // ------------------------------------
        // STATUS
        // ------------------------------------

        const species =
          data.predicted_species ||
          "Unknown species";

        const confidence =
          data.confidence ?? 0;

        const confidenceLevel =
          data.confidence_level ||
          "UNKNOWN";

        setUploadStatus(
          `✓ ${species} — ${Number(
            confidence
          ).toFixed(
            2
          )}% confidence (${confidenceLevel})`
        );
      } catch (error) {
        console.error(
          "Fish prediction error:",
          error
        );

        setUploadStatus(
          `❌ ${
            error.message ||
            "Fish image prediction failed."
          }`
        );
      }

      // Reset file input
      event.target.value = "";

      return;
    }

    // ========================================
    // DOCUMENT
    // ========================================

    if (isDocument) {
      try {
        setUploadStatus(
          "📄 Uploading document..."
        );

        const data =
          await uploadDocument(
            selectedFile
          );

        setUploadStatus(
          `✓ ${
            data.message ||
            "Document uploaded successfully."
          }`
        );
      } catch (error) {
        console.error(
          "Document upload error:",
          error
        );

        setUploadStatus(
          `❌ ${
            error.message ||
            "Document upload failed."
          }`
        );
      }

      // Reset file input
      event.target.value = "";

      return;
    }

    // ========================================
    // INVALID FILE
    // ========================================

    setUploadStatus(
      "❌ Unsupported file format. Use PDF, DOCX, TXT, JPG, JPEG, PNG, WEBP or BMP."
    );

    event.target.value = "";
  };

  // ==========================================
  // OPEN FILE PICKER
  // ==========================================

  const handleAttachClick = () => {
    fileInputRef.current?.click();
  };

  // ==========================================
  // SEND MESSAGE
  // ==========================================

  const handleSubmit = (event) => {
    event.preventDefault();

    const trimmedValue =
      value.trim();

    if (!trimmedValue) {
      return;
    }

    onSend(trimmedValue);
  };

  // ==========================================
  // VOICE INPUT
  // ==========================================

  const handleVoiceInput = () => {
    const SpeechRecognition =
      window.SpeechRecognition ||
      window.webkitSpeechRecognition;

    if (!SpeechRecognition) {
      setUploadStatus(
        "❌ Voice input is not supported by this browser."
      );

      return;
    }

    if (isListening) {
      return;
    }

    const recognition =
      new SpeechRecognition();

    recognition.continuous = false;
    recognition.interimResults = true;
    recognition.lang = "en-US";

    recognition.onstart = () => {
      setIsListening(true);

      setUploadStatus(
        "🎙️ Listening..."
      );
    };

    recognition.onresult = (event) => {
      let transcript = "";

      for (
        let i = event.resultIndex;
        i < event.results.length;
        i++
      ) {
        transcript +=
          event.results[i][0].transcript;
      }

      setValue(transcript);
    };

    recognition.onerror = (event) => {
      console.error(
        "Speech recognition error:",
        event.error
      );

      setUploadStatus(
        `❌ Voice input error: ${event.error}`
      );

      setIsListening(false);
    };

    recognition.onend = () => {
      setIsListening(false);

      setUploadStatus("");
    };

    recognition.start();
  };

  // ==========================================
  // KEYBOARD HANDLER
  // ==========================================

  const handleKeyDown = (event) => {
    if (event.key === "Enter" && !event.shiftKey) {
      event.preventDefault();

      handleSubmit(event);
    }
  };

  // ==========================================
  // UI
  // ==========================================

  return (
    <div className="mx-auto w-full max-w-4xl px-4 py-3">

      {/* UPLOAD STATUS */}

      {uploadStatus && (
        <div className="mb-2 px-2 text-sm text-zinc-500 dark:text-zinc-400">
          {uploadStatus}
        </div>
      )}

      {/* INPUT FORM */}

      <form
        onSubmit={handleSubmit}
        className="relative flex items-end gap-2 rounded-2xl border border-zinc-300 bg-white p-2 shadow-sm transition-colors duration-200 dark:border-zinc-700 dark:bg-zinc-900"
      >

        {/* HIDDEN FILE INPUT */}

        <input
          ref={fileInputRef}
          type="file"
          accept=".pdf,.docx,.txt,.jpg,.jpeg,.png,.webp,.bmp"
          onChange={handleFileChange}
          className="hidden"
        />

        {/* ATTACH BUTTON */}

        <button
          type="button"
          onClick={handleAttachClick}
          className="mb-0.5 rounded-xl p-2.5 text-zinc-500 transition hover:bg-zinc-100 hover:text-zinc-900 dark:hover:bg-zinc-800 dark:hover:text-white"
          title="Attach document or fish image"
          aria-label="Attach document or fish image"
        >
          <Paperclip size={20} />
        </button>

        {/* TEXTAREA */}

        <textarea
          value={value}
          onChange={(event) =>
            setValue(event.target.value)
          }
          onKeyDown={handleKeyDown}
          placeholder="Message FishAI..."
          rows={1}
          className="max-h-32 min-h-10 flex-1 resize-none bg-transparent px-2 py-2.5 text-sm text-zinc-900 outline-none placeholder:text-zinc-400 dark:text-white dark:placeholder:text-zinc-500"
        />

        {/* VOICE BUTTON */}

        <button
          type="button"
          onClick={handleVoiceInput}
          disabled={isListening}
          className={`mb-0.5 rounded-xl p-2.5 transition ${
            isListening
              ? "bg-red-100 text-red-600 dark:bg-red-950 dark:text-red-400"
              : "text-zinc-500 hover:bg-zinc-100 hover:text-zinc-900 dark:hover:bg-zinc-800 dark:hover:text-white"
          }`}
          title={
            isListening
              ? "Listening..."
              : "Voice input"
          }
          aria-label={
            isListening
              ? "Listening..."
              : "Voice input"
          }
        >
          {isListening ? (
            <Square size={18} />
          ) : (
            <Mic size={20} />
          )}
        </button>

        {/* SEND BUTTON */}

        <button
          type="submit"
          disabled={!value.trim()}
          className="mb-0.5 rounded-xl bg-zinc-900 p-2.5 text-white transition hover:bg-zinc-700 disabled:cursor-not-allowed disabled:opacity-40 dark:bg-white dark:text-zinc-900 dark:hover:bg-zinc-200"
          title="Send message"
          aria-label="Send message"
        >
          <Send size={19} />
        </button>
      </form>

      {/* FOOTER */}

      <p className="mt-2 text-center text-xs text-zinc-400 dark:text-zinc-600">
        FishAI can make mistakes. Verify important
        information.
      </p>
    </div>
  );
}

export default ChatInput;
