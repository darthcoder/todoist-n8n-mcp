#!/usr/bin/env python3
"""
Todoist via n8n — MCP Server
One tool: create_task. Fires an n8n webhook. n8n creates the Todoist task.

Config (env vars):
  N8N_WEBHOOK_URL — required. Set this after configuring your n8n OAuth connection.
"""

import asyncio
import os
import httpx
from mcp.server import Server
from mcp.server.stdio import stdio_server
import mcp.types as types

server = Server("todoist-n8n")

WEBHOOK_URL = os.environ.get("N8N_WEBHOOK_URL", "")


@server.list_tools()
async def list_tools() -> list[types.Tool]:
    return [
        types.Tool(
            name="create_task",
            description=(
                "Create a task in Todoist via n8n. "
                "Use whenever the user asks to add, remember, track, or schedule a task."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "title": {
                        "type": "string",
                        "description": "Task title — concise, actionable.",
                    },
                    "description": {
                        "type": "string",
                        "description": "Optional detail or context for the task.",
                    },
                    "due_date": {
                        "type": "string",
                        "description": (
                            "Optional due date. Natural language OK: "
                            "'today', 'tomorrow', 'next Monday', or ISO date 'YYYY-MM-DD'."
                        ),
                    },
                    "priority": {
                        "type": "integer",
                        "enum": [1, 2, 3, 4],
                        "description": "Priority 1 (urgent) to 4 (normal). Default 4.",
                    },
                },
                "required": ["title"],
            },
        )
    ]


@server.call_tool()
async def call_tool(name: str, arguments: dict | None) -> list[types.TextContent]:
    if name != "create_task":
        return [types.TextContent(type="text", text=f"Unknown tool: {name}")]

    args = arguments or {}
    title = args.get("title", "").strip()
    if not title:
        return [types.TextContent(type="text", text="Error: task title is required.")]

    if not WEBHOOK_URL:
        return [types.TextContent(
            type="text",
            text="Error: N8N_WEBHOOK_URL is not set. Export it before starting the server."
        )]

    payload = {
        "title":       title,
        "description": args.get("description", ""),
        "due_date":    args.get("due_date", ""),
        "priority":    args.get("priority", 4),
    }

    headers = {"Content-Type": "application/json"}

    try:
        async with httpx.AsyncClient(timeout=10) as client:
            response = await client.post(WEBHOOK_URL, json=payload, headers=headers)
            response.raise_for_status()
        return [types.TextContent(
            type="text",
            text=f'Task created: "{title}"'
        )]
    except httpx.HTTPStatusError as e:
        return [types.TextContent(
            type="text",
            text=f"n8n returned HTTP {e.response.status_code}: {e.response.text}"
        )]
    except httpx.RequestError as e:
        return [types.TextContent(
            type="text",
            text=f"Could not reach n8n webhook: {e}"
        )]


async def main():
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            server.create_initialization_options(),
        )


if __name__ == "__main__":
    asyncio.run(main())
