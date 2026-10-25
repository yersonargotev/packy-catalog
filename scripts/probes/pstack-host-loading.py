#!/usr/bin/env python3
"""Exercise real Claude loading with a localhost deterministic provider.

No model inference, credentials, or external side effects. Native skill bodies
and auxiliary tool reads must actually reach the provider. Run from the catalog:
python3 scripts/probes/pstack-host-loading.py claude [global|project]
"""
import http.server
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import threading


host = sys.argv[1]
scope = sys.argv[2] if len(sys.argv) > 2 else "project"
assert host == "claude" and scope in ("global", "project")
binary = shutil.which(host)
assert binary, f"{host} is not installed"
with tempfile.TemporaryDirectory(prefix=f"pstack-{host}-{scope}-") as directory:
    root = Path(directory).resolve()
    project = root / "project"
    project.mkdir()
    env = {"PATH": "/usr/bin:/bin:/usr/sbin:/sbin", "LANG": "en_US.UTF-8", "TERM": "dumb"}
    for key, directory in [("HOME", "home"), ("XDG_CONFIG_HOME", "config"), ("XDG_DATA_HOME", "data"), ("XDG_STATE_HOME", "state"), ("XDG_CACHE_HOME", "cache"), ("TMPDIR", "tmp"), ("CODEX_HOME", "codex"), ("CLAUDE_CONFIG_DIR", "claude")]:
        (root / directory).mkdir()
        env[key] = str(root / directory)
    subprocess.run(["git", "init", "-q", str(project)], env=env, check=True)
    catalog = Path(__file__).resolve().parents[2]
    if scope == "project":
        native = project / ".claude/skills"
    else:
        native = root / "claude/skills"
    shutil.copytree(catalog / "packs/pstack/skills" / host, native)
    auxiliary = native / "reflect/references/judgment-reviewer.md"
    requests = []


    class Provider(http.server.BaseHTTPRequestHandler):
        def log_message(self, *args):
            pass

        def do_POST(self):
            body = json.loads(self.rfile.read(int(self.headers["Content-Length"])))
            requests.append(body)
            self.send_response(200)
            self.send_header("Content-Type", "text/event-stream")
            self.end_headers()
            first = not any("tool_result" in json.dumps(message) for message in body.get("messages", []))
            def emit(event, **data):
                self.wfile.write((f"event: {event}\ndata: " + json.dumps({"type": event, **data}) + "\n\n").encode())
            emit("message_start", message={"id": "msg_probe", "type": "message", "role": "assistant", "content": [], "model": body.get("model"), "stop_reason": None, "stop_sequence": None, "usage": {"input_tokens": 1, "output_tokens": 1}})
            block = {"type": "tool_use", "id": "read_probe", "name": "Read", "input": {}} if first else {"type": "text", "text": ""}
            emit("content_block_start", index=0, content_block=block)
            delta = {"type": "input_json_delta", "partial_json": json.dumps({"file_path": str(auxiliary)})} if first else {"type": "text_delta", "text": "Deterministic loading probe completed; no inference."}
            emit("content_block_delta", index=0, delta=delta)
            emit("content_block_stop", index=0)
            emit("message_delta", delta={"stop_reason": "tool_use" if first else "end_turn", "stop_sequence": None}, usage={"output_tokens": 1})
            emit("message_stop")
            self.wfile.flush()


    server = http.server.ThreadingHTTPServer(("127.0.0.1", 0), Provider)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    url = f"http://127.0.0.1:{server.server_port}"
    env.update(ANTHROPIC_API_KEY="fake-local-only", ANTHROPIC_BASE_URL=url, CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC="1")
    command = [binary, "-p", "/reflect Inspect the current session only. Read the judgment reviewer reference. Do not modify files or publish anything.", "--output-format", "stream-json", "--verbose", "--no-session-persistence", "--tools", "Read", "--allowedTools", "Read", "--strict-mcp-config", "--mcp-config", '{"mcpServers":{}}']
    try:
        result = subprocess.run(command, cwd=project, env=env, capture_output=True, text=True, timeout=55)
        (root / "stdout.jsonl").write_text(result.stdout)
        (root / "stderr.txt").write_text(result.stderr)
        (root / "requests.json").write_text(json.dumps(requests, indent=2))
        payload = json.dumps(requests)
        label = "Claude Code"
        summary = {"host": host, "scope": scope, "version": subprocess.run([binary, "--version"], env=env, capture_output=True, text=True, check=True).stdout.strip(), "exit": result.returncode, "native_body_loaded": f"## {label} execution" in payload, "auxiliary_read": "You are a reviewer applying the judgment lens" in payload, "requests": len(requests), "inference": False, "evidence": str(root)}
        (root / "summary.json").write_text(json.dumps(summary, indent=2))
        print(json.dumps(summary), flush=True)
        assert result.returncode == 0 and summary["native_body_loaded"] and summary["auxiliary_read"], summary
    finally:
        server.shutdown()
        server.server_close()
