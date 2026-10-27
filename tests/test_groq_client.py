import io
import json
import urllib.error

import pytest

from scripts import groq_client


def test_retry_transient_failure(monkeypatch):
    attempts = []

    def fake_urlopen(request, timeout):
        attempts.append(request)
        if len(attempts) == 1:
            raise urllib.error.HTTPError(request.full_url, 429, "rate limit", {}, None)
        return io.StringIO(json.dumps({"choices": [{"message": {"content": '{"approved":true}'}}]}))

    monkeypatch.setattr(groq_client.urllib.request, "urlopen", fake_urlopen)
    monkeypatch.setattr(groq_client.time, "sleep", lambda _: None)
    assert groq_client.completion({}, "test-only")["approved"] is True
    assert len(attempts) == 2
    assert attempts[0].get_header("User-agent") == "termo-devops/1.0"


def test_no_retry_invalid_credentials(monkeypatch):
    def fail(request, timeout):
        raise urllib.error.HTTPError(request.full_url, 401, "unauthorized", {}, None)

    monkeypatch.setattr(groq_client.urllib.request, "urlopen", fail)
    with pytest.raises(urllib.error.HTTPError):
        groq_client.completion({}, "test-only")
