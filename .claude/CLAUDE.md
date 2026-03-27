# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Setup

```bash
python -m venv venv
source venv/bin/activate        # Linux/Mac
venv\Scripts\activate           # Windows

pip install -r requirements.txt
```

Configure `.env` with credentials before running:
```
CONNECTIONS__SERVICE_CONNECTION__SETTINGS__CLIENTID=<azure-app-client-id>
CONNECTIONS__SERVICE_CONNECTION__SETTINGS__CLIENTSECRET=<azure-app-client-secret>
CONNECTIONS__SERVICE_CONNECTION__SETTINGS__TENANTID=<azure-tenant-id>
CONNECTIONS__SERVICE_CONNECTION__SETTINGS__ANONYMOUS_ALLOWED=true
ANTHROPIC_API_KEY=<anthropic-api-key>
```

## Running

```bash
python -m src.main
```

In a separate terminal run:

```bash
npm install -g @microsoft/teams-app-test-tool
teamsapptester
```

Starts an HTTP server on `localhost:3978` (or `PORT` env var). The agent endpoint is `POST /api/messages`.

## Architecture

This is **DAP (Daily Account Planner)** — a B2B sales assistant built on the Microsoft Agents SDK (Python) that orchestrates three Claude-powered sub-agents via the Anthropic API.

**Two-layer AI architecture:**
1. **Microsoft Agents SDK layer** — handles the Teams/Bot Framework transport (JWT auth, `CloudAdapter`, `AgentApplication`) via `src/agent.py` and `src/start_server.py`
2. **Anthropic Claude layer** — `src/dap_agent.py` runs an agentic loop using `claude-haiku-4-5` that delegates to three sub-agents as tools

**Full request flow:**
```
POST /api/messages
  → JWT auth middleware (start_server.py)
  → CloudAdapter → AgentApplication (agent.py)
  → run_agent() in dap_agent.py
      → Anthropic API (claude-haiku-4-5, up to 10 iterations)
      → sub-agent tools (Account Pulse / Quota Coach / Next Move)
          → each sub-agent runs its own Anthropic agentic loop with domain tools
  → reply sent back via context.send_activity()
```

**Key source files:**
- [src/agent.py](src/agent.py) — Microsoft Agents SDK app (`AGENT_APP`, `ADAPTER`, `CONNECTION_MANAGER`). Maintains conversation history in `TurnState` and calls `run_agent()` on each message.
- [src/dap_agent.py](src/dap_agent.py) — Core agentic loop: sends messages + system prompt to Claude, handles `tool_use` stop reason by executing sub-agent tools asynchronously, loops up to 10 times.
- [src/dap_types.py](src/dap_types.py) — `Message`, `ToolHandler`, and `ToolDefinition` TypedDicts.
- [src/sub_agents/index.py](src/sub_agents/index.py) — Registers the three sub-agents as `ToolDefinition` entries (schema + async handler).
- [src/instructions.md](src/instructions.md) — System prompt for the top-level DAP coordinator agent.

**Sub-agents** (each in `src/sub_agents/<name>/`):
- **Account Pulse** — account health scores and recent activity; tools: `get_account_health`, `get_recent_activity`
- **Quota Coach** — quota attainment and pipeline forecast; tools: `get_quota_status`, `get_pipeline_forecast`
- **Next Move** — open opportunities and recommended actions; tools: `get_open_opportunities`, `get_recommended_actions`

Each sub-agent follows the same pattern: an `instructions.md` system prompt, a `<name>.py` that runs its own `run_agent`-style loop, and tool handlers in `src/tools/<name>_tools.py` that return mock JSON data.

**State:** `MemoryStorage` — ephemeral per-process. Conversation history is stored in `TurnState` under `ConversationState.messages` as a list of `{role, content}` dicts passed to Claude on every turn.

**Adding a new sub-agent:** Create the sub-agent module under `src/sub_agents/`, add its tools under `src/tools/`, register it as a `ToolDefinition` in `src/sub_agents/index.py`, and include it in the `sub_agents` list passed to `run_agent()` in `src/agent.py`.
