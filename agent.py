# agent.py  — pure LangGraph, no AgentCore yet

import os
from dotenv import load_dotenv
load_dotenv()

from langchain_aws import ChatBedrockConverse
from langchain_core.messages import HumanMessage, SystemMessage
from langchain.agents import create_agent
from tools import search_web, find_email, send_email, log_outreach, get_outreach_log
from langgraph.prebuilt import create_react_agent  # keep this import



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
BEDROCK_MODEL = os.environ.get(
    "BEDROCK_MODEL",
    "eu.anthropic.claude-haiku-4-5-20251001-v1:0"  # eu. prefix
)
BEDROCK_REGION = os.environ.get("AWS_REGION", "eu-north-1")  # your region

llm = ChatBedrockConverse(
    model=BEDROCK_MODEL,
    region_name=BEDROCK_REGION,
    temperature=0.3,   # lower = more consistent, less hallucination on facts
    max_tokens=2048,
)

tools = [search_web, find_email, send_email, log_outreach, get_outreach_log]
graph = create_react_agent(llm, tools=tools, prompt=SYSTEM_PROMPT)   # NOT create_agent, prompt= not system_prompt=


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