"""Servidor HTTP local com logs JSON, métricas e traces por requisição."""

import argparse
import json
import threading
import time
import uuid
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlsplit

from conversor.core import convert

ROOT = Path(__file__).resolve().parents[1]


class Telemetry:
    def __init__(self, directory):
        self.directory = Path(directory)
        self.directory.mkdir(parents=True, exist_ok=True)
        self.lock = threading.Lock()
        self.requests = 0
        self.errors = 0
        self.latencies = []

    def record(self, status, elapsed, trace_id, spans):
        with self.lock:
            self.requests += 1
            self.errors += status >= 500
            self.latencies.append(elapsed)
            self.latencies = self.latencies[-1000:]
            log = {
                "level": "ERROR" if status >= 500 else "INFO",
                "status": status,
                "trace_id": trace_id,
                "duration_ms": elapsed,
            }
            with (self.directory / "app.jsonl").open("a", encoding="utf-8") as stream:
                stream.write(json.dumps(log) + "\n")
            trace = {"trace_id": trace_id, "spans": spans, "status": status}
            with (self.directory / "traces.jsonl").open("a", encoding="utf-8") as stream:
                stream.write(json.dumps(trace) + "\n")

    def snapshot(self):
        with self.lock:
            ordered = sorted(self.latencies)
            index = max(0, math_ceil(len(ordered) * 0.95) - 1)
            return {
                "requests": self.requests,
                "errors": self.errors,
                "error_rate": 100 * self.errors / max(1, self.requests),
                "p95_ms": ordered[index] if ordered else 0,
                "window": "last_1000_latency_samples; cumulative_error_rate",
            }


def math_ceil(number):
    return int(-(-number // 1))


def make_server(host="127.0.0.1", port=8000, directory="runtime"):
    telemetry = Telemetry(directory)

    class Handler(BaseHTTPRequestHandler):
        def log_message(self, *_args):
            pass

        def send(self, status, payload, content_type="application/json; charset=utf-8"):
            body = (
                payload
                if isinstance(payload, bytes)
                else json.dumps(payload, ensure_ascii=False, allow_nan=False).encode("utf-8")
            )
            self.send_response(status)
            self.send_header("Content-Type", content_type)
            self.send_header("Content-Length", str(len(body)))
            self.send_header("X-Content-Type-Options", "nosniff")
            self.end_headers()
            self.wfile.write(body)

        def do_GET(self):
            route = urlsplit(self.path).path
            if route == "/":
                self.send(200, (ROOT / "web/index.html").read_bytes(), "text/html; charset=utf-8")
            elif route == "/health":
                self.send(200, {"status": "ok"})
            elif route == "/metrics":
                self.send(200, telemetry.snapshot())
            else:
                self.send(404, {"error": "Rota não encontrada."})

        def do_POST(self):
            if urlsplit(self.path).path != "/api/convert":
                self.send(404, {"error": "Rota não encontrada."})
                return
            started = time.perf_counter()
            trace_id = uuid.uuid4().hex
            spans = []
            status = 200
            try:
                length = int(self.headers.get("Content-Length", "0"))
                if length <= 0 or length > 4096:
                    raise ValueError("Corpo deve ter entre 1 e 4096 bytes.")
                data = json.loads(self.rfile.read(length))
                if not isinstance(data, dict):
                    raise ValueError("Envie um objeto JSON.")
                spans.append(
                    {
                        "name": "parse",
                        "duration_ms": (time.perf_counter() - started) * 1000,
                        "status": "ok",
                    }
                )
                calculation = time.perf_counter()
                result = convert(data.get("value"), data.get("source"), data.get("target"))
                spans.append(
                    {
                        "name": "convert",
                        "duration_ms": (time.perf_counter() - calculation) * 1000,
                        "status": "ok",
                    }
                )
                payload = {"result": result, "unit": data["target"], "trace_id": trace_id}
            except (ValueError, TypeError, UnicodeError) as error:
                status = 400
                payload = {"error": str(error), "trace_id": trace_id}
                spans.append({"name": "validation", "status": "invalid_input", "duration_ms": 0})
            except Exception:
                status = 500
                payload = {"error": "Erro interno.", "trace_id": trace_id}
                spans.append({"name": "convert", "status": "error", "duration_ms": 0})
            telemetry.record(status, (time.perf_counter() - started) * 1000, trace_id, spans)
            self.send(status, payload)

    server = ThreadingHTTPServer((host, port), Handler)
    server.telemetry = telemetry
    return server


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8000)
    args = parser.parse_args()
    with make_server(args.host, args.port) as server:
        print(f"Conversor em http://{args.host}:{args.port}", flush=True)
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            pass


if __name__ == "__main__":
    main()
