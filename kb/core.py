"""Pure-Python core: no MCP dependency, fully unit-testable."""
import json, math, re
from collections import Counter
from dataclasses import dataclass
from pathlib import Path

INJECTION_PATTERNS = [
    r"ignore (all )?(previous|prior|above) instructions",
    r"you are now (in )?\w+ mode",
    r"(send|forward|email) .{0,60}(to|@)\s*\S+@\S+",
    r"system prompt",
]
_inj = re.compile("|".join(INJECTION_PATTERNS), re.I)
_tok = re.compile(r"[a-z0-9]+")

@dataclass(frozen=True)
class Doc:
    id: str
    title: str
    acl: frozenset
    passages: tuple

def load_corpus(path) -> dict:
    docs = {}
    for d in json.loads(Path(path).read_text()):
        passages = tuple(p.strip() for p in d["text"].split("\n\n") if p.strip())
        docs[d["id"]] = Doc(d["id"], d["title"], frozenset(d["acl"]), passages)
    return docs

def can_read(doc: Doc, user: str) -> bool:
    return bool(user) and user in doc.acl

def tokens(s): return _tok.findall(s.lower())

def is_suspicious(text: str) -> bool:
    return bool(_inj.search(text))

def search(corpus: dict, user: str, query: str, limit: int = 5):
    """Authorize FIRST, then rank. Unauthorized docs never reach scoring,
    so they can't leak through scores, counts or ordering."""
    visible = [d for d in corpus.values() if can_read(d, user)]
    q = tokens(query)
    if not q or not visible:
        return []
    chunks = [(d, i, p) for d in visible for i, p in enumerate(d.passages)]
    df = Counter(t for _, _, p in chunks for t in set(tokens(p)))
    n = len(chunks)
    out = []
    for d, i, p in chunks:
        tf = Counter(tokens(p))
        score = sum(tf[t] * (math.log((n + 1) / (df[t] + 1)) + 1) for t in q if t in tf)
        if score > 0:
            out.append({
                "source_id": f"{d.id}#{i}", "doc_id": d.id, "title": d.title,
                "score": round(score, 3),
                "passage": p,
                "flagged_untrusted": is_suspicious(p),
                "citation": f"[{d.id}#{i}]",
                "uri": f"docs://{d.id}/sections/{i}",
            })
    out.sort(key=lambda r: (-r["score"], r["source_id"]))
    return out[:max(1, min(limit, 20))]

def wrap_untrusted(text: str) -> str:
    """Delimit retrieved content so the model treats it as data, not instructions."""
    return ("<retrieved_document untrusted=\"true\">\n" + text +
            "\n</retrieved_document>")
