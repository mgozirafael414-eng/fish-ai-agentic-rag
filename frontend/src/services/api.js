
const API_BASE_URL = "http://127.0.0.1:8000";

// ==========================================
// SEND CHAT MESSAGE
// ==========================================

export async function sendChatMessage(
  message,
  conversation = []
) {
  const response = await fetch(
    `${API_BASE_URL}/api/chat`,
    {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        message: message,
        conversation: conversation,
      }),
    }
  );

  if (!response.ok) {
    throw new Error(
      `Backend error: ${response.status}`
    );
  }

  return await response.json();
}


// ==========================================
// UPLOAD DOCUMENT
// ==========================================

export async function uploadDocument(file) {
  const formData = new FormData();

  formData.append("file", file);

  const response = await fetch(
    `${API_BASE_URL}/api/documents/upload`,
    {
      method: "POST",
      body: formData,
    }
  );

  const data = await response.json();

  if (!response.ok) {
    throw new Error(
      data.detail ||
        data.message ||
        "Document upload failed."
    );
  }

  return data;
}
