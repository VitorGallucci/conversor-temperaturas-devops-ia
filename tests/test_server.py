import json
import threading
import urllib.error
import urllib.request

import pytest

from conversor import server as module


@pytest.fixture
def app(tmp_path):
    server = module.make_server(port=0, directory=tmp_path)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    yield f"http://127.0.0.1:{server.server_port}", server, tmp_path
    server.shutdown()
    thread.join()
    server.server_close()


def request(app, route, data=None):
    req = urllib.request.Request(app[0] + route, data=data)
    try:
        response = urllib.request.urlopen(req, timeout=3)
    except urllib.error.HTTPError as error:
        response = error
    with response:
        return response.status, response.read()


def test_routes(app):
    assert b"termo" in request(app, "/")[1]
    assert json.loads(request(app, "/health")[1])["status"] == "ok"
    assert request(app, "/missing")[0] == 404
    assert request(app, "/missing", b"{}")[0] == 404
    assert json.loads(request(app, "/metrics")[1])["requests"] == 0


def test_api_and_telemetry(app):
    status, body = request(app, "/api/convert", b'{"value":25,"source":"C","target":"F"}')
    data = json.loads(body)
    assert status == 200 and data["result"] == 77
    metrics = json.loads(request(app, "/metrics")[1])
    assert metrics["requests"] == 1 and metrics["error_rate"] == 0
    assert metrics["p95_ms"] >= 0
    log = json.loads((app[2] / "app.jsonl").read_text())
    trace = json.loads((app[2] / "traces.jsonl").read_text())
    assert log["trace_id"] == trace["trace_id"] == data["trace_id"]
    assert [span["name"] for span in trace["spans"]] == ["parse", "convert"]


@pytest.mark.parametrize(
    "body", [b"{", b"[]", b"{}", b" ", b"x" * 4097, b'{"value":-300,"source":"C","target":"F"}']
)
def test_bad_requests(app, body):
    assert request(app, "/api/convert", body)[0] == 400
    assert app[1].telemetry.snapshot()["error_rate"] == 0


def test_internal_failure(app, monkeypatch):
    def broken(*_args):
        raise RuntimeError("Injected failure for test")

    monkeypatch.setattr(module, "convert", broken)
    assert request(app, "/api/convert", b'{"value":1,"source":"C","target":"F"}')[0] == 500
    assert app[1].telemetry.snapshot()["error_rate"] == 100
    assert "ERROR" in (app[2] / "app.jsonl").read_text()
