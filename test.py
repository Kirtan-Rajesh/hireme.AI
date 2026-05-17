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