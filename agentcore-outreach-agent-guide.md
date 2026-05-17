# LangGraph + AWS AgentCore: Startup Founder Outreach Agent
### End-to-End Build & Deploy Guide

> **What you'll build:** An AI agent that finds US startup founders in any niche, researches their company, drafts a hyper-personalized cold email, and sends it — all from a single prompt. Deployed on AWS AgentCore.

---

## Why NOT LinkedIn Easy Apply

LinkedIn's ToS explicitly bans automation bots. In 2025 they banned Apollo.io and Seamless.ai overnight — permanent account loss. You're actively job hunting. Don't risk it.

**What this agent does instead is better:**
- Easy Apply = you + 400 others clicking the same button
- Cold email to a founder = almost nobody does this → you stand out massively
- A well-researched, personalized 5-line email to 20 founders beats 100 Easy Applies

---

## Architecture

```
User Prompt: "Find AI/robotics startups in SF that raised Series A in 2024,
              email founders about a GenAI engineer role"
        ↓
LangGraph ReAct Agent
        ↓
   ┌────┴─────────────────────────────────────┐
   │                                          │
search_web()              find_email()        send_email()
(Tavily - free)      (Hunter.io - free)   (Gmail SMTP - free)
   │                                          │
   └────────────────┬─────────────────────────┘
                    ↓
           log_outreach() → outreach_log.json
                    ↓
         AgentCore Runtime (AWS)
```

**Cost per agent run: ~$0.001** (just Bedrock Haiku tokens)

---

## Prerequisites Checklist

- [ ] AWS account + credentials configured (`aws configure`)
- [ ] Python 3.10+
- [ ] Bedrock model access: enable `Claude Haiku 4.5` in AWS Console → Bedrock → Model Access (region: us-west-2)
- [ ] Tavily API key (free) → sign up at https://app.tavily.com → copy your API key
- [ ] Hunter.io API key (free, 25 email searches/month) → sign up at https://hunter.io → API tab
- [ ] Gmail account → enable 2FA → create App Password at https://myaccount.google.com/apppasswords

---

## STEP 1 — Project Setup

```bash
mkdir founder-outreach-agent
cd founder-outreach-agent
python3 -m venv .venv
# macOS / Linux:
source .venv/bin/activate
# Windows PowerShell:
.\.venv\Scripts\Activate.ps1
# Windows CMD:
.\.venv\Scripts\activate.bat
pip install --upgrade pip
```

Install dependencies:

```bash
pip install \
  langgraph \
  langchain-aws \
  langchain-community \
  tavily-python \
  requests \
  bedrock-agentcore \
  bedrock-agentcore-starter-toolkit \
  boto3
```

Create `requirements.txt`:

```
langgraph
langchain-aws
langchain-community
tavily-python
requests
bedrock-agentcore
boto3
```

Create `.env` for your secrets:

```bash
# .env  ← NEVER commit this to git
TAVILY_API_KEY=tvly-xxxxxxxxxxxxxxxx
HUNTER_API_KEY=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
GMAIL_ADDRESS=youremail@gmail.com
GMAIL_APP_PASSWORD=xxxx xxxx xxxx xxxx    # the 16-char app password
YOUR_NAME=Kiki
YOUR_ROLE=GenAI Solutions Engineer
YOUR_LINKEDIN=https://linkedin.com/in/yourprofile
YOUR_GITHUB=https://github.com/yourusername
```

> Note: `agentcore_env.sh` is a Bash script. On Windows PowerShell, do not run `source agentcore_env.sh` directly. Instead either:
> - use `bash .\agentcore_env.sh` from Git Bash / WSL, or
> - create a `.env` file and let `python-dotenv` load it, or
> - set environment vars in PowerShell with `$env:NAME="value"`.

---

## STEP 2 — Build the Agent Tools

Create `tools.py`:

