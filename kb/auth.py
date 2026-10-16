"""Token -> user mapping. No MCP dependency, so it is unit-testable anywhere."""
import hmac

def parse_tokens(spec: str) -> dict:
    """'tokA:alice,tokB:bob' -> {'tokA': 'alice', 'tokB': 'bob'}"""
    out = {}
    for item in filter(None, (s.strip() for s in spec.split(","))):
        tok, _, user = item.partition(":")
        if tok and user:
            out[tok] = user
    return out

def lookup(tokens: dict, presented: str):
    """Constant-time comparison against every known token (no early exit)."""
    found = None
    for tok, user in tokens.items():
        if hmac.compare_digest(tok.encode(), (presented or "").encode()):
            found = user
    return found
