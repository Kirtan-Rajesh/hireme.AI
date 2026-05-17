# Job Hunting Agent - Complete Setup Guide

**Status**: Production-ready local agent (no AWS/cloud required)  
**Purpose**: Daily automated job search with personalized outreach and tracking  
**Built**: May 15, 2026

---

## What You're Getting

✅ **Daily Job Hunt Automation**
- Searches for companies hiring for your role
- Identifies hiring managers/CTOs
- Researches their work
- Drafts personalized emails
- Sends and tracks automatically
- Reports daily progress

✅ **Resume Optimization**
- Analyzes your LaTeX resume
- Suggests improvements
- Highlights missing skills/projects
- Helps optimize before sending

✅ **Excel Tracking Sheet**
- Logs every company/contact
- Tracks email sent date
- Records response status
- Generates daily reports
- Sent to your email each evening

✅ **Zero Cloud Dependency**
- Runs locally on your PC
- No AWS AgentCore complexity
- Uses only free APIs (Tavily, Hunter.io, Gmail)
- Easy to schedule with Windows Task Scheduler

---

## Prerequisites

### 1. Python 3.11+ with Virtual Environment

```powershell
# Check Python version
python --version  # Should be 3.11+

# Create virtual environment
python -m venv .venv

# Activate it
.\.venv\Scripts\Activate.ps1

# Upgrade pip
python -m pip install --upgrade pip
```

### 2. Install Dependencies

```powershell
# Inside activated venv
pip install -r requirements.txt

# Verify Claude/Bedrock access
python -c "import boto3; print('✅ AWS SDK ready')"
```

### 3. API Keys & Credentials

You need 3 free accounts:

#### A. **Tavily API** (Web Search - 1000/month free)
```
1. Go to https://tavily.com
2. Sign up (free)
3. Get API key
4. Add to .env: TAVILY_API_KEY=xxx
```

#### B. **Hunter.io** (Email Finding - 25/month free)
```
1. Go to https://hunter.io
2. Sign up (free)
3. Get API key
4. Add to .env: HUNTER_API_KEY=xxx
```

#### C. **Gmail** (Email Sending - unlimited free)
```
1. Use your existing Gmail or create new one
2. Enable 2FA: https://myaccount.google.com/security
3. Create App Password (NOT your Gmail password!):
   a. Go to https://myaccount.google.com/apppasswords
   b. Select Mail > Windows Computer
   c. Copy the 16-character password
4. Add to .env:
   GMAIL_ADDRESS=yourname@gmail.com
   GMAIL_APP_PASSWORD=xxxx xxxx xxxx xxxx
```

#### D. **AWS Bedrock** (Claude AI - $0.25 per 1M input tokens)
```
1. Already have AWS account? Great!
2. If not: https://aws.amazon.com (free tier includes $100 credit)
3. Enable Bedrock in eu-north-1 region
4. Configure AWS CLI:
   aws configure
   # Enter AWS Access Key ID
   # Enter AWS Secret Access Key
   # Default region: eu-north-1
```

---

## Configuration (.env file)

Create `.env` file in `E:\hireme\`:

```env
# Your Profile
YOUR_NAME=Your Name
YOUR_ROLE=Software Engineer
YOUR_EMAIL=yourname@gmail.com
YOUR_LINKEDIN=https://linkedin.com/in/yourprofile
YOUR_GITHUB=https://github.com/yourprofile

# Resume (create resume.tex first!)
RESUME_PATH=./resume.tex

# API Keys (KEEP SECRET - never commit to git!)
TAVILY_API_KEY=your-key-here
HUNTER_API_KEY=your-key-here
GMAIL_ADDRESS=yourname@gmail.com
GMAIL_APP_PASSWORD=xxxx xxxx xxxx xxxx

# AWS/Bedrock
AWS_REGION=eu-north-1
BEDROCK_MODEL=eu.anthropic.claude-haiku-4-5-20251001-v1:0

# Development (ignore in production)
DISABLE_SSL_VERIFY=1
DEV_MODE=1
```

**⚠️ IMPORTANT**: Add `.env` to `.gitignore` to never leak secrets!

```powershell
# Add to .gitignore
echo ".env" >> .gitignore
```

---

## Create Your Resume

Create `resume.tex` (LaTeX format):

```latex
\documentclass[11pt]{article}
\usepackage{geometry}
\geometry{margin=0.5in}

\title{Your Name - Software Engineer}
\author{Email: your@email.com | GitHub: github.com/you | LinkedIn: linkedin.com/in/you}

\begin{document}
\maketitle