```python
# tools.py  — all the tools the agent can use

import os
import json
import smtplib
import requests
from datetime import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from langchain_core.tools import tool
from tavily import TavilyClient


# ─── Load config from environment ────────────────────────────────────────────

def get_env(key: str) -> str:
    val = os.environ.get(key, "")
    if not val:
        raise EnvironmentError(f"Missing env var: {key}")
    return val


# ─── Tool 1: Web Search (Tavily — free tier: 1000 searches/month) ────────────

@tool
def search_web(query: str) -> str:
    """
    Search the web for any information. Use this to:
    - Find startup companies in a niche ("AI robotics startups San Francisco 2024")
    - Find a founder's name ("CEO founder of <company>")
    - Research a company before writing an email ("what does <company> do")
    - Find someone's email or contact info ("john smith acme corp email")
    Returns top 5 results as text.
    """
    try:
        client = TavilyClient(api_key=get_env("TAVILY_API_KEY"))
        response = client.search(
            query=query,
            max_results=5,
            search_depth="basic"   # use "advanced" for deeper research (costs 2 credits)
        )
        results = []
        for r in response.get("results", []):
            results.append(f"SOURCE: {r['url']}\nTITLE: {r['title']}\n{r['content'][:400]}\n")
        return "\n---\n".join(results) if results else "No results found."
    except Exception as e:
        return f"Search error: {str(e)}"


# ─── Tool 2: Find Email via Hunter.io (free: 25 searches/month) ──────────────

@tool
def find_email(full_name: str, company_domain: str) -> str:
    """
    Find a professional's email address given their full name and company domain.
    Args:
        full_name: e.g. "John Smith"
        company_domain: e.g. "acmecorp.com" (just the domain, no https://)
    Returns the email if found, or a suggested pattern to try.
    """
    try:
        api_key = get_env("HUNTER_API_KEY")
        first, *rest = full_name.strip().split()
        last = rest[-1] if rest else ""

        # Hunter.io email finder endpoint
        url = "https://api.hunter.io/v2/email-finder"
        params = {
            "domain": company_domain,
            "first_name": first,
            "last_name": last,
            "api_key": api_key,
        }
        resp = requests.get(url, params=params, timeout=10)
        data = resp.json()

        if data.get("data", {}).get("email"):
            email = data["data"]["email"]
            score = data["data"].get("score", "?")
            return f"Found: {email} (confidence: {score}/100)"
        else:
            # Fallback: guess common patterns
            first_lower = first.lower()
            last_lower = last.lower() if last else ""
            guesses = [
                f"{first_lower}@{company_domain}",
                f"{first_lower}.{last_lower}@{company_domain}",
                f"{first_lower[0]}{last_lower}@{company_domain}",
            ]
            return f"Email not found via Hunter. Common patterns to try:\n" + "\n".join(guesses)

    except Exception as e:
        return f"Email lookup error: {str(e)}"


# ─── Tool 3: Send Email via Gmail SMTP (completely free) ─────────────────────

@tool
def send_email(to_email: str, subject: str, body: str) -> str:
    """
    Send a cold outreach email from your Gmail account.
    Args:
        to_email: recipient's email address
        subject: email subject line
        body: full email body (plain text, keep it under 200 words)
    Returns success confirmation or error message.
    """
    try:
        gmail = get_env("GMAIL_ADDRESS")
        password = get_env("GMAIL_APP_PASSWORD")

        msg = MIMEMultipart("alternative")
        msg["From"] = gmail
        msg["To"] = to_email
        msg["Subject"] = subject
        msg.attach(MIMEText(body, "plain"))

        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(gmail, password)
            server.sendmail(gmail, to_email, msg.as_string())

        # Log the sent email
        log_outreach.invoke({
            "to_email": to_email,
            "subject": subject,
            "body_preview": body[:200],
            "status": "sent"
        })

        return f"✅ Email sent to {to_email}"

    except Exception as e:
        return f"❌ Email send failed: {str(e)}"


# ─── Tool 4: Log Outreach (free — writes to local JSON) ──────────────────────

@tool
def log_outreach(to_email: str, subject: str, body_preview: str, status: str = "sent") -> str:
    """
    Log an outreach attempt to outreach_log.json for tracking.
    Always call this after sending or attempting to send an email.
    Args:
        to_email: who you emailed
        subject: email subject
        body_preview: first 200 chars of the body
        status: "sent", "failed", or "skipped"
    """
    log_file = "outreach_log.json"
    entry = {
        "timestamp": datetime.utcnow().isoformat(),
        "to": to_email,
        "subject": subject,
        "preview": body_preview,
        "status": status,
    }
    try:
        existing = []
        if os.path.exists(log_file):
            with open(log_file, "r") as f:
                existing = json.load(f)
        existing.append(entry)
        with open(log_file, "w") as f:
            json.dump(existing, f, indent=2)
        return f"Logged: {to_email} ({status})"
    except Exception as e:
        return f"Log error: {str(e)}"


# ─── Tool 5: Get Outreach Log ─────────────────────────────────────────────────

@tool
def get_outreach_log() -> str:
    """
    Read the outreach log to see who you've already emailed.
    Use this to avoid emailing the same person twice.
    """
    log_file = "outreach_log.json"
    if not os.path.exists(log_file):
        return "No emails sent yet."
    with open(log_file, "r") as f:
        data = json.load(f)
    if not data:
        return "Log is empty."
    lines = [f"- {e['to']} | {e['subject']} | {e['status']} | {e['timestamp'][:10]}"
             for e in data[-20:]]  # last 20
    return f"Last {len(lines)} outreach entries:\n" + "\n".join(lines)
```

