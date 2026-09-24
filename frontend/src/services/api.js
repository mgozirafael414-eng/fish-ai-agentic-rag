
const API_BASE_URL = "http://127.0.0.1:8000";
export const AUTH_TOKEN_KEY = "fishai_auth_token";

async function request(path, options = {}) {
  const headers = new Headers(options.headers || {});
  const token = localStorage.getItem(AUTH_TOKEN_KEY);
  if (token) headers.set("Authorization", `Bearer ${token}`);
  const response = await fetch(`${API_BASE_URL}${path}`, { ...options, headers });
  const data = await response.json().catch(() => ({}));
  if (!response.ok) throw new Error(data.detail || data.message || `Backend error: ${response.status}`);
  return data;
}

export async function authenticate(mode, payload) {
  const data = await request(`/api/auth/${mode}`, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(payload) });
  localStorage.setItem(AUTH_TOKEN_KEY, data.token);
  return data;
}
export async function logout() { try { await request("/api/auth/logout", { method: "POST" }); } finally { localStorage.removeItem(AUTH_TOKEN_KEY); } }
export async function getMe() { return request("/api/auth/me"); }
export async function getProfile() { return request("/api/profile"); }
export async function updateProfile(display_name) { return request("/api/profile", { method: "PATCH", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ display_name }) }); }
export async function getSettings() { return request("/api/settings"); }
export async function updateSettings(dark_mode) { return request("/api/settings", { method: "PATCH", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ dark_mode }) }); }
export async function getConversations() { return request("/api/conversations"); }
export async function getConversation(id) { return request(`/api/conversations/${id}`); }
export async function createConversation(title = "New chat") { return request("/api/conversations", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ title }) }); }
export async function deleteConversation(id) { return request(`/api/conversations/${id}`, { method: "DELETE" }); }
export async function saveConversationMessage(id, role, content, metadata = null) { return request(`/api/conversations/${id}/messages`, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ role, content, metadata }) }); }
export async function sendChatMessage(message, conversation = [], conversationId = null) { return request("/api/chat", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ message, conversation, conversation_id: conversationId }) }); }
export async function uploadDocument(file) { const formData = new FormData(); formData.append("file", file); return request("/api/documents/upload", { method: "POST", body: formData }); }
