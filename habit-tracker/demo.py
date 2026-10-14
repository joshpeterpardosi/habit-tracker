"""End-to-end demo: starts the server, exercises the API, stops it. Stdlib only."""
import json, os, socket, subprocess, sys, tempfile, urllib.error, urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))


def free_port():
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


def call(base, method, path, body=None):
    data = json.dumps(body).encode() if body is not None else None
    print(f"\n>>> {method} {path}" + (f"  {json.dumps(body)}" if body is not None else ""))
    req = urllib.request.Request(base + path, data=data, method=method)
    try:
        with urllib.request.urlopen(req, timeout=5) as r:
            code, out = r.status, json.loads(r.read())
    except urllib.error.HTTPError as e:
        code, out = e.code, json.loads(e.read())
    print(f"<<< {code}  {json.dumps(out)}")
    return code, out


def main():
    tmp = tempfile.mkdtemp()
    port = free_port()
    env = dict(os.environ, HABIT_DATA_FILE=os.path.join(tmp, "habits.json"))
    proc = subprocess.Popen([sys.executable, os.path.join(HERE, "src", "server.py"), str(port)],
                            env=env, stdout=subprocess.PIPE, text=True)
    try:
        line = proc.stdout.readline().strip()
        print(f"Server started (pid {proc.pid}): {line}")
        base = f"http://127.0.0.1:{port}"
        _, h = call(base, "POST", "/habits", {"name": "Read"})
        hid = h["habit_id"]
        call(base, "POST", f"/habits/{hid}/check-in")
        code, _ = call(base, "POST", f"/habits/{hid}/check-in")
        print(f"    duplicate check-in rejected: {code == 409}")
        call(base, "GET", f"/habits/{hid}/streak")
    finally:
        proc.terminate()
        proc.wait(timeout=5)
        print("\nServer stopped.")


if __name__ == "__main__":
    main()