---

## STEP 3 — Build the LangGraph Agent

Create `agent.py`:

```python
# agent.py  — pure LangGraph, no AgentCore yet

import os
from dotenv import load_dotenv
load_dotenv()

from langchain_aws import ChatBedrockConverse
from langchain_core.messages import HumanMessage, SystemMessage
from langgraph.prebuilt import create_react_agent
from tools import search_web, find_email, send_email, log_outreach, get_outreach_log


# ─── System Prompt — this defines the agent's personality and strategy ────────

SYSTEM_PROMPT = f"""You are a smart outreach agent helping {os.environ.get('YOUR_NAME', 'a developer')} find job opportunities and connect with startup founders.

Your goal: Find relevant people, research them, draft personalized cold emails, and send them.

PROFILE OF THE PERSON YOU REPRESENT:
- Name: {os.environ.get('YOUR_NAME', 'Developer')}
- Role: {os.environ.get('YOUR_ROLE', 'Software Engineer')}
- LinkedIn: {os.environ.get('YOUR_LINKEDIN', '')}
- GitHub: {os.environ.get('YOUR_GITHUB', '')}
- Background: CSE graduate (AI & Robotics specialization), experienced in LangGraph, AWS, Python, C++, GenAI agents

OUTREACH STRATEGY:
1. First, check the outreach log (get_outreach_log) to avoid duplicates
2. Search for companies/founders using search_web
3. For each target: search for their name and role first
4. Find their email using find_email
5. Research the company (1-2 quick searches) — what they build, recent news
6. Draft a SHORT, personalized email (5-7 lines max):
   - Line 1: specific reference to their company/product (shows you researched)
   - Line 2-3: why you're relevant (1-2 concrete things you've built)
   - Line 4: the ask (15-min call or reply about opportunities)
   - Sign off with name + LinkedIn
7. Send the email using send_email
8. Log it using log_outreach

EMAIL TONE RULES:
- Never say "I hope this email finds you well"
- Never send generic spam — if you can't personalize it, skip that person
- Keep it under 120 words
- Sound like a smart engineer, not a sales rep
- One specific compliment about their work > three generic sentences

WHEN TO SKIP:
- If the email address is not found with reasonable confidence, skip (don't guess)
- If already emailed them (check log), skip
- If the company seems irrelevant, skip and move to the next one
"""


# ─── LLM + Agent ──────────────────────────────────────────────────────────────

llm = ChatBedrockConverse(
    model="anthropic.claude-haiku-4-5",
    region_name="us-west-2",
    temperature=0.3,   # lower = more consistent, less hallucination on facts
    max_tokens=2048,
)

tools = [search_web, find_email, send_email, log_outreach, get_outreach_log]
graph = create_react_agent(llm, tools=tools, prompt=SYSTEM_PROMPT)


def run_agent(user_message: str) -> str:
    """Run the agent and return the final response."""
    result = graph.invoke({
        "messages": [HumanMessage(content=user_message)]
    })
    return result["messages"][-1].content


# ─── Test it locally ──────────────────────────────────────────────────────────

if __name__ == "__main__":
    # Start with a safe test that doesn't actually send emails
    test = """
    Find 3 AI or robotics startups in San Francisco that raised funding in 2023 or 2024.
    For each one, just research them and tell me:
    1. Company name and what they do
    2. Founder name (if findable)
    3. Whether they might be hiring GenAI engineers
    
    DO NOT send any emails yet — just research and report back.
    """
    print("🔍 Running research-only test...")
    print(run_agent(test))
```

