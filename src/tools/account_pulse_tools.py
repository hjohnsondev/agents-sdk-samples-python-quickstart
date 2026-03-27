import json

_accounts = {
    "Acme Corp": {"health_score": 42, "last_contact": "2026-03-10", "engagement": "Low", "mrr": 12000},
    "Globex Industries": {"health_score": 78, "last_contact": "2026-03-22", "engagement": "High", "mrr": 45000},
    "Umbrella Ltd": {"health_score": 29, "last_contact": "2026-02-28", "engagement": "Critical", "mrr": 31000},
}

_activity = {
    "Acme Corp": [
        "2026-03-10 — Email opened (product update)",
        "2026-02-20 — Last call with VP of Ops (no follow-up scheduled)",
    ],
    "Globex Industries": [
        "2026-03-22 — Discovery call with new champion (Sarah Kim)",
        "2026-03-19 — Executive Business Review — positive feedback",
    ],
    "Umbrella Ltd": [
        "2026-02-28 — Voicemail, no callback",
        "2026-02-10 — Login activity dropped 80% MoM",
        "2026-01-30 — NPS score: 4 (detractor)",
    ],
}


async def _get_account_health(inputs: dict) -> str:
    name = inputs.get("account_name", "")
    if name.lower() == "all":
        return json.dumps(_accounts, indent=2)
    data = _accounts.get(name)
    if not data:
        return f"Account not found. Available: {', '.join(_accounts)}"
    return json.dumps({"account_name": name, **data}, indent=2)


async def _get_recent_activity(inputs: dict) -> str:
    name = inputs.get("account_name", "")
    activity = _activity.get(name)
    if not activity:
        return f"No activity found. Available: {', '.join(_activity)}"
    return json.dumps({"account_name": name, "recent_activity": activity}, indent=2)


get_account_health_tool = {
    "schema": {
        "name": "get_account_health",
        "description": "Retrieve health score, last contact, engagement level, and MRR for an account.",
        "input_schema": {
            "type": "object",
            "properties": {
                "account_name": {
                    "type": "string",
                    "description": "Account name, or 'all' to retrieve all accounts.",
                }
            },
            "required": ["account_name"],
        },
    },
    "handler": _get_account_health,
}

get_recent_activity_tool = {
    "schema": {
        "name": "get_recent_activity",
        "description": "Retrieve recent activity log (calls, emails, meetings) for an account.",
        "input_schema": {
            "type": "object",
            "properties": {
                "account_name": {
                    "type": "string",
                    "description": "The account name to retrieve activity for.",
                }
            },
            "required": ["account_name"],
        },
    },
    "handler": _get_recent_activity,
}
