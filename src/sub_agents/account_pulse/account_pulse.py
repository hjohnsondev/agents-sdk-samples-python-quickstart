from pathlib import Path
from ...dap_agent import run_agent
from ...tools.account_pulse_tools import get_account_health_tool, get_recent_activity_tool

_system_prompt = (Path(__file__).parent / "instructions.md").read_text(encoding="utf-8")
_tools = [get_account_health_tool, get_recent_activity_tool]


async def run_account_pulse(query: str) -> str:
    print("[account-pulse] Running subagent...")
    return await run_agent([{"role": "user", "content": query}], _system_prompt, _tools)