### 3.1 Test it — research only (safe, no emails sent)

```bash
python agent.py
```

You should see the agent making tool calls to Tavily, searching for companies, and returning a structured report. This confirms your tools are working before you send any real emails.

---

## STEP 4 — Test with Real Outreach (Optional Before Deploy)

Once research works, test a real single-email run:

```python
# run_local_test.py — test with one real email to yourself first
import os
from dotenv import load_dotenv
load_dotenv()
from agent import run_agent

# Step 1: Send test email to yourself
result = run_agent(f"""
Send a test email to {os.environ.get('GMAIL_ADDRESS')} with subject "Agent test" 
and body "This is a test from my outreach agent. If you're reading this, 
tools are working correctly!"
""")
print(result)
```

```bash
python run_local_test.py
```

Check your Gmail. If the email arrives — your pipeline is end-to-end working. ✅

---

## STEP 5 — Wrap With AgentCore

Create `main.py`:

```python
# main.py  — AgentCore entrypoint (what AWS deploys)

import os
from dotenv import load_dotenv
load_dotenv()

from bedrock_agentcore import BedrockAgentCoreApp
from langchain_aws import ChatBedrockConverse
from langchain_core.messages import HumanMessage
from langgraph.prebuilt import create_react_agent
from tools import search_web, find_email, send_email, log_outreach, get_outreach_log

# ─── Same agent setup as agent.py ────────────────────────────────────────────

YOUR_NAME = os.environ.get("YOUR_NAME", "Developer")
YOUR_ROLE = os.environ.get("YOUR_ROLE", "Software Engineer")
YOUR_LINKEDIN = os.environ.get("YOUR_LINKEDIN", "")
YOUR_GITHUB = os.environ.get("YOUR_GITHUB", "")

SYSTEM_PROMPT = f"""You are a smart outreach agent helping {YOUR_NAME} find job opportunities and connect with startup founders.

Your goal: Find relevant people, research them, draft personalized cold emails, and send them.

PROFILE:
- Name: {YOUR_NAME}
- Role: {YOUR_ROLE}  
- LinkedIn: {YOUR_LINKEDIN}
- GitHub: {YOUR_GITHUB}
- Background: CSE graduate (AI & Robotics), experienced in LangGraph, AWS, Python, C++, GenAI agents

OUTREACH RULES:
1. Check get_outreach_log first to avoid duplicates
2. Research companies with search_web (2-3 searches per company)
3. Find emails with find_email
4. Draft short personalized emails (max 120 words):
   - Specific reference to their product/company
   - 1-2 concrete things you've built (mention papers, LangGraph projects, AWS work)
   - Clear ask: 15-min call or reply about opportunities
5. Send with send_email, log with log_outreach
6. Skip anyone you can't personalize for or whose email you can't find confidently

EMAIL RULES:
- No "I hope this finds you well"
- Under 120 words
- One specific compliment > three generic sentences
- Sound like an engineer, not a sales rep
"""

llm = ChatBedrockConverse(
    model="anthropic.claude-haiku-4-5",
    region_name="us-west-2",
    temperature=0.3,
    max_tokens=2048,
)

tools = [search_web, find_email, send_email, log_outreach, get_outreach_log]
graph = create_react_agent(llm, tools=tools, prompt=SYSTEM_PROMPT)


# ─── AgentCore wrapper ────────────────────────────────────────────────────────

app = BedrockAgentCoreApp()

@app.entrypoint
def invoke(payload: dict, context=None) -> dict:
    """
    Payload keys:
      - prompt (str): what you want the agent to do
      - dry_run (bool): if true, research only — don't send emails
    """
    prompt = payload.get("prompt", "")
    dry_run = payload.get("dry_run", False)

    if not prompt:
        return {"error": "Missing 'prompt' in payload"}

    # Safety gate: append no-send instruction if dry_run
    if dry_run:
        prompt += "\n\nIMPORTANT: This is a DRY RUN. Research and draft emails but DO NOT call send_email. Just show me the drafted emails."

    result = graph.invoke({"messages": [HumanMessage(content=prompt)]})
    return {"response": result["messages"][-1].content}


if __name__ == "__main__":
    app.run()   # local server on port 8080
```

