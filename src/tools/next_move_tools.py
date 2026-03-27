import json

_opportunities = [
    {
        "id": "OPP-001",
        "account": "Globex Industries",
        "title": "Platform Expansion — Sales Ops Suite",
        "stage": "Negotiation",
        "amount": 55000,
        "close_date": "2026-03-28",
        "days_until_close": 4,
        "next_step": "Send redlined MSA back to Sarah Kim",
        "risk_flag": None,
    },
    {
        "id": "OPP-002",
        "account": "Umbrella Ltd",
        "title": "Annual Renewal",
        "stage": "Proposal Sent",
        "amount": 31000,
        "close_date": "2026-03-31",
        "days_until_close": 7,
        "next_step": "No response in 6 days — escalate to exec sponsor",
        "risk_flag": "Account health critical — churn risk",
    },
    {
        "id": "OPP-003",
        "account": "Acme Corp",
        "title": "Renewal",
        "stage": "Proposal Sent",
        "amount": 18000,
        "close_date": "2026-03-31",
        "days_until_close": 7,
        "next_step": "Follow up — no reply to proposal",
        "risk_flag": None,
    },
]

_recommended_actions = [
    {
        "priority": 1,
        "action": "Close OPP-001 (Globex)",
        "detail": "Send redlined MSA to Sarah Kim today. $55K is your biggest path to quota this week.",
        "urgency": "High",
    },
    {
        "priority": 2,
        "action": "Rescue OPP-002 (Umbrella renewal)",
        "detail": "Health score is 29 and NPS is 4. Reach out to VP directly before pushing the renewal.",
        "urgency": "High",
    },
    {
        "priority": 3,
        "action": "Follow up with Acme Corp (OPP-003)",
        "detail": "Proposal sent — no reply. Quick call to procurement could unlock $18K this quarter.",
        "urgency": "Medium",
    },
]


async def _get_open_opportunities(inputs: dict) -> str:
    filter_stage = inputs.get("filter_stage")
    opps = _opportunities
    if filter_stage:
        opps = [o for o in opps if o["stage"].lower() == filter_stage.lower()]
    return json.dumps(opps, indent=2)


async def _get_recommended_actions(_inputs: dict) -> str:
    return json.dumps(_recommended_actions, indent=2)


get_open_opportunities_tool = {
    "schema": {
        "name": "get_open_opportunities",
        "description": "Retrieve open pipeline opportunities with stage, amount, close date, and risk flags.",
        "input_schema": {
            "type": "object",
            "properties": {
                "filter_stage": {
                    "type": "string",
                    "description": "Optional: filter by stage (e.g. 'Negotiation'). Omit for all.",
                }
            },
        },
    },
    "handler": _get_open_opportunities,
}

get_recommended_actions_tool = {
    "schema": {
        "name": "get_recommended_actions",
        "description": "Retrieve a prioritized list of recommended actions for today.",
        "input_schema": {"type": "object", "properties": {}},
    },
    "handler": _get_recommended_actions,
}
