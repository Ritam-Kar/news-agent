import asyncio
import json
import httpx
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp import types

server = Server("hn-server")

@server.list_tools()
async def list_tools():
    return [
        types.Tool(
            name="get_top_story_ids",
            description="Returns the top 10 Hacker News story IDs",
            inputSchema={"type": "object", "properties": {}, "required": []}
        ),
        types.Tool(
            name="get_story_details",
            description="Returns details of a specific HN story by its ID",
            inputSchema={
                "type": "object",
                "properties": {
                    "story_id": {"type": "integer", "description": "The HN story ID"}
                },
                "required": ["story_id"]
            }
        )
    ]

@server.call_tool()
async def call_tool(name: str, arguments: dict):
    async with httpx.AsyncClient(timeout=10) as client:
        if name == "get_top_story_ids":
            resp = await client.get(
                "https://hacker-news.firebaseio.com/v0/topstories.json"
            )
            ids = resp.json()[:10]
            return [types.TextContent(type="text", text=json.dumps(ids))]
        elif name == "get_story_details":
            story_id = arguments["story_id"]
            resp = await client.get(
                f"https://hacker-news.firebaseio.com/v0/item/{story_id}.json"
            )
            data = resp.json()
            result = {
                "id": data.get("id"),
                "title": data.get("title", "No title"),
                "url": data.get("url", ""),
                "score": data.get("score", 0),
                "by": data.get("by", "unknown"),
                "descendants": data.get("descendants", 0),
            }
            return [types.TextContent(type="text", text=json.dumps(result))]
        return [types.TextContent(type="text", text="Unknown tool")]

async def main():
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            server.create_initialization_options()
        )

if __name__ == "__main__":
    asyncio.run(main())