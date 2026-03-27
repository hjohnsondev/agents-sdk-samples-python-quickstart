# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

import sys
import traceback
from pathlib import Path
from dotenv import load_dotenv
import asyncio
from microsoft_agents.activity import Activity

load_dotenv()

from os import environ
from microsoft_agents.hosting.aiohttp import CloudAdapter
from microsoft_agents.hosting.core import (
    Authorization,
    AgentApplication,
    TurnState,
    TurnContext,
    MemoryStorage,
)
from microsoft_agents.authentication.msal import MsalConnectionManager
from microsoft_agents.activity import load_configuration_from_env

from .dap_agent import run_agent
from .sub_agents.index import sub_agents
agents_sdk_config = load_configuration_from_env(environ)

STORAGE = MemoryStorage()
CONNECTION_MANAGER = MsalConnectionManager(**agents_sdk_config)
ADAPTER = CloudAdapter(connection_manager=CONNECTION_MANAGER)
AUTHORIZATION = Authorization(STORAGE, CONNECTION_MANAGER, **agents_sdk_config)

AGENT_APP = AgentApplication[TurnState](
    storage=STORAGE, adapter=ADAPTER, authorization=AUTHORIZATION, **agents_sdk_config
)

_DAP_SYSTEM_PROMPT = (Path(__file__).parent / "instructions.md").read_text(encoding="utf-8")

# Welcome message when a user is added to the conversation
@AGENT_APP.conversation_update("membersAdded")
async def on_members_added(context: TurnContext, _state: TurnState):
    await context.send_activity(
        "Welcome to DAP — your Daily Account Planner! "
        "Try asking: 'Give me my daily brief' or 'Where do I stand on quota?'"
    )
    return True

# Message handler for incoming messages
@AGENT_APP.activity("message")
async def on_message(context: TurnContext, state: TurnState):
    # Ignore non-text activities (attachments, adaptive card submits, etc.)
    if not context.activity.text:
        return

    # Send typing indicator immediately (awaited so it arrives before the LLM call starts).
    await context.send_activity(Activity(type="typing"))

    # Background loop refreshes the "..." animation every ~4s (it times out after ~5s).
    async def _typing_loop():
        try:
            while True:
                await asyncio.sleep(4)
                await context.send_activity(Activity(type="typing"))
        except asyncio.CancelledError:
            pass  # Expected on cancel.

    typing_task = asyncio.create_task(_typing_loop())
    try:
        # Amend conversation history with the latest user message, then call the agent to get a response.
        history: list = state.get_value("ConversationState.messages") or []
        history.append({"role": "user", "content": context.activity.text})

        reply = await run_agent(history, _DAP_SYSTEM_PROMPT, sub_agents, context)

        history.append({"role": "assistant", "content": reply})
        state.set_value("ConversationState.messages", history)

        await context.send_activity(reply)
    finally:
        typing_task.cancel()
        try:
            await typing_task
        except asyncio.CancelledError:
            pass

# Global error handler for unhandled exceptions during turn processing
@AGENT_APP.error
async def on_error(context: TurnContext, error: Exception):
    print(f"\n [on_turn_error] unhandled error: {error}", file=sys.stderr)
    traceback.print_exc()
    await context.send_activity("The bot encountered an error or bug.")