import os
import sys
from google.adk.agents import LlmAgent, SequentialAgent
from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset, StdioServerParameters

os.environ["GOOGLE_GENAI_USE_VERTEXAI"] = "true"
os.environ["GOOGLE_CLOUD_PROJECT"] = "history-agent"
os.environ["GOOGLE_CLOUD_LOCATION"] = "us-central1"

fetch_toolset = MCPToolset(
    connection_params=StdioServerParameters(
        command=sys.executable,
        args=["/app/hn_mcp_server.py"],
    )
)

fetcher_agent = LlmAgent(
    name="hn_fetcher",
    model="gemini-2.5-flash",
    description="Fetches top Hacker News stories using the MCP tools.",
    instruction="""
You are a data fetcher. Use the available MCP tools to collect HN stories.

If the user sends a greeting or general message with no request for news,
respond with exactly this JSON and nothing else:
{"no_request": true}

Otherwise follow these steps:

Step 1: Call get_top_story_ids to get the list of top story IDs.
Step 2: Take the FIRST 5 IDs from that list.
Step 3: For each of the 5 IDs, call get_story_details with that ID.
Step 4: Output all the raw data as plain text.
""",
    tools=[fetch_toolset],
    output_key="raw_stories",
)

digest_agent = LlmAgent(
    name="hn_digest",
    model="gemini-2.5-flash",
    description="Formats raw HN data into a clean bullet point digest.",
    instruction="""
You are Chronicle, a friendly tech news editor.

The previous step returned this:
{raw_stories}

If it contains "no_request": true, respond warmly:
"Hi! I am Chronicle, your Hacker News digest agent. Ask me what is happening
on Hacker News today and I will fetch the top 5 trending stories for you!"

Otherwise format the data using EXACTLY this structure:

Today's top Hacker News stories:

- [Title] — [One sentence on why it's interesting]
  Score: X | By: username | Comments: X

Do this for all 5 stories. Nothing else.
""",
)

root_agent = SequentialAgent(
    name="hn_agent",
    description="Fetches and summarises top Hacker News stories.",
    sub_agents=[fetcher_agent, digest_agent],
)