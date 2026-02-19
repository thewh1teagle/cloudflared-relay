import os
import io
import requests

TUNNEL_URL = os.environ["TUNNEL_URL"]

# create dummy file in memory
dummy_content = b"hello world " * 1000  # 12000 bytes
expected_size = len(dummy_content)

response = requests.post(
    f"{TUNNEL_URL.rstrip('/')}/submit",
    files={"file": ("dummy.txt", io.BytesIO(dummy_content))},
    headers={
        "X-Tunnel-Secret": os.environ.get("TUNNEL_SECRET", ""),
    },
)

print(f"Expected size: {expected_size}")
print(f"Status: {response.status_code}")
print(f"Response: {response.text}")