---

## STEP 6 — Test the Entrypoint Locally

Terminal 1:
```bash
python main.py
```

Terminal 2:
```bash
# Dry run — research only, no emails sent
curl -X POST http://localhost:8080/invocations \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Find 3 AI startup founders in San Francisco who raised Series A in 2024. Research each company.",
    "dry_run": true
  }'

# Real run — finds and emails founders
curl -X POST http://localhost:8080/invocations \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Find 2 robotics or AI startups in the US that are likely hiring engineers. Email their founders about my GenAI background.",
    "dry_run": false
  }'
```

Stop with Ctrl+C when done. ✅

---

## STEP 7 — Handle Secrets for AWS Deployment

Your env vars (API keys, Gmail password) can't be in code. Use AWS Secrets Manager (free tier: 30 days, then $0.40/secret/month — but for this use case we pass them as env vars at deploy time).

The starter toolkit supports env vars via the config:

Create `agentcore_env.sh` (run this before deploying):

```bash
#!/bin/bash
# agentcore_env.sh — sets env vars for the deployed agent
# Run: source agentcore_env.sh

export TAVILY_API_KEY="tvly-your-key-here"
export HUNTER_API_KEY="your-hunter-key-here"
export GMAIL_ADDRESS="youremail@gmail.com"
export GMAIL_APP_PASSWORD="xxxx xxxx xxxx xxxx"
export YOUR_NAME="Kiki"
export YOUR_ROLE="GenAI Solutions Engineer"
export YOUR_LINKEDIN="https://linkedin.com/in/yourprofile"
export YOUR_GITHUB="https://github.com/yourusername"
```

Add to `.bedrock_agentcore.yaml` after configure step:

```yaml
# Add this section after running agentcore configure
environment_variables:
  TAVILY_API_KEY: "${TAVILY_API_KEY}"
  HUNTER_API_KEY: "${HUNTER_API_KEY}"
  GMAIL_ADDRESS: "${GMAIL_ADDRESS}"
  GMAIL_APP_PASSWORD: "${GMAIL_APP_PASSWORD}"
  YOUR_NAME: "${YOUR_NAME}"
  YOUR_ROLE: "${YOUR_ROLE}"
  YOUR_LINKEDIN: "${YOUR_LINKEDIN}"
  YOUR_GITHUB: "${YOUR_GITHUB}"
```

---

## STEP 8 — Deploy to AgentCore

```bash
# Source your env vars first
source agentcore_env.sh

# Configure (one time only)
agentcore configure -e main.py --disable-memory -r us-west-2

# Edit .bedrock_agentcore.yaml to add environment_variables (Step 7)

# Deploy (~8 minutes)
agentcore deploy
```

Output:
```
✅ Deployment successful!
Agent ARN: arn:aws:bedrock-agentcore:us-west-2:123456789012:agent-runtime/founder-outreach-agent-xxxx
Logs: /aws/bedrock-agentcore/founder-outreach-agent-xxxx
```

**Save that ARN.**

---

## STEP 9 — Invoke Your Deployed Agent

### Via CLI

```bash
# Research mode (safe, free test)
agentcore invoke '{"prompt": "Find 3 AI startups in the US that raised money in 2024", "dry_run": true}'

# Real outreach
agentcore invoke '{
  "prompt": "Find 2 robotics or GenAI startups in US hiring engineers. Email their founders mentioning my IEEE papers and LangGraph+AWS work.",
  "dry_run": false
}'
```

### Via Python (invoke_agent.py)

