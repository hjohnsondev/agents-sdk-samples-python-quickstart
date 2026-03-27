import json

_quota = {
    "rep_name": "Alex Rivera",
    "period": "Q1 2026",
    "days_remaining": 7,
    "quota_target": 250000,
    "closed_won": 147500,
    "attainment_pct": 59,
    "gap_to_quota": 102500,
    "weighted_forecast": 186000,
}

_pipeline_by_stage = [
    {"stage": "Discovery", "count": 2, "total_value": 48000, "close_probability": 0.15},
    {"stage": "Proposal Sent", "count": 2, "total_value": 52000, "close_probability": 0.55},
    {"stage": "Negotiation", "count": 1, "total_value": 55000, "close_probability": 0.80},
]


async def _get_quota_status(_inputs: dict) -> str:
    return json.dumps(_quota, indent=2)


async def _get_pipeline_forecast(_inputs: dict) -> str:
    total = sum(s["total_value"] for s in _pipeline_by_stage)
    weighted = sum(s["total_value"] * s["close_probability"] for s in _pipeline_by_stage)
    summary = {
        "pipeline_by_stage": _pipeline_by_stage,
        "total_pipeline": total,
        "weighted_forecast": round(weighted),
        "coverage_ratio": round(total / _quota["gap_to_quota"], 2),
    }
    return json.dumps(summary, indent=2)


get_quota_status_tool = {
    "schema": {
        "name": "get_quota_status",
        "description": "Retrieve quota attainment, closed-won total, gap to goal, and days remaining.",
        "input_schema": {"type": "object", "properties": {}},
    },
    "handler": _get_quota_status,
}

get_pipeline_forecast_tool = {
    "schema": {
        "name": "get_pipeline_forecast",
        "description": "Retrieve pipeline breakdown by stage with counts, values, and weighted forecast.",
        "input_schema": {"type": "object", "properties": {}},
    },
    "handler": _get_pipeline_forecast,
}
