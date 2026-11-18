import json
import os
from pathlib import Path

import httpx
from dotenv import load_dotenv
from mcp.server.mcpserver import MCPServer


# --------------------------------------------------
# Configuration
# --------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parents[1]
load_dotenv(PROJECT_ROOT / ".env")

API_BASE_URL = os.getenv(
    "LEADS_API_BASE_URL",
    "http://127.0.0.1:8000"
).rstrip("/")

HERMES_API_KEY = os.getenv("HERMES_API_KEY")

if not HERMES_API_KEY:
    raise RuntimeError(
        "HERMES_API_KEY is missing from the project .env file"
    )

HEADERS = {
    "X-Hermes-API-Key": HERMES_API_KEY,
    "Content-Type": "application/json",
}

server = MCPServer(
    name="lead-management",
    version="1.0.0",
    instructions=(
        "Use these tools to look up leads and update permitted lead statuses. "
        "Never mark a lead CONVERTED or LOST; those transitions require human approval."
    ),
)


# --------------------------------------------------
# Shared API helper
# --------------------------------------------------

async def call_leads_api(method: str, endpoint: str, payload=None) -> str:
    url = f"{API_BASE_URL}{endpoint}"

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.request(
                method=method,
                url=url,
                headers=HEADERS,
                json=payload,
            )

        try:
            result = response.json()
        except ValueError:
            result = {"response": response.text}

        if not response.is_success:
            return json.dumps(
                {
                    "success": False,
                    "http_status": response.status_code,
                    "error": result,
                },
                ensure_ascii=False,
                indent=2,
            )

        return json.dumps(
            {
                "success": True,
                "data": result,
            },
            ensure_ascii=False,
            indent=2,
        )

    except httpx.RequestError as exc:
        return json.dumps(
            {
                "success": False,
                "error": "Could not connect to the Lead Management API.",
                "details": str(exc),
            },
            ensure_ascii=False,
            indent=2,
        )


# --------------------------------------------------
# MCP Tool 1: Look up a lead
# --------------------------------------------------

@server.tool(
    name="lookup_lead",
    description=(
        "Retrieve a lead by its numeric ID from the Lead Management API. "
        "The lookup is authenticated and recorded in the audit log."
    ),
)
async def lookup_lead(lead_id: int) -> str:
    """Retrieve a lead using its ID."""

    if lead_id <= 0:
        return json.dumps({
            "success": False,
            "error": "lead_id must be a positive integer."
        })

    return await call_leads_api(
        "GET",
        f"/internal/leads/{lead_id}",
    )


# --------------------------------------------------
# MCP Tool 2: Update permitted lead status
# --------------------------------------------------

@server.tool(
    name="update_lead_status",
    description=(
        "Update a lead's sales status. Hermes is only authorized to set "
        "CONTACTED. CONVERTED and LOST require human approval."
    ),
)
async def update_lead_status(
    lead_id: int,
    sales_status: str,
) -> str:
    """Update a lead status within Hermes permissions."""

    if lead_id <= 0:
        return json.dumps({
            "success": False,
            "error": "lead_id must be a positive integer."
        })

    if sales_status != "CONTACTED":
        return json.dumps({
            "success": False,
            "error": (
                "Permission denied. Hermes can only set CONTACTED. "
                "CONVERTED and LOST require human approval."
            ),
        })

    return await call_leads_api(
        "PATCH",
        f"/internal/leads/{lead_id}/status",
        payload={"sales_status": sales_status},
    )


# --------------------------------------------------
# Start MCP server over stdio
# --------------------------------------------------

if __name__ == "__main__":
    server.run(transport="stdio")
