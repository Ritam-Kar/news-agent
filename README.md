# HN Digest Agent

An AI-powered agent built with Google ADK and Gemini that fetches live Hacker News stories using a custom MCP server and formats them into a concise digest.

## What it does

- Fetches the top 5 trending stories from Hacker News in real time
- Uses the Model Context Protocol (MCP) to connect to the Hacker News Firebase API
- Returns a clean bullet-point digest with title, one-sentence insight, score, author, and comment count
- Responds with a friendly greeting if no news request is made

## Architecture

Two sequential agents run in a pipeline:

1. **HN Fetcher** — uses MCP tools to call `get_top_story_ids` then `get_story_details` for each of the top 5 stories
2. **Digest Writer** — reads the raw story data and formats it into a readable digest using Gemini

### MCP Server

A custom Python MCP server (`hn_mcp_server.py`) exposes two tools over stdio transport:
- `get_top_story_ids` — fetches the current top story IDs from HN
- `get_story_details` — fetches full details for a given story ID

## Tech stack

- [Google ADK](https://github.com/google/adk-python) — agent orchestration
- Gemini 2.5 Flash — AI inference via Vertex AI
- [Model Context Protocol (MCP)](https://modelcontextprotocol.io) — tool connectivity standard
- Hacker News Firebase API — free, no auth required
- Google Cloud Run — serverless deployment
- Docker — containerisation

## Live demo

- Web UI: `https://hn-agent-624320433211.us-central1.run.app/dev-ui/`
- API endpoint: `https://hn-agent-624320433211.us-central1.run.app/run`

## Project structure
```
hn-agent/
├── hn_agent/
│   ├── __init__.py
│   └── agent.py          # Two LlmAgents + SequentialAgent + MCPToolset
├── hn_mcp_server.py      # Custom Python MCP server
├── Dockerfile
├── entrypoint.sh
└── requirements.txt
```

## Running locally

### Prerequisites
- Python 3.11+
- Docker
- Google Cloud account with Vertex AI enabled

### Steps
```bash
# Clone the repo
git clone https://github.com/YOUR_USERNAME/news-agent.git
cd news-agent

# Authenticate with Google Cloud
gcloud auth application-default login

# Build and run
docker build -t hn-agent .

docker run --rm \
  -p 8080:8080 \
  -e GOOGLE_CLOUD_PROJECT=YOUR_PROJECT_ID \
  -e GOOGLE_CLOUD_LOCATION=us-central1 \
  -v ~/.config/gcloud:/root/.config/gcloud \
  hn-agent
```

Open `http://localhost:8080/dev-ui/` in your browser.

## Deploying to Cloud Run
```bash
gcloud builds submit --tag gcr.io/YOUR_PROJECT_ID/hn-agent .

gcloud run deploy hn-agent \
  --image=gcr.io/YOUR_PROJECT_ID/hn-agent \
  --region=us-central1 \
  --allow-unauthenticated \
  --port=8080 \
  --memory=1Gi \
  --timeout=120
```

## Example queries

- "What are people talking about on Hacker News today?"
- "Show me the top tech stories right now"
- "What's trending on HN?"