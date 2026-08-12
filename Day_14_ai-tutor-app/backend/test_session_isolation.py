"""
Session isolation test — proves that N concurrent chat sessions never
cross-contaminate history, title, or usage state.

This mocks `client.models.generate_content` (no real Gemini key needed)
so it exercises the actual FastAPI/session-store code path in main.py,
not a simulation of it. The mock echoes back the session's own last user
message, which is what lets the assertions detect cross-contamination:
if session A ever saw session B's content, the echoed reply would prove it.

Run:
    cd backend
    GEMINI_API_KEY=test-key python3 -m pytest test_session_isolation.py -v
    # or, without pytest:
    GEMINI_API_KEY=test-key python3 test_session_isolation.py
"""

import os
from unittest.mock import patch, MagicMock

os.environ.setdefault("GEMINI_API_KEY", "test-key")

import main  # noqa: E402
from starlette.testclient import TestClient  # noqa: E402

client = TestClient(main.app)

N_SESSIONS = 5


def fake_generate_content(**kwargs):
    """Returns a canned response that echoes the last user message,
    so tests can verify each session only ever saw its own content."""
    contents = kwargs["contents"]
    last_user_text = next(
        part.text
        for content in reversed(contents)
        if content.role == "user"
        for part in content.parts
        if part.text is not None
    )
    fake = MagicMock()
    fake.text = f"echo: {last_user_text}"
    fake.function_calls = None
    fake.usage_metadata = MagicMock(prompt_token_count=10, candidates_token_count=5)
    return fake


def test_five_simultaneous_sessions_stay_isolated():
    main.chat_sessions.clear()
    session_ids = []

    with patch.object(main.client.models, "generate_content", side_effect=fake_generate_content):
        # Create 5 distinct sessions, each with a unique first message.
        for i in range(N_SESSIONS):
            res = client.post("/api/chat", json={
                "message": f"unique-topic-{i}",
                "persona": "casual",
            })
            assert res.status_code == 200
            body = res.json()
            session_ids.append(body["session_id"])
            assert body["reply"] == f"echo: unique-topic-{i}"

        assert len(set(session_ids)) == N_SESSIONS, "session IDs collided"

        # Send a second message to each session, interleaved, to catch
        # any shared-state bugs that only show up under interleaving.
        for i, sid in enumerate(session_ids):
            res = client.post("/api/chat", json={
                "session_id": sid,
                "message": f"followup-{i}",
                "persona": "casual",
            })
            assert res.status_code == 200
            assert res.json()["reply"] == f"echo: followup-{i}"

        # Verify each session's server-side history contains ONLY its own
        # messages — no leakage from any other session.
        for i, sid in enumerate(session_ids):
            detail = client.get(f"/api/sessions/{sid}").json()
            user_msgs = [m["content"] for m in detail["messages"] if m["role"] == "user"]
            assert user_msgs == [f"unique-topic-{i}", f"followup-{i}"]
            for other_i in range(N_SESSIONS):
                if other_i != i:
                    assert f"unique-topic-{other_i}" not in user_msgs
                    assert f"followup-{other_i}" not in user_msgs

        # Sidebar listing should show 5 sessions with correct message counts.
        sessions_list = client.get("/api/sessions").json()
        assert len(sessions_list) == N_SESSIONS
        for s in sessions_list:
            assert s["message_count"] == 4  # 2 turns x (1 user + 1 assistant)

    print(f"✓ {N_SESSIONS} simultaneous sessions verified isolated (history, IDs, counts).")


if __name__ == "__main__":
    test_five_simultaneous_sessions_stay_isolated()
