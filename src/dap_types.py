from typing import Any, Callable, Coroutine, TypedDict


# A single turn in conversation history (matches Anthropic SDK MessageParam)
Message = dict

# An async function that takes a dict of inputs and returns a string
ToolHandler = Callable[[dict[str, Any]], Coroutine[Any, Any, str]]


class ToolDefinition(TypedDict):
    schema: dict   # Anthropic tool schema: name, description, input_schema
    handler: ToolHandler
