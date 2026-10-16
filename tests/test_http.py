"""Real HTTP: starts the server in a thread and checks that auth is enforced.
Needs the venv (mcp, uvicorn). Run: pytest tests/test_http.py"""
import socket, threading, time, urllib.request, urllib.error
import pytest, uvicorn
import server, serve_http

def _free_port():
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]

@pytest.fixture(scope="module")
def port():
    old = server.ALLOW_ENV_USER
    p = _free_port()
    mcp = serve_http.make_server({"tok-alice": "alice"}, port=p)
    app = mcp.streamable_http_app(host="127.0.0.1")
    srv = uvicorn.Server(uvicorn.Config(app, host="127.0.0.1", port=p, log_level="warning"))
    t = threading.Thread(target=srv.run, daemon=True)
    t.start()
    for _ in range(200):
        if srv.started:
            break
        time.sleep(0.05)
    yield p
    srv.should_exit = True
    t.join(5)
    server.ALLOW_ENV_USER = old

def post(port, token=None):
    h = {"Content-Type": "application/json", "Accept": "application/json, text/event-stream"}
    if token:
        h["Authorization"] = f"Bearer {token}"
    req = urllib.request.Request(f"http://127.0.0.1:{port}/mcp", data=b"{}", headers=h, method="POST")
    try:
        return urllib.request.urlopen(req, timeout=5).status
    except urllib.error.HTTPError as e:
        return e.code

def test_no_token_is_401(port):
    assert post(port) == 401

def test_bad_token_is_401(port):
    assert post(port, "wrong") == 401

def test_good_token_passes_auth(port):
    assert post(port, "tok-alice") != 401   # body is junk, so any non-401 means auth passed
