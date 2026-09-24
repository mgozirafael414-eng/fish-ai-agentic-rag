import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from fastapi.testclient import TestClient

import app.db as db
from app.main import app


class PersistenceApiTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        db.DB_PATH = Path(self.temp_dir.name) / "test.sqlite3"
        db.init_db()
        self.client = TestClient(app)

        user_a = self.client.post(
            "/api/auth/register",
            json={"email": "a@example.com", "password": "password123", "display_name": "User A"},
        )
        user_b = self.client.post(
            "/api/auth/register",
            json={"email": "b@example.com", "password": "password123", "display_name": "User B"},
        )
        self.assertEqual(user_a.status_code, 200)
        self.assertEqual(user_b.status_code, 200)
        self.headers_a = {"Authorization": f"Bearer {user_a.json()['token']}"}
        self.headers_b = {"Authorization": f"Bearer {user_b.json()['token']}"}

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_profile_settings_and_isolation(self):
        profile = self.client.patch(
            "/api/profile", headers=self.headers_a, json={"display_name": "Saved A"}
        )
        settings = self.client.patch(
            "/api/settings", headers=self.headers_a, json={"dark_mode": True}
        )
        self.assertEqual(profile.json()["profile"]["display_name"], "Saved A")
        self.assertTrue(settings.json()["settings"]["dark_mode"])

        conversation = self.client.post(
            "/api/conversations", headers=self.headers_a, json={"title": "Private chat"}
        ).json()["conversation"]
        conversation_id = conversation["id"]
        message = self.client.post(
            f"/api/conversations/{conversation_id}/messages",
            headers=self.headers_a,
            json={"role": "user", "content": "Private message"},
        )
        self.assertEqual(message.status_code, 200)
        self.assertEqual(
            self.client.get(f"/api/conversations/{conversation_id}", headers=self.headers_b).status_code,
            404,
        )

    def test_chat_saves_user_and_assistant_messages(self):
        with patch("app.api.chat.generate_ai_response", return_value="Persisted assistant response"):
            response = self.client.post(
                "/api/chat",
                headers=self.headers_a,
                json={"message": "Hello, this is a persistence test."},
            )
        self.assertEqual(response.status_code, 200)
        conversation_id = response.json()["conversation_id"]
        detail = self.client.get(
            f"/api/conversations/{conversation_id}", headers=self.headers_a
        ).json()["conversation"]
        self.assertEqual([message["role"] for message in detail["messages"]], ["user", "assistant"])
        self.assertEqual(detail["messages"][1]["content"], "Persisted assistant response")

    def test_logout_invalidates_session(self):
        self.assertEqual(self.client.post("/api/auth/logout", headers=self.headers_a).status_code, 200)
        self.assertEqual(self.client.get("/api/auth/me", headers=self.headers_a).status_code, 401)


if __name__ == "__main__":
    unittest.main()
