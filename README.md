# AI Lead Management Automation — Technical Assessment

## 1. Project Overview

This project demonstrates an AI-powered lead management and automation system integrating:

- **FastAPI** — Backend API and lead management.
- **PostgreSQL/SQLAlchemy** — Lead data persistence and database operations.
- **n8n** — Workflow automation and lead routing.
- **Hermes Agent** — AI agent orchestration.
- **Model Context Protocol (MCP)** — Communication between Hermes and backend tools.
- **Ollama** — Local LLM inference using `llama3.2:3b`.

The system captures incoming leads, analyzes their requirements, classifies them, routes them through automated workflows, and allows Hermes to perform authorized lead-status updates.

## 2. System Architecture

```text
                Incoming Lead
                      |
                      v
                n8n Webhook
                      |
                      v
              FastAPI Backend
                      |
                      v
                Lead Database
                      |
                      v
                 AI Analysis
                      |
                      v
              Lead Classification
                /     |     \
              HOT    WARM   COLD
               |       |      |
               v       v      v
             Action  Follow  Email/
                     Up      Routing

                      |
                      v
                 Hermes Agent
                      |
                      v
                 MCP Client
                      |
                      v
              Lead Management MCP
                      |
             +--------+---------+
             |                  |
             v                  v
         lookup_lead      update_lead_status
             |                  |
             +--------+---------+
                      |
                      v
               FastAPI Backend
                      |
                      v
                 Lead Database
```

## 3. Technology Stack

| Component | Technology |
|---|---|
| Backend | Python, FastAPI |
| Database | SQLAlchemy |
| Workflow automation | n8n |
| AI agent | Hermes Agent |
| Tool integration | MCP |
| LLM runtime | Ollama |
| Model | llama3.2:3b |
| API testing | PowerShell / HTTP requests |

## 4. Main Functionalities

### Lead Management API
- Create and retrieve leads.
- Retrieve individual leads by ID.
- Update lead sales status through authorized endpoints.
- Validate requests and authenticate internal operations.

### n8n Automation
- Receive leads through a webhook.
- Send lead information to the backend.
- Perform AI-based lead analysis.
- Classify leads into HOT, WARM, and COLD categories.
- Route leads through corresponding workflow branches.
- Trigger follow-up actions.

### Hermes and MCP Integration

The MCP server exposes two lead-management tools:

**1. lookup_lead**
- Accepts a lead ID.
- Retrieves lead details from FastAPI.
- Uses authenticated API communication.

**2. update_lead_status**
- Accepts a lead ID and sales status.
- Allows Hermes to set `CONTACTED`.
- Restricts `CONVERTED` and `LOST` to human approval.
- Sends a PATCH request to FastAPI.

## 5. API Endpoints

| Method | Endpoint | Purpose |
|---|---|---|
| GET | `/health` | Backend health check |
| GET | `/api/health/database` | Database health check |
| PATCH | `/internal/leads/{lead_id}/status` | Update lead status |
| GET | `/internal/leads/{lead_id}` | Retrieve lead details |

Internal endpoints require the `X-Hermes-API-Key` authentication header.

## 6. Verification and Test Evidence

The following integration tests were performed.

| Test | Result |
|---|---|
| FastAPI startup | Passed |
| Backend health check | Passed |
| Database connectivity | Passed |
| n8n webhook execution | Passed |
| Lead creation | Passed |
| AI classification and routing | Passed |
| MCP server handshake | Passed |
| MCP tool discovery | Passed |
| Hermes lead lookup | Passed |
| Hermes status update invocation | Passed |
| FastAPI PATCH response | HTTP 200 |
| Independent lead retrieval | Passed |

### Verified execution evidence

Hermes execution log:

```text
agent.tool_executor:
tool mcp__lead_management__update_lead_status
completed (0.51s, 479 chars)
```

MCP server HTTP log:

```text
HTTP Request: PATCH
http://127.0.0.1:8000/internal/leads/2/status
HTTP/1.1 200 OK
```

Independent API verification:

```json
{
  "id": 2,
  "name": "Test Lead",
  "sales_status": "CONTACTED",
  "updated_at": "2026-11-17T20:23:45.758152"
}
```

Note: The lead was already in `CONTACTED` status before the successful PATCH request. The logs prove successful tool execution and HTTP acceptance, but not a transition from another status.

## 7. Security and Authorization

- API authentication uses an environment variable.
- Credentials are not intended to be committed to source control.
- Hermes is authorized to set only `CONTACTED`.
- `CONVERTED` and `LOST` require human approval.
- Internal API requests use an authentication header.
- Lead-status operations are recorded through the backend audit mechanism.

## 8. Local Setup

### Step 1: Activate virtual environment

```powershell
.\venv\Scripts\Activate.ps1
```

### Step 2: Configure environment

Create or update `.env` with the required database configuration and API credentials.

Never commit `.env` to source control.

### Step 3: Start FastAPI

```powershell
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```

### Step 4: Start n8n

Start the configured n8n instance and activate the lead-management workflow.

### Step 5: Configure MCP

Register the `lead-management` MCP server with Hermes and ensure its environment configuration points to the running FastAPI backend.

### Step 6: Verify MCP

```powershell
hermes mcp test lead-management
```

### Step 7: Verify backend

```powershell
Invoke-RestMethod http://127.0.0.1:8000/health
```

## 9. Future Improvements

- Add more advanced lead-scoring models.
- Implement human approval workflows.
- Add role-based access control.
- Improve retry and failure-handling mechanisms.
- Add automated integration tests.
- Implement observability dashboards.
- Add multi-agent orchestration for complex lead-management operations.

## 10. Conclusion

The assessment demonstrates an integrated AI-driven lead-management workflow combining backend development, workflow automation, local LLM inference, agent orchestration, and MCP-based tool execution.

The successful Hermes-to-MCP-to-FastAPI execution confirms that the agent can discover and invoke backend operations through a controlled tool interface, with authorization restrictions enforced by the backend.

**Project status:** Core integration and verification completed.