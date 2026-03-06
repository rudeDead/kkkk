"""
HR Chatbot API Endpoints
Uses OpenRouter API with rule-based local fallback
"""

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from app.core.dependencies import get_current_active_user
from app.config import settings
from datetime import datetime
import httpx
import re
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

# ─────────────────────────────────────────────────────────────────────────────
# SYSTEM PROMPT
# ─────────────────────────────────────────────────────────────────────────────
SYSTEM_PROMPT = """You are QKREW HR Assistant, a helpful AI chatbot for QKREW Software Technologies.

QKREW is a modern software development company with a comprehensive employee management system.

Key Information:
- Company: QKREW Software Technologies
- Hierarchy: L1 (CEO/CTO) → L2 (VP) → L3-L5 (Project Manager) → L6 (Principal Architect) → L7 (Team Lead) → L8-L11 (Senior/Mid Engineers) → L12-L13 (Junior/Intern)
- Leave Types: Casual, Sick, Earned, Maternity, Paternity, Unpaid
- Leave Workflow: Employee → HR Review → L7 Team Lead → L6 Architect (if conflicts detected)
- Software Requests: Employees can request software/tools with business justification
- Notice Period: Employees submit resignation; handover process managed by HR
- Events: Company organizes team building, training, workshops, social events
- Incidents: Critical issues tracked and assigned; block leave if severity is high/critical
- Projects: Managed by PM (L3-L5), Principal Architects (L6), Team Leads (L7)
- ESP: Extra Staffing Projection — AI-driven staffing recommendations

Keep responses concise, friendly, and actionable."""


# ─────────────────────────────────────────────────────────────────────────────
# MODELS (try all free models, no retries per model — just rotate fast)
# ─────────────────────────────────────────────────────────────────────────────
FREE_MODELS = [
    "qwen/qwen3-4b:free",
    "meta-llama/llama-3.2-3b-instruct:free",
    "google/gemma-3-4b-it:free",
    "liquid/lfm-2.5-1.2b-instruct:free",
    "arcee-ai/trinity-mini:free",
    "nvidia/nemotron-nano-9b-v2:free",
    "google/gemma-3n-e2b-it:free",
    "mistralai/mistral-small-3.1-24b-instruct:free",
    "meta-llama/llama-3.3-70b-instruct:free",
]


