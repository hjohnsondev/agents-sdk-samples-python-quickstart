import asyncio
import anthropic
from microsoft_agents.hosting.core import ( 
    TurnContext,
) 
from .dap_types import Message, ToolDefinition

_client = anthropic.AsyncAnthropic()
MAX_ITERATIONS = 10


async def run_agent(
    conversation_history: list[Message],
    system_prompt: str,
    tools: list[ToolDefinition], 
    context: TurnContext = None,
) -> str:
    messages = list(conversation_history)
    tool_schemas = [t["schema"] for t in tools]
    tool_handlers = {t["schema"]["name"]: t["handler"] for t in tools}

    tool_notified = False
    for iteration in range(1, MAX_ITERATIONS + 1):
        print(f"[dap_agent] Iteration {iteration}")

        response = await _client.messages.create(
            model="claude-haiku-4-5",
            max_tokens=4096,
            system=system_prompt,
            tools=tool_schemas if tool_schemas else anthropic.NOT_GIVEN,
            messages=messages,
        )

        if response.stop_reason == "end_turn":
            for block in response.content:
                if block.type == "text":
                    return block.text
            return "(No text response)"

        if response.stop_reason == "tool_use":
            if context and not tool_notified:
                await context.send_activity("I need to use a tool to answer your question...")
                tool_notified = True

            tool_use_blocks = [b for b in response.content if b.type == "tool_use"]
            tool_names = [b.name for b in tool_use_blocks]
            print(f"[dap_agent] Tool calls: {', '.join(tool_names)}")

            messages.append({
                "role": "assistant",
                "content": [b.model_dump() for b in response.content],
            })

            async def call_tool(block):
                handler = tool_handlers.get(block.name)
                if not handler:
                    raise ValueError(f'Unknown tool: "{block.name}"')
                output = await handler(block.input)
                return {"id": block.id, "output": output}

            results = await asyncio.gather(*[call_tool(b) for b in tool_use_blocks])

            messages.append({
                "role": "user",
                "content": [
                    {
                        "type": "tool_result",
                        "tool_use_id": r["id"],
                        "content": r["output"],
                    }
                    for r in results
                ],
            })
            continue

        # Fallback for unexpected stop reasons
        for block in response.content:
            if block.type == "text":
                return block.text
        return f"(Stopped: {response.stop_reason})"

    raise RuntimeError(f"Agent exceeded {MAX_ITERATIONS} iterations")
