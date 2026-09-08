import { useState } from "react";
import { FileUp, CheckCircle, AlertCircle, Loader2 } from "lucide-react";

function DocumentUpload() {
  const [file, setFile] = useState(null);
  const [uploading, setUploading] = useState(false);
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");

  const handleFileChange = (event) => {
    const selectedFile = event.target.files?.[0];

    setMessage("");
    setError("");

    if (!selectedFile) {
      setFile(null);
      return;
    }

    const allowedTypes = [".pdf", ".docx", ".txt"];
    const extension =
      "." + selectedFile.name.split(".").pop().toLowerCase();

    if (!allowedTypes.includes(extension)) {
      setFile(null);
      setError("Only PDF, DOCX, and TXT files are allowed.");
      return;
    }

    setFile(selectedFile);
  };

  const handleUpload = async () => {
    if (!file) {
      setError("Please choose a document first.");
      return;
    }

    setUploading(true);
    setMessage("");
    setError("");

    try {
      const formData = new FormData();

      formData.append("file", file);

      const response = await fetch(
        "http://127.0.0.1:8000/api/documents/upload",
        {
          method: "POST",
          body: formData,
        }
      );

      const data = await response.json();

      if (!response.ok) {
        throw new Error(
          data.detail || "Failed to upload document."
        );
      }

      setMessage(
        `${data.filename} uploaded successfully. ${data.chunks_stored} chunks stored.`
      );

      setFile(null);

    } catch (err) {
      setError(
        err.message || "Failed to upload document."
      );
    } finally {
      setUploading(false);
    }
  };

  return (
    <div className="border-t border-gray-200 p-4">
      <div className="flex items-center gap-2 mb-3">
        <FileUp size={18} />

        <span className="font-medium text-sm">
          Upload Document
        </span>
      </div>

      <div className="flex flex-col gap-3">

        <input
          type="file"
          accept=".pdf,.docx,.txt"
          onChange={handleFileChange}
          className="text-sm"
        />

        {file && (
          <p className="text-sm text-gray-600">
            Selected: {file.name}
          </p>
        )}

        <button
          onClick={handleUpload}
          disabled={!file || uploading}
          className="flex items-center justify-center gap-2 rounded-lg bg-black px-4 py-2 text-sm text-white disabled:cursor-not-allowed disabled:opacity-50"
        >
          {uploading ? (
            <>
              <Loader2
                size={16}
                className="animate-spin"
              />

              Uploading...
            </>
          ) : (
            <>
              <FileUp size={16} />

              Upload Document
            </>
          )}
        </button>

        {message && (
          <div className="flex items-start gap-2 rounded-lg bg-green-50 p-3 text-sm text-green-700">
            <CheckCircle
              size={18}
              className="mt-0.5 shrink-0"
            />

            <span>{message}</span>
          </div>
        )}

        {error && (
          <div className="flex items-start gap-2 rounded-lg bg-red-50 p-3 text-sm text-red-700">
            <AlertCircle
              size={18}
              className="mt-0.5 shrink-0"
            />

            <span>{error}</span>
          </div>
        )}

        <p className="text-xs text-gray-500">
          Supported formats: PDF, DOCX, TXT
        </p>

      </div>
    </div>
  );
}

export default DocumentUpload;