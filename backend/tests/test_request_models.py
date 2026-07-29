from app.models.requests import ChatRequest, FeedbackRequest


def test_chat_request_accepts_short_session_id():
    payload = ChatRequest(question="What is this?", session_id="sess-1")

    assert payload.session_id == "sess-1"


def test_feedback_request_accepts_short_session_id():
    payload = FeedbackRequest(message_id="message-1", session_id="sess-1", rating="good")

    assert payload.session_id == "sess-1"
