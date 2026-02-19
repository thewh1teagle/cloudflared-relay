import subprocess, re, threading, os, sys, time, logging, secrets
from flask import Flask, request, jsonify
import click

# suppress all flask/werkzeug output
log = logging.getLogger("werkzeug")
log.setLevel(logging.ERROR)


app = Flask(__name__)
SECRET = os.environ.get("TUNNEL_SECRET") or secrets.token_urlsafe(32)

@app.route("/submit", methods=["POST"])
def filesize():
    if request.headers.get("X-Tunnel-Secret") != SECRET:
        return jsonify({"error": "unauthorized"}), 401
    file = request.files["file"]
    data = file.read()
    return jsonify({"filename": file.filename, "size": len(data)})

def start_tunnel(local_port=8080):
    proc = subprocess.Popen(
        ["ssh", "-T", "-R", f"80:localhost:{local_port}", "-o", "StrictHostKeyChecking=no", "serveo.net"],
        stdout=subprocess.PIPE, stderr=subprocess.STDOUT
    )
    for line in proc.stdout:
        text = line.decode().replace('\r', '').strip()
        match = re.search(r'https://\S+', text)
        if match and 'console.serveo.net' not in match.group():
            # drain remaining output in background
            threading.Thread(target=proc.stdout.read, daemon=True).start()
            return proc, match.group()
    raise RuntimeError("Failed to get tunnel URL")

def main():
    tunnel = None
    try:
        threading.Thread(
            target=lambda: app.run(port=8080, use_reloader=False),
            daemon=True
        ).start()
        time.sleep(0.5)
        sys.stdout.write("Starting tunnel...\n")
        sys.stdout.flush()
        tunnel, url = start_tunnel()
        msg = (
            f"\nTunnel ready! Listening at: {url}\n"
            f"\n"
            f"To use from another machine:\n"
            f"  export TUNNEL_URL={url}\n"
            f"  export TUNNEL_SECRET={SECRET}\n"
            f"  uv run src/client.py\n"
            f"\n"
            f"Press Ctrl+C to stop\n"
        )
        sys.stdout.write(msg)
        sys.stdout.flush()
        tunnel.wait()
    except KeyboardInterrupt:
        print("\nShutting down...")
    finally:
        if tunnel:
            tunnel.kill()
            tunnel.wait()
        print("Cleaned up")

if __name__ == "__main__":
    main()