\section*{SUMMARY}
Software engineer with experience in Python, AWS, AI/ML, and distributed systems.
Strong background in building scalable applications and AI agents.

\section*{EXPERIENCE}
\textbf{Title} | Company Name | Jan 2024 - Present
\begin{itemize}
    \item Built AI agent using LangGraph that processed 10K+ requests/day
    \item Deployed to AWS Lambda with 99.99\% uptime
    \item Tech Stack: Python, AWS, Claude AI, LangChain
\end{itemize}

\section*{PROJECTS}
\textbf{Job Hunt Agent} | Personal Project | May 2026
\begin{itemize}
    \item Built AI agent for automated job search and outreach
    \item Sends 5-10 personalized emails daily to target companies
    \item Tracks all outreach in Excel with daily reports
\end{itemize}

\section*{SKILLS}
\textbf{Languages}: Python, JavaScript, C++, SQL
\textbf{Tools}: AWS (Lambda, Bedrock, EC2), Git, Docker
\textbf{AI/ML}: LangChain, LangGraph, Claude, OpenAI
\textbf{Frameworks}: FastAPI, React, Django

\end{document}
```

---

## Test the Agent

### Test 1: Check all tools work

```powershell
# Activate venv
.\.venv\Scripts\Activate.ps1

# Test in dry-run mode (no emails sent)
python main.py dry-run "Find 3 Python engineer jobs in Berlin"

# Expected output:
# - Search results showing companies
# - Email drafts (not sent)
# - No entries in job_tracking.xlsx
```

### Test 2: Send a real email

```powershell
# Search and send email to test address
python main.py "Find a company hiring for my role and draft an email"

# Follow prompts to review and send
# Check job_tracking.xlsx - should have 1 entry
```

### Test 3: Check tracking sheet

```powershell
python main.py track

# Should show:
# 📊 Last 1 contacts:
# 🏢 Company | 👤 Person | 📧 email@company.com | 2026-05-15 | Sent
```

---

## Daily Execution

### Option 1: Manual Daily Run

```powershell
# Every morning, run:
python main.py daily

# This will:
# 1. Optimize your resume
# 2. Search for 5-10 companies
# 3. Find hiring managers
# 4. Draft and send personalized emails
# 5. Email you a daily report with Excel attachment
```

### Option 2: Automated Daily Run (Windows Task Scheduler)

```powershell
# Step 1: Create a batch file (run_daily_job_hunt.bat)
@echo off
cd E:\hireme
.\.venv\Scripts\activate.bat
python main.py daily
pause

# Save as: E:\hireme\run_daily_job_hunt.bat

# Step 2: Open Task Scheduler (Windows)
# Win+R → taskschd.msc

# Step 3: Create Basic Task
# Name: "Daily Job Hunt"
# Trigger: Daily at 9:00 AM
# Action: 
#   Program: cmd.exe
#   Args: /c E:\hireme\run_daily_job_hunt.bat

# Step 4: Done! Runs automatically every morning at 9 AM
```

### Option 3: Custom Schedule

```powershell
# Find specific companies
python main.py "Search for AI startups in SF hiring for ML engineers"

# Follow up with past contacts
python main.py "Find people who didn't respond and send follow-up emails"

# Target specific companies
python main.py "Find engineering leaders at Google/Meta/OpenAI and email them"
```

---

## Understanding the Workflow

```
┌─────────────────────────────────────────┐
│   Daily Job Hunt (9:00 AM - Automated)   │
└────────────┬────────────────────────────┘
             │
             ▼
    ┌────────────────────────┐
    │ 1. Optimize Resume     │
    │    ├─ Analyze current  │
    │    ├─ Identify gaps    │
    │    └─ Suggest updates  │
    └────────────┬───────────┘
                 │
                 ▼
    ┌────────────────────────┐
    │ 2. Search Companies    │
    │    ├─ Find 5-10 targets│
    │    ├─ Check job posts  │
    │    └─ Verify tech stack│
    └────────────┬───────────┘
                 │
                 ▼
    ┌────────────────────────┐
    │ 3. Find Contacts       │
    │    ├─ Identify CTO/CEO │
    │    ├─ Get email        │
    │    └─ Research work    │
    └────────────┬───────────┘
                 │
                 ▼
    ┌────────────────────────┐
    │ 4. Draft Emails        │
    │    ├─ Personalize      │
    │    ├─ Reference project│
    │    └─ Clear CTA        │
    └────────────┬───────────┘
                 │
                 ▼
    ┌────────────────────────┐
    │ 5. Send & Track        │
    │    ├─ Send via Gmail   │
    │    ├─ Log in Excel     │
    │    └─ Track response   │
    └────────────┬───────────┘
                 │
                 ▼
    ┌────────────────────────┐
    │ 6. Daily Report        │
    │    ├─ Emails sent: 7   │
    │    ├─ Companies: 7     │
    │    └─ Report → Gmail   │
    └────────────────────────┘
