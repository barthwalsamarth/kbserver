"""Run the knowledge server over Streamable HTTP with bearer-token auth.

Usage:  python serve_http.py            (tokens from KB_TOKENS or generated)
        KB_TOKENS="t1:alice,t2:bob" python serve_http.py
"""
import os, secrets, sys
import anyio
import server
from kb.auth import parse_tokens, lookup
from mcp.server.auth.provider import AccessToken
from mcp.server.auth.settings import AuthSettings

class StaticTokenVerifier:
    def __init__(self, tokens: dict):
        self.tokens = tokens

    async def verify_token(self, token: str):
        user = lookup(self.tokens, token)
        if user is None:
            return None
        return AccessToken(token=token, client_id=user, scopes=[], subject=user)

def make_server(tokens: dict, host: str = "127.0.0.1", port: int = 8000):
    server.ALLOW_ENV_USER = False      # identity comes ONLY from the token
    auth = AuthSettings(
        # Stage 1 has no real authorization server; this is a placeholder.
        issuer_url="http://127.0.0.1:9000",
        resource_server_url=f"http://{host}:{port}/mcp",
        validate_token_resource=False,  # our verifier does its own check
    )
    return server.build_server(token_verifier=StaticTokenVerifier(tokens), auth=auth)

def main():
    host, port = "127.0.0.1", 8000
    spec = os.environ.get("KB_TOKENS", "")
    tokens = parse_tokens(spec)
    if not tokens:
        tokens = {secrets.token_urlsafe(24): u for u in ("alice", "bob", "carol")}
        print("No KB_TOKENS set. Generated dev tokens (shown once):")
        for tok, user in tokens.items():
            print(f"  {user}: {tok}")
    mcp = make_server(tokens, host, port)
    print(f"Serving on http://{host}:{port}/mcp  (Ctrl+C to stop)")
    anyio.run(lambda: mcp.run_streamable_http_async(host=host, port=port))

if __name__ == "__main__":
    main()