# ─────────────────────────────────────────────────────────────────────────────
# LOCAL RULE-BASED FALLBACK — always works, no API needed
# ─────────────────────────────────────────────────────────────────────────────
RULES: list[tuple[list[str], str]] = [
    # Leave
    (["leave", "vacation", "time off", "casual", "sick", "earned", "maternity", "paternity", "unpaid"],
     """**Leave Policy at QKREW**

**Types of Leave:**
• Casual Leave — personal/short-term needs
• Sick Leave — illness or medical appointments
• Earned Leave — accrued based on service
• Maternity / Paternity Leave — parental leave
• Unpaid Leave — for personal reasons beyond quota

**How to Apply:**
1. Submit a leave request in the QKREW portal
2. HR reviews and validates your quota
3. Your L7 Team Lead checks for project conflicts (AI-assisted)
4. L6 Architect reviews if conflicts are detected
5. Decision notified to you

**Tips:**
- Apply early for long leaves to allow conflict resolution
- If you own critical tasks, ensure an alternate is assigned
- Leaves blocked if you have unresolved high/critical incidents"""),

    # Incident
    (["incident", "bug", "issue", "critical", "severity", "sla"],
     """**Incident Management at QKREW**

**Severity Levels:** Low → Medium → High → Critical

**How to Report:**
1. Go to Incidents in the sidebar
2. Fill in title, description, project, severity, and assignee

**Important Rules:**
• High/Critical incidents **block leave approvals** for the assignee
• Incidents must be resolved before the assignee can go on leave
• SLA timers track resolution time

**Resolving:**
- Update incident status to "Resolved" with resolution notes
- This automatically unblocks any pending leave requests"""),

    # Software Request
    (["software", "tool", "license", "request", "procurement"],
     """**Software / Tool Requests at QKREW**

**How to Request:**
1. Go to Software Requests in the portal
2. Fill in: tool name, justification, priority, estimated cost
3. Submit — HR and Finance review the request

**Approval Flow:**
Employee → HR Review → Finance/Admin Approval → Procurement

**Tips:**
- Always include a clear business justification
- Mention if the tool is needed for a specific project
- Urgent requests can be flagged as high priority"""),

    # Notice Period
    (["notice", "resign", "resignation", "quit", "exit", "handover"],
     """**Notice Period & Exit Process at QKREW**

**Steps:**
1. Submit your resignation via the Notice Period module
2. HR acknowledges and sets your last working day
3. You complete a structured handover checklist
4. HR conducts an exit interview
5. Final settlement and documentation

**Standard Notice Periods:**
• L8-L13: 30 days
• L6-L7: 45 days
• L3-L5: 60 days
• L1-L2: 90 days

Contact HR directly for early release or negotiated exits."""),

    # Hierarchy / Levels
    (["level", "hierarchy", "l1", "l2", "l3", "l4", "l5", "l6", "l7", "l8", "l9", "l10", "l11", "l12", "l13", "role", "designation"],
     """**QKREW Organizational Hierarchy**

| Level | Role |
|-------|------|
| L1 | CEO / CTO |
| L2 | VP / Director |
| L3–L5 | Project Manager |
| L6 | Principal Architect |
| L7 | Team Lead |
| L8–L9 | Senior Engineer |
| L10–L11 | Mid-level Engineer |
| L12 | Junior Engineer |
| L13 | Intern |

**Key Access Rules:**
• L1-L2 (Admin) — full system access
• L3-L5 (PM) — project & ESP management
• L6-L7 (TL) — team management, leave approvals
• L8+ (Employee) — self-service features"""),

    # ESP
    (["esp", "staffing", "projection", "hiring", "headcount", "resource"],
     """**ESP — Extra Staffing Projection**

ESP is QKREW's AI-driven staffing recommendation system.

**Workflow:**
1. **L7 (Team Lead)** creates a staffing package for a project
2. **L6 (Architect)** runs simulation: analyzes skill gaps, capacity, utilization
3. **PM (L3-L5)** reviews simulation results and approves/rejects positions

**Simulation Shows:**
• Skill coverage before vs. after hiring
• Timeline improvement estimate
• Per-candidate skill match vs. project requirements
• Remaining skill gaps after the hire

**Tips:**
- Tag projects with required skills for accurate matching
- Use the Simulator tab to test different team compositions"""),

    # Events
    (["event", "workshop", "training", "team building", "social"],
     """**Company Events at QKREW**

**Types of Events:**
• Team Building Activities
• Technical Workshops & Training
• Social Events & Celebrations
• All-Hands Meetings

**How to Participate:**
1. Go to Events in the portal
2. Browse upcoming events
3. Register / confirm attendance

**Organizing an Event:**
- Submit event details to HR for approval
- HR coordinates logistics, venue, and participation
- Events appear on the company calendar for all employees"""),

    # Project
    (["project", "task", "assignment", "milestone", "deadline", "progress"],
     """**Project & Task Management at QKREW**

**Projects are managed by:**
• PM (L3-L5) — overall ownership, budget, timeline
• Principal Architect (L6) — technical direction
• Team Lead (L7) — day-to-day team management

**Task Assignment Rules:**
• L6/L7 can assign tasks to L8–L11
• L8 can create learning tasks for L12–L13 only

**Updating Tasks:**
1. Find your task in the Task Board
2. Update progress % and status
3. Setting progress to 100% auto-marks task as "Completed"

**Status Workflow:**
Not Started → In Progress → Blocked → In Review → Completed"""),

    # General greetings
    (["hello", "hi", "hey", "good morning", "good afternoon", "greetings"],
     """Hello! 👋 I'm your **QKREW HR Assistant**.

I can help you with:
• 🏖️ **Leave** — apply, check status, policies
• 🚨 **Incidents** — report, resolve, track
• 💻 **Software Requests** — request tools or licenses
• 📋 **Notice Period** — resignation and exit process
• 🏗️ **Projects & Tasks** — assignments and progress
• 👥 **Hierarchy & Roles** — org structure (L1–L13)
• 🤖 **ESP** — staffing projections and simulations
• 🎉 **Events** — company activities and workshops

What can I help you with today?"""),

    # Help
    (["help", "what can you do", "capabilities", "features"],
     """**I can answer questions about:**

✅ Leave policies and how to apply
✅ Incident reporting and severity levels
✅ Software/tool procurement requests
✅ Notice period and resignation process
✅ QKREW hierarchy levels (L1–L13)
✅ Project and task management
✅ ESP (staffing projection) workflow
✅ Company events and workshops

Just type your question and I'll do my best to help!
For complex HR matters, contact HR directly."""),

    # Contact HR
    (["contact", "email", "phone", "hr team", "reach hr"],
     """**Contacting HR at QKREW**

For matters requiring direct HR attention:
• Use the internal QKREW portal messaging
• Raise a query via your Team Lead (L7)
• For urgent matters, escalate to your L6 Architect

The HR team handles:
• Leave quota corrections
• Payroll queries
• Policy clarifications
• Disciplinary matters
• Employee grievances"""),
]


