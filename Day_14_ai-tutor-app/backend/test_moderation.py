"""
Moderation test — proves that harsh/abusive user messages are intercepted
locally and NEVER reach the Gemini API, and that ordinary messages pass
through untouched.

Like test_session_isolation.py, this mocks `client.models.generate_content`
so it exercises the real FastAPI route in main.py. Here the mock is used
to assert it was *not* called for flagged messages, and *was* called for
clean ones.

Run:
    cd backend
    GEMINI_API_KEY=test-key python3 -m pytest test_moderation.py -v
    # or, without pytest:
    GEMINI_API_KEY=test-key python3 test_moderation.py
"""

import os
from unittest.mock import patch, MagicMock

os.environ.setdefault("GEMINI_API_KEY", "test-key")

import main  # noqa: E402
from starlette.testclient import TestClient  # noqa: E402
from moderation import check_tone  # noqa: E402

client = TestClient(main.app)


def fake_generate_content(**kwargs):
    fake = MagicMock()
    fake.text = "a real model reply"
    fake.function_calls = None
    fake.usage_metadata = MagicMock(prompt_token_count=10, candidates_token_count=5)
    return fake


def test_abusive_message_is_blocked_before_reaching_model():
    main.chat_sessions.clear()
    with patch.object(main.client.models, "generate_content", side_effect=fake_generate_content) as mock_call:
        res = client.post("/api/chat", json={
            "message": "You are so stupid, this app is useless.",
            "persona": "casual",
        })
        assert res.status_code == 200
        body = res.json()
        assert body["moderated"] is True
        assert body["usage"]["prompt_tokens"] == 0
        assert body["usage"]["cost"] == 0.0
        assert "a real model reply" not in body["reply"]
        mock_call.assert_not_called()


def test_shouting_without_profanity_is_also_blocked():
    main.chat_sessions.clear()
    with patch.object(main.client.models, "generate_content", side_effect=fake_generate_content) as mock_call:
        res = client.post("/api/chat", json={
            "message": "WHY DOES THIS NEVER WORK RIGHT????",
            "persona": "casual",
        })
        assert res.status_code == 200
        assert res.json()["moderated"] is True
        mock_call.assert_not_called()


def test_ordinary_question_is_not_flagged_and_reaches_model():
    main.chat_sessions.clear()
    with patch.object(main.client.models, "generate_content", side_effect=fake_generate_content) as mock_call:
        res = client.post("/api/chat", json={
            "message": "Can you explain how recursion works?",
            "persona": "casual",
        })
        assert res.status_code == 200
        body = res.json()
        assert body["moderated"] is False
        assert body["reply"] == "a real model reply"
        mock_call.assert_called_once()


def test_check_tone_unit_behavior():
    assert check_tone("This is a normal, polite question.")["flagged"] is False
    assert check_tone("You are an idiot and this is garbage.")["flagged"] is True
    assert check_tone("STOP BREAKING EVERYTHING!!!")["flagged"] is True


if __name__ == "__main__":
    test_abusive_message_is_blocked_before_reaching_model()
    test_shouting_without_profanity_is_also_blocked()
    test_ordinary_question_is_not_flagged_and_reaches_model()
    test_check_tone_unit_behavior()
    print("✓ moderation tests passed: abusive/shouting messages blocked pre-model, clean messages pass through.")