```python
# invoke_agent.py
import boto3
import json

AGENT_ARN = "arn:aws:bedrock-agentcore:us-west-2:YOUR_ACCOUNT:agent-runtime/YOUR_AGENT_ID"
client = boto3.client("bedrock-agentcore", region_name="us-west-2")

def run(prompt: str, dry_run: bool = True) -> str:
    response = client.invoke_agent_runtime(
        agentRuntimeArn=AGENT_ARN,
        sessionId="outreach-session-001",
        payload=json.dumps({"prompt": prompt, "dry_run": dry_run}),
    )
    result = json.loads(response["completion"].read())
    return result["response"]

if __name__ == "__main__":
    # Always test dry run first
    print("=== DRY RUN ===")
    print(run(
        "Find 3 AI startup founders in San Francisco. Research each company.",
        dry_run=True
    ))
    
    # Uncomment when ready to actually send
    # print("=== LIVE RUN ===")
    # print(run(
    #     "Find 2 GenAI or robotics startups in US likely hiring. Email founders about my background.",
    #     dry_run=False
    # ))
```

```bash
python invoke_agent.py
```

---

## STEP 10 — Real Prompts to Use

Once deployed, here are prompts that actually work:

```bash
# Find AI startup founders and email them
agentcore invoke '{
  "prompt": "Find 5 AI startups in San Francisco or New York that raised Series A or Seed in 2024. For each, find the founder or CTO email and send them a cold email from Kiki about a GenAI engineer role. Mention her LangGraph multi-agent system, IEEE papers, and AWS AgentCore experience.",
  "dry_run": false
}'

# Target robotics companies specifically  
agentcore invoke '{
  "prompt": "Find robotics startups in the US that focus on autonomous systems or AI-powered robots. Find their technical founders and email them. Mention NYCU robotics research internship and C++ real-time systems background.",
  "dry_run": false
}'

# Check what has been sent
agentcore invoke '{
  "prompt": "Show me the outreach log — who have we emailed so far and what were the subjects?",
  "dry_run": true
}'

# Research only (no emails)
agentcore invoke '{
  "prompt": "Find the top 10 AI agent infrastructure startups in the US (companies building platforms for deploying AI agents). Just research and list them with founders.",
  "dry_run": true
}'
```

---

## STEP 11 — Cost Breakdown

| Resource | Free Tier / Pricing | Monthly Cost (low usage) |
|---|---|---|
| Tavily API | 1,000 searches/month free | $0 |
| Hunter.io | 25 email lookups/month free | $0 |
| Gmail SMTP | 500 emails/day free | $0 |
| Claude Haiku (Bedrock) | $0.25/M input tokens | ~$0.10 (100 runs) |
| AgentCore Runtime | ~$0.001/invocation | ~$0.10 (100 runs) |
| **Total** | | **~$0.20/month** |

---

## STEP 12 — Clean Up

```bash
agentcore delete
```

---

## Final Project Structure

```
founder-outreach-agent/
├── tools.py                  # All 5 tools (search, email, log)
├── agent.py                  # Pure LangGraph (local testing)
├── main.py                   # AgentCore entrypoint (deployed)
├── invoke_agent.py           # boto3 client
├── run_local_test.py         # Local test runner
├── requirements.txt          # Python deps for cloud
├── agentcore_env.sh          # Set env vars (never commit this)
├── .bedrock_agentcore.yaml   # AgentCore config (auto-generated)
├── outreach_log.json         # Auto-created, tracks all emails sent
└── .env                      # Local secrets (never commit this)
```

---

## What You Learned vs Guide 1

| Concept | Guide 1 | This Guide |
|---|---|---|
| Tools | Wikipedia + calculator | Real-world: Tavily, Hunter.io, Gmail SMTP |
| Use case | Demo | Actual career tool you can use |
| Secrets | Hardcoded | Env vars + AgentCore config |
| Safety | No dry_run | `dry_run` flag before any real action |
| Logging | None | Persistent JSON log to avoid duplicates |
| System prompt | Basic | Role-aware, tone-controlled, strategy-defined |

---

## Common Issues & Fixes

| Error | Fix |
|---|---|
| `TavilyException: Invalid API key` | Check TAVILY_API_KEY in .env |
| `smtplib.SMTPAuthenticationError` | Use App Password not your Gmail password |
| `No module named 'dotenv'` | `pip install python-dotenv` |
| `Hunter returns no email` | Agent falls back to guessed patterns — check the log |
| Agent sends duplicate emails | It checks `get_outreach_log` — works if log is accessible in cloud |
| AgentCore can't find outreach_log.json | In cloud, log is ephemeral per container — use S3 or DynamoDB for production persistence |
