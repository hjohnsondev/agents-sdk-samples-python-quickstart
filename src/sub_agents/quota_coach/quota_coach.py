from pathlib import Path
from ...dap_agent import run_agent
from ...tools.quota_coach_tools import get_quota_status_tool, get_pipeline_forecast_tool

_system_prompt = (Path(__file__).parent / "instructions.md").read_text(encoding="utf-8")
_tools = [get_quota_status_tool, get_pipeline_forecast_tool]


async def run_quota_coach(query: str) -> str:
    print("[quota-coach] Running subagent...")
    return await run_agent([{"role": "user", "content": query}], _system_prompt, _tools)