def local_fallback(message: str) -> str:
    """Rule-based HR chatbot — always works, no external API needed."""
    msg = message.lower()

    # Score each rule by keyword hits
    best_score = 0
    best_response = None

    for keywords, response in RULES:
        score = sum(1 for kw in keywords if kw in msg)
        if score > best_score:
            best_score = score
            best_response = response

    if best_response and best_score > 0:
        return best_response

    # Generic fallback
    return (
        "I'm not sure I have specific information about that. "
        "Here are topics I can help with:\n\n"
        "• Leave policies and application\n"
        "• Incident reporting\n"
        "• Software requests\n"
        "• Notice period / resignation\n"
        "• QKREW hierarchy (L1–L13)\n"
        "• Projects and tasks\n"
        "• ESP staffing projections\n"
        "• Company events\n\n"
        "Try rephrasing your question, or contact HR directly for personalised help."
    )


# ─────────────────────────────────────────────────────────────────────────────
# MODELS
# ─────────────────────────────────────────────────────────────────────────────
class ChatMessage(BaseModel):
    message: str


class ChatResponse(BaseModel):
    response: str
    timestamp: str
    source: str = "ai"   # "ai" or "local"


# ─────────────────────────────────────────────────────────────────────────────
# ENDPOINT
# ─────────────────────────────────────────────────────────────────────────────
@router.post("/chat", response_model=ChatResponse)
async def chat_with_bot(
    chat_message: ChatMessage,
    current_user: dict = Depends(get_current_active_user)
):
    """Send message to HR chatbot — tries OpenRouter, falls back to local rules."""

    api_key = settings.OPENROUTER_API_KEY
    payload = {
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user",   "content": chat_message.message},
        ],
        "temperature": 0.7,
        "max_tokens": 500,
    }
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type":  "application/json",
        "HTTP-Referer":  "http://localhost:5173",
        "X-Title":       "QKREW HR Chatbot",
    }

    # ── Try each free model once (no retries — just rotate fast) ─────────
    if api_key:
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                for model in FREE_MODELS:
                    try:
                        resp = await client.post(
                            "https://openrouter.ai/api/v1/chat/completions",
                            headers=headers,
                            json={**payload, "model": model},
                        )
                        logger.info(f"[{model}] → {resp.status_code}")

                        if resp.status_code == 200:
                            data = resp.json()
                            choices = data.get("choices") or []
                            if choices:
                                text = choices[0]["message"]["content"]
                                logger.info(f"[{model}] success ({len(text)} chars)")
                                return ChatResponse(
                                    response=text,
                                    timestamp=datetime.utcnow().isoformat(),
                                    source="ai"
                                )
                        elif resp.status_code == 429:
                            logger.warning(f"[{model}] rate limited — trying next")
                            continue
                        else:
                            logger.warning(f"[{model}] {resp.status_code} — trying next")
                            continue

                    except httpx.TimeoutException:
                        logger.warning(f"[{model}] timeout — trying next")
                        continue

        except Exception as e:
            logger.error(f"OpenRouter connection error: {e}")

    # ── All models failed / no API key → use local rule-based fallback ───
    logger.info("Using local rule-based fallback")
    response_text = local_fallback(chat_message.message)
    return ChatResponse(
        response=response_text,
        timestamp=datetime.utcnow().isoformat(),
        source="local"
    )


@router.get("/chat/history")
async def get_chat_history(
    current_user: dict = Depends(get_current_active_user)
):
    """Get chat history (placeholder)"""
    return {"messages": [], "note": "Chat history not persisted in this version"}
