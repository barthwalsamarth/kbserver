# Enterprise Knowledge MCP Server

A permission-aware knowledge-base server built with the Model Context Protocol (Python SDK v2).

- `search_docs` tool: ranked passages with source ids and citations
- Authorization happens before ranking, so unreadable documents never leak
- Retrieved text is wrapped as untrusted data, and likely prompt injections are flagged
- Resources: `docs://{doc_id}` and `docs://{doc_id}/sections/{n}`
- Prompt: `answer_with_citations`

## Run
    pip install -r requirements.txt
    python -m unittest discover -s tests -p test_core.py
    pytest tests/test_server.py
    KB_USER=alice python server.py

Tested with Gemini CLI as the client.
