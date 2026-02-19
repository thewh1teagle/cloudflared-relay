# cloudflared-relay

Local Flask server tunneled via Cloudflare Tunnel. Receives files from GitHub Actions, processes them locally, and returns results.

## Prerequisites

- Python 3.12+
- [uv](https://docs.astral.sh/uv/)
- [cloudflared](https://developers.cloudflare.com/cloudflare-one/connections/connect-networks/downloads/) (`brew install cloudflare/cloudflare/cloudflared`)
- A domain with DNS managed by Cloudflare (free plan works, domain ~$10/yr from any registrar)

## Setup

### 1. Create a Cloudflare Tunnel

1. Go to [Cloudflare Zero Trust](https://one.dash.cloudflare.com) > Networks > Tunnels > Create a tunnel
2. Choose **Cloudflared** as connector
3. Name it and copy the token
4. Add a public hostname:
   - Subdomain: your choice (e.g. `tunnel`)
   - Domain: your Cloudflare domain
   - Service type: `HTTP`
   - URL: `localhost:8080`

### 2. Configure `.env`

```console
CP_TUNNEL_TOKEN=<your-cloudflare-tunnel-token>
TUNNEL_SECRET=<any-random-secret>
TUNNEL_URL=https://<your-subdomain>.<your-domain>
```

Generate a secret: `uv run python -c "import secrets; print(secrets.token_urlsafe(32))"`

### 3. Run

```console
uv run src/server.py
```

### 4. Test from another machine

```console
export TUNNEL_URL=https://<your-subdomain>.<your-domain>
export TUNNEL_SECRET=<same-secret-as-server>
uv run src/client.py
```

## Optional: Rate Limiting

To protect against brute force attacks on the endpoint:

1. Go to [Cloudflare Dashboard](https://dash.cloudflare.com) > your domain > Security > WAF
2. Create a rate limiting rule with expression:
   ```console
   (http.host eq "<your-subdomain>.<your-domain>" and http.request.uri.path eq "/submit")
   ```
   - Rate: 50 requests per 10 seconds
   - Action: Block
