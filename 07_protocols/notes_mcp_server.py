"""A tiny MCP server that manages notes in a JSON file. Any MCP client (Agno, LangGraph, Claude Code, ...) can use it.

Run directly to check it starts:  python notes_mcp_server.py   (it then waits for a client on stdin/stdout)
"""
import json
from datetime import datetime
from pathlib import Path

try:  # mcp 1.x
    from mcp.server.fastmcp import FastMCP as Server
except ImportError:  # mcp 2.x renamed FastMCP to MCPServer
    from mcp.server.mcpserver import MCPServer as Server

NOTES = Path(__file__).parent / "notes.json"
server = Server("notes")


def _load() -> list[dict]:
    return json.loads(NOTES.read_text(encoding="utf-8")) if NOTES.exists() else []


def _save(notes: list[dict]) -> None:
    NOTES.write_text(json.dumps(notes, indent=2), encoding="utf-8")


@server.tool()
def add_note(title: str, text: str, tags: list[str] | None = None) -> str:
    """Save a new note with a title, text and optional tags."""
    notes = _load()
    note = {"id": len(notes) + 1, "title": title, "text": text, "tags": tags or [],
            "created": datetime.now().isoformat(timespec="minutes")}
    notes.append(note)
    _save(notes)
    return f"Saved note {note['id']}: {title}"


@server.tool()
def list_notes() -> str:
    """List all notes (id, title, tags)."""
    notes = _load()
    return "\n".join(f"{n['id']}. {n['title']} {n['tags']}" for n in notes) or "No notes yet."


@server.tool()
def search_notes(query: str) -> str:
    """Find notes whose title, text or tags contain the query (case-insensitive)."""
    q = query.lower()
    hits = [n for n in _load() if q in n["title"].lower() or q in n["text"].lower()
            or any(q in t.lower() for t in n["tags"])]
    return "\n\n".join(f"{n['id']}. {n['title']}\n{n['text']}" for n in hits) or f"No notes match '{query}'."


@server.tool()
def delete_note(note_id: int) -> str:
    """Delete a note by its id."""
    notes = _load()
    kept = [n for n in notes if n["id"] != note_id]
    if len(kept) == len(notes):
        return f"No note with id {note_id}."
    _save(kept)
    return f"Deleted note {note_id}."


if __name__ == "__main__":
    server.run()  # default transport: stdio
