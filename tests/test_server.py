"""End-to-end via in-memory client. Needs: pip install "mcp>=2,<3" pytest anyio"""
import pytest
from mcp import Client          # SDK
import server

pytestmark = pytest.mark.anyio

@pytest.fixture
def anyio_backend(): return "asyncio"

async def call(user, query):
    server.os.environ["KB_USER"] = user
    async with Client(server.mcp) as c:
        return await c.call_tool("search_docs", {"query": query})

async def test_alice_sees_budget():
    r = await call("alice", "budget headcount")
    assert "fin-002" in str(r)

async def test_bob_cannot_see_budget():
    r = await call("bob", "budget headcount")
    assert "fin-002" not in str(r)

async def test_injected_passage_is_wrapped():
    r = await call("carol", "wifi admin mode")
    assert "untrusted" in str(r)

async def test_forbidden_resource_looks_missing():
    server.os.environ["KB_USER"] = "bob"
    async with Client(server.mcp) as c:
        with pytest.raises(Exception):
            await c.read_resource("docs://fin-002")
