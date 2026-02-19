import subprocess, threading, os, sys, logging, secrets
from dotenv import load_dotenv
from flask import Flask, request, jsonify
import click

load_dotenv()

# suppress all flask/werkzeug output
log = logging.getLogger("werkzeug")
log.setLevel(logging.ERROR)

app = Flask(__name__)
SECRET = os.environ.get("TUNNEL_SECRET") or secrets.token_urlsafe(32)
TUNNEL_URL = os.environ["TUNNEL_URL"]
CF_TOKEN = os.environ["CF_TUNNEL_TOKEN"]

@app.route("/submit", methods=["POST"])
def filesize():
    if request.headers.get("X-Tunnel-Secret") != SECRET:
        return jsonify({"error": "unauthorized"}), 401
    file = request.files["file"]
    data = file.read()
    return jsonify({"filename": file.filename, "size": len(data)})

def start_tunnel():
    proc = subprocess.Popen(
        ["cloudflared", "tunnel", "run", "--token", CF_TOKEN],
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
    )
    return proc

def main():
    tunnel = None
    try:
        threading.Thread(
            target=lambda: app.run(port=8080, use_reloader=False),
            daemon=True
        ).start()
        print("Starting tunnel...")
        tunnel = start_tunnel()
        msg = (
            f"\nTunnel ready! Listening at: {TUNNEL_URL}\n"
            f"\n"
            f"To use from another machine:\n"
            f"  export TUNNEL_URL={TUNNEL_URL}\n"
            f"  export TUNNEL_SECRET={SECRET}\n"
            f"  uv run src/client.py\n"
            f"\n"
            f"Press Ctrl+C to stop\n"
        )
        print(msg)
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