```

---

## Key Features Explained

### 1. **Email Tracking (job_tracking.xlsx)**

Automatically logs:
- **Company**: Where you emailed
- **Person**: Who you contacted
- **Email**: Their email address
- **Date**: When you sent
- **Status**: Sent / Replied / Rejected
- **Notes**: Any notes

Updated every send and emailed to you daily.

### 2. **Resume Optimization**

Analyzes your resume.tex for:
- ✅ Experience section (required)
- ✅ Projects using latest tech
- ⚠️ Missing: AI/ML experience
- ⚠️ Missing: AWS certifications
- 💡 Suggestions for improvement

### 3. **Personalized Emails**

Agent drafts emails that:
- Reference their specific company/product
- Mention your relevant projects
- Include technical details (shows expertise)
- Keep to 100 words max
- Sound genuine (not sales-y)
- Include unsubscribe (GDPR compliant)

### 4. **Daily Reports**

Each evening, you get:
- List of all companies contacted today
- Total outreach statistics
- Excel attachment with full tracking
- Sent to your Gmail inbox

---

## Cost Analysis

```
Free Tier Usage:

Tavily (Web Search):
├─ 1000 searches/month free
├─ 5-10 searches per day = OK
└─ Cost: $0 (free tier sufficient)

Hunter.io (Email Finding):
├─ 25 lookups/month free
├─ 1-2 per day = OK for free tier
└─ Cost: $0 (free tier sufficient)

Gmail (Email Sending):
├─ 50 emails/day limit
├─ 5-10 per day = Plenty of room
└─ Cost: $0 (free Gmail account)

AWS Bedrock (Claude AI):
├─ ~1000 tokens per email draft
├─ 5-10 emails/day = 5-10K tokens
├─ Cost: $0.25 per 1M tokens = ~$0.02/day
└─ Monthly: ~$0.50 (very cheap!)

TOTAL MONTHLY COST: ~$0.50 😎
(Just pay for AWS Bedrock, rest is free!)
```

---

## Troubleshooting

### "SSL Certificate Error"

```powershell
# Solution: Enable dev mode
$env:DISABLE_SSL_VERIFY=1
python main.py daily
```

### "Email not sending"

```powershell
# Check:
1. GMAIL_ADDRESS set in .env?
2. Using APP PASSWORD (not regular password)?
3. 2FA enabled on Gmail account?

# Verify:
python main.py dry-run "test"
```

### "No results from search"

```powershell
# Check:
1. TAVILY_API_KEY set correctly?
2. Still have searches remaining?
3. Query is specific enough?

# Try:
python main.py "Search for Python engineers hiring in 2026"
```

### "Email looks like spam"

Agent checks for:
- Missing unsubscribe option (add it)
- ALL CAPS subject (avoid)
- Too many !!!s (be professional)
- Generic content (personalize more)

Draft will warn before sending.

---

## Commands Reference

```powershell
# Daily automated run (9 AM auto)
python main.py daily

# Manual test (no emails)
python main.py dry-run "Find 3 companies"

# Custom search
python main.py "Find companies using my tech stack"

# Resume optimization
python main.py resume

# Show tracking
python main.py track

# Send daily report
python main.py report

# Help
python main.py
```

---

## Next Steps

1. ✅ Create .env with API keys
2. ✅ Create resume.tex with your experience
3. ✅ Run `python main.py dry-run "test"`
4. ✅ Schedule daily run in Task Scheduler
5. ✅ Check emails tomorrow morning!

---

## Success Metrics

Track your progress:

```
Week 1:
├─ Companies reached: 30-50
├─ Response rate: 0-2% (normal for cold email)
└─ Follow-up emails: Setup time

Week 2-4:
├─ Companies reached: 60-100+
├─ Response rate: 2-5% (conversations starting)
├─ Interviews: 1-3
└─ Job offers: (coming soon!)
```

---

## Safety & Best Practices

✅ **DO**:
- Personalize every email
- Reference their specific work
- Keep emails under 120 words
- Include unsubscribe option
- Track responses

❌ **DON'T**:
- Send mass identical emails (spam)
- Impersonate someone
- Make false claims about your experience
- Ignore unsubscribe requests
- Email more than 10-20 per day

---

**Happy job hunting! 🚀**

Questions? Check logs in `outreach_log.json` and `job_tracking.xlsx`
