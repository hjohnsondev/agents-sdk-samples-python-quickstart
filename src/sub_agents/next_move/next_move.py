from pathlib import Path
from ...dap_agent import run_agent
from ...tools.next_move_tools import get_open_opportunities_tool, get_recommended_actions_tool

_system_prompt = (Path(__file__).parent / "instructions.md").read_text(encoding="utf-8")
_tools = [get_open_opportunities_tool, get_recommended_actions_tool]


async def run_next_move(query: str) -> str:
    print("[next-move] Running subagent...")
    return await run_agent([{"role": "user", "content": query}], _system_prompt, _tools)
