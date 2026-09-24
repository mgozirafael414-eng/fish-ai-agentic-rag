import { AUTH_TOKEN_KEY } from "./api";

const API_BASE_URL = "http://127.0.0.1:8000";

export async function predictFishImage(file) {
  const formData = new FormData();

  formData.append("file", file);

  const response = await fetch(
    `${API_BASE_URL}/api/fish/predict`,
    {
      method: "POST",
      headers: {
        Authorization: `Bearer ${localStorage.getItem(AUTH_TOKEN_KEY) || ""}`,
      },
      body: formData,
    }
  );

  const data = await response.json();

  if (!response.ok) {
    throw new Error(
      data.detail || "Fish image prediction failed."
    );
  }

  return data;
}