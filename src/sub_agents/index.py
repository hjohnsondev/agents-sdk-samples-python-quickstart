from ..dap_types import ToolDefinition
from .account_pulse.account_pulse import run_account_pulse
from .quota_coach.quota_coach import run_quota_coach
from .next_move.next_move import run_next_move


async def _invoke_account_pulse(inputs: dict) -> str:
    return await run_account_pulse(inputs["query"])


async def _invoke_quota_coach(inputs: dict) -> str:
    return await run_quota_coach(inputs["query"])


async def _invoke_next_move(inputs: dict) -> str:
    return await run_next_move(inputs["query"])


sub_agents: list[ToolDefinition] = [
    {
        "schema": {
            "name": "invoke_account_pulse",
            "description": (
                "Delegate to Account Pulse. Use to analyze account health, "
                "engagement signals, and recent activity."
            ),
            "input_schema": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "The question to send to Account Pulse.",
                    }
                },
                "required": ["query"],
            },
        },
        "handler": _invoke_account_pulse,
    },
    {
        "schema": {
            "name": "invoke_quota_coach",
            "description": (
                "Delegate to Quota Coach. Use to retrieve quota attainment, "
                "pipeline coverage, and revenue forecasting."
            ),
            "input_schema": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "The question to send to Quota Coach.",
                    }
                },
                "required": ["query"],
            },
        },
        "handler": _invoke_quota_coach,
    },
    {
        "schema": {
            "name": "invoke_next_move",
            "description": (
                "Delegate to Next Move. Use to get prioritized action "
                "recommendations and deal-specific next steps."
            ),
            "input_schema": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "The question to send to Next Move.",
                    }
                },
                "required": ["query"],
            },
        },
        "handler": _invoke_next_move,
    },
]
