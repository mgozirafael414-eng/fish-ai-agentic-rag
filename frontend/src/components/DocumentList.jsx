import { useEffect, useState } from "react";
import {
  FileText,
  Trash2,
  RefreshCw,
  Loader2,
  AlertCircle,
} from "lucide-react";

function DocumentList() {
  const [documents, setDocuments] = useState([]);
  const [loading, setLoading] = useState(false);
  const [deleting, setDeleting] = useState("");
  const [error, setError] = useState("");

  // =========================================================
  // LOAD DOCUMENTS
  // =========================================================

  const loadDocuments = async () => {
    setLoading(true);
    setError("");

    try {
      const response = await fetch(
        "http://127.0.0.1:8000/api/documents/"
      );

      const data = await response.json();

      if (!response.ok) {
        throw new Error(
          data.detail || "Failed to load documents."
        );
      }

      setDocuments(data.documents || []);

    } catch (err) {
      console.error(
        "Document List Error:",
        err
      );

      setError(
        err.message ||
          "Failed to load documents."
      );

    } finally {
      setLoading(false);
    }
  };


  // =========================================================
  // LOAD DOCUMENTS WHEN COMPONENT MOUNTS
  // =========================================================

  useEffect(() => {
    loadDocuments();
  }, []);


  // =========================================================
  // DELETE DOCUMENT
  // =========================================================

  const handleDelete = async (filename) => {

    const confirmed = window.confirm(
      `Are you sure you want to delete "${filename}"?`
    );

    if (!confirmed) {
      return;
    }

    setDeleting(filename);
    setError("");

    try {

      const response = await fetch(
        `http://127.0.0.1:8000/api/documents/${encodeURIComponent(
          filename
        )}`,
        {
          method: "DELETE",
        }
      );

      const data = await response.json();

      if (!response.ok) {
        throw new Error(
          data.detail ||
            "Failed to delete document."
        );
      }

      // Remove document from UI
      setDocuments((previous) =>
        previous.filter(
          (document) =>
            document.filename !== filename
        )
      );

    } catch (err) {

      console.error(
        "Document Delete Error:",
        err
      );

      setError(
        err.message ||
          "Failed to delete document."
      );

    } finally {
      setDeleting("");
    }
  };


  // =========================================================
  // UI
  // =========================================================

  return (
    <div className="rounded-xl border border-zinc-200 bg-white p-4 dark:border-zinc-800 dark:bg-zinc-900">

      {/* =====================================================
          HEADER
      ===================================================== */}

      <div className="mb-4 flex items-center justify-between">

        <div className="flex items-center gap-2">

          <FileText size={18} />

          <div>
            <h2 className="text-sm font-semibold">
              Knowledge Base
            </h2>

            <p className="text-xs text-zinc-500">
              {documents.length} document
              {documents.length !== 1
                ? "s"
                : ""}
            </p>
          </div>

        </div>


        {/* Refresh */}

        <button
          type="button"
          onClick={loadDocuments}
          disabled={loading}
          className="rounded-lg p-2 text-zinc-500 transition hover:bg-zinc-100 hover:text-zinc-900 disabled:opacity-50 dark:hover:bg-zinc-800 dark:hover:text-white"
          title="Refresh documents"
          aria-label="Refresh documents"
        >

          {loading ? (
            <Loader2
              size={17}
              className="animate-spin"
            />
          ) : (
            <RefreshCw size={17} />
          )}

        </button>

      </div>


      {/* =====================================================
          ERROR
      ===================================================== */}

      {error && (

        <div className="mb-4 flex items-start gap-2 rounded-lg bg-red-50 p-3 text-sm text-red-700 dark:bg-red-950/30 dark:text-red-400">

          <AlertCircle
            size={18}
            className="mt-0.5 shrink-0"
          />

          <span>
            {error}
          </span>

        </div>

      )}


      {/* =====================================================
          LOADING
      ===================================================== */}

      {loading && documents.length === 0 && (

        <div className="flex items-center justify-center gap-2 py-6 text-sm text-zinc-500">

          <Loader2
            size={18}
            className="animate-spin"
          />

          Loading documents...

        </div>

      )}


      {/* =====================================================
          EMPTY STATE
      ===================================================== */}

      {!loading &&
        documents.length === 0 &&
        !error && (

          <div className="py-6 text-center">

            <FileText
              size={32}
              className="mx-auto mb-2 text-zinc-400"
            />

            <p className="text-sm text-zinc-500">
              No documents uploaded yet.
            </p>

          </div>
        )}


      {/* =====================================================
          DOCUMENTS
      ===================================================== */}

      {documents.length > 0 && (

        <div className="space-y-2">

          {documents.map((document) => (

            <div
              key={document.filename}
              className="flex items-center justify-between gap-3 rounded-lg border border-zinc-200 p-3 dark:border-zinc-800"
            >

              {/* Document information */}

              <div className="flex min-w-0 items-center gap-3">

                <div className="shrink-0 rounded-lg bg-zinc-100 p-2 dark:bg-zinc-800">

                  <FileText
                    size={18}
                  />

                </div>


                <div className="min-w-0">

                  <p className="truncate text-sm font-medium">
                    {document.filename}
                  </p>

                  <p className="text-xs text-zinc-500">
                    {document.chunks} chunk
                    {document.chunks !== 1
                      ? "s"
                      : ""}
                  </p>

                </div>

              </div>


              {/* Delete button */}

              <button
                type="button"
                onClick={() =>
                  handleDelete(
                    document.filename
                  )
                }
                disabled={
                  deleting ===
                  document.filename
                }
                className="shrink-0 rounded-lg p-2 text-zinc-500 transition hover:bg-red-50 hover:text-red-600 disabled:cursor-not-allowed disabled:opacity-50 dark:hover:bg-red-950/30"
                title="Delete document"
                aria-label={`Delete ${document.filename}`}
              >

                {deleting ===
                document.filename ? (

                  <Loader2
                    size={17}
                    className="animate-spin"
                  />

                ) : (

                  <Trash2
                    size={17}
                  />

                )}

              </button>

            </div>

          ))}

        </div>

      )}

    </div>
  );
}

export default DocumentList;