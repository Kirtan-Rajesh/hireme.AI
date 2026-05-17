# 🚀 JOB HUNTING AGENT - QUICK START (5 Minutes)

## What You Have Now

✅ **Fully automated job hunting system**
- Searches for companies hiring your role
- Finds hiring managers and their emails
- Drafts personalized emails using Claude AI
- Sends emails via your Gmail
- Tracks everything in Excel
- Emails you daily reports

✅ **Zero configuration required** (mostly)
- Works locally on your PC
- No AWS complexity (just uses Bedrock for AI)
- No website/app to deploy
- No uptime concerns

---

## 5-Minute Setup

### 1. Copy Your Secrets (2 minutes)

**Create `.env` file** in `E:\hireme\`:

```env
YOUR_NAME=Your Name
YOUR_ROLE=Software Engineer
GMAIL_ADDRESS=yourname@gmail.com
GMAIL_APP_PASSWORD=xxxx xxxx xxxx xxxx  # Get from Gmail > App Passwords

TAVILY_API_KEY=your-key  # Free from tavily.com
HUNTER_API_KEY=your-key  # Free from hunter.io

AWS_REGION=eu-north-1
DISABLE_SSL_VERIFY=1
```

See `SETUP_JOB_HUNTER_AGENT.md` for detailed instructions.

### 2. Update Your Resume (2 minutes)

Edit `resume.tex` with your:
- Name and email
- Recent jobs and achievements
- Projects (especially AI/ML/Cloud)
- Skills
- Education

This is what gets mentioned in emails!

### 3. Test It Works (1 minute)

```powershell
# Activate Python environment
.\.venv\Scripts\Activate.ps1

# Test without sending emails
python main.py dry-run "Find 3 companies hiring for my role"

# You should see:
# ✅ Search results
# ✅ Email drafts (shown, not sent)
# ✅ Company/person research
```

---

## Start Using It

### Manual Daily Use

```powershell
# Every morning, run:
python main.py daily

# This will:
# 1. Analyze your resume
# 2. Find 5-10 companies
# 3. Find hiring managers
# 4. Draft personalized emails
# 5. Send them
# 6. Email you a report
```

### Automate It (Windows Task Scheduler)

**One-time setup:**

1. **Win+R** → `taskschd.msc` (opens Task Scheduler)
2. **Right-click** → Create Basic Task
3. **Name**: "Daily Job Hunt"
4. **Trigger**: Daily, 9:00 AM
5. **Action**: 
   - Program: `cmd.exe`
   - Args: `/c E:\hireme\run_daily_job_hunt.bat`
6. **Finish** → Done!

**Result**: Every morning at 9 AM, your agent runs automatically and emails you the results.

---

## Key Commands

```powershell
# Full automated run (what Task Scheduler does)
python main.py daily

# Test without sending
python main.py dry-run "Search for AI startups"

# Just optimize resume
python main.py resume

# See all past outreach
python main.py track

# Send today's report
python main.py report

# Custom search
python main.py "Find Python engineers at startups in SF"
```

---

## What Happens Each Day

```
9:00 AM - Task Scheduler triggers run_daily_job_hunt.bat
    ↓
Python activates and runs: python main.py daily
    ↓
Agent:
  1. Optimizes your resume ✅
  2. Searches: "Hiring for [your role]"
  3. Finds: 5-10 target companies
  4. Researches: Their product/work
  5. Identifies: Hiring manager/CTO
  6. Finds: Their email address
  7. Drafts: Personalized email
  8. Sends: Via your Gmail
  9. Logs: In job_tracking.xlsx
  10. Reports: Emails you summary + Excel
    ↓
You get email like:
  "Daily Job Hunt Report - 2026-05-15
   Contacted: 7 companies
   Details: [Excel attached]"
```

---

## Track Your Progress

### Excel Tracking Sheet (`job_tracking.xlsx`)

| Company | Person | Email | Date | Status | Notes |
|---------|--------|-------|------|--------|-------|
| TwelveLabs | Jae Lee | jae@twelvelabs.io | 2026-05-15 | Sent | CTO, AI video |
| Together AI | Vipul Ved | vipul@together.ai | 2026-05-15 | Sent | LLM platform |

**Updated**: Every email sent, every day

**Emailed to you**: Every evening with summary

---

## Cost (Very Cheap!)

```
Monthly Costs:

Tavily (Search):     FREE (1000/month free tier)
Hunter.io (Email):   FREE (25/month free tier)
Gmail (Sending):     FREE (unlimited)
AWS Bedrock (AI):    ~$0.50 (very cheap!)
─────────────────────────────
TOTAL:               ~$0.50/month 😎
```

---

## Success Expectations

```
Week 1: Just getting started
├─ 30-50 companies contacted
└─ 0-2% response rate (normal)

Week 2-4: Building momentum
├─ 100+ companies contacted
├─ 3-5% response rate (conversations!)
└─ 2-5 interviews scheduled

Month 2+: Job offers coming
└─ Job offer + negotiation! 🎉
```

*Note: Timing varies by role/market. Keep at it!*

---

## Troubleshooting

### "Where are my API keys?"

1. **Tavily**: https://tavily.com → Sign up (free) → Copy API key
2. **Hunter.io**: https://hunter.io → Sign up (free) → Copy API key
3. **Gmail App Password**: 
   - Go to https://myaccount.google.com/apppasswords
   - Select Mail + Windows Computer
   - Copy the 16-character password (not your Gmail password!)

### "SSL Certificate Error"

```powershell
# In .env, set:
DISABLE_SSL_VERIFY=1
```

### "No search results"

- Check TAVILY_API_KEY is correct
- Try more specific search: "Python engineer hiring Berlin startup"
- Check you have searches remaining (1000/month)

### "Email didn't send"

- Check GMAIL_ADDRESS in .env
- Make sure GMAIL_APP_PASSWORD is set (not your regular password)
- Verify 2FA is enabled on Gmail
- Check email isn't being filtered to spam

---

## Advanced Usage

### Target Specific Companies

```powershell
python main.py "Find engineers at Google who work on AI and email them about my AI projects"

python main.py "Search for companies using LangChain in their tech stack"

python main.py "Find startups Series B or later hiring ML engineers in Berlin"
```

### Follow-Up Strategy

```powershell
python main.py "Find people I emailed 7+ days ago with no response and send polite follow-up"

python main.py "Send thank you emails to people who replied positively"
```

### Dry Run (Test Before Sending)

```powershell
python main.py dry-run "Find 5 companies and draft emails"

# Shows everything but doesn't send
# Great for testing new searches!
```

---

## Files You Have

```
E:\hireme\
├── main.py                    ← Main agent (read prompts, run searches)
├── tools.py                   ← All 9 tools (search, email, tracking, etc.)
├── requirements.txt           ← Python dependencies
├── resume.tex                 ← Your resume (EDIT THIS!)
├── .env                       ← Your secrets (CREATE THIS!)
├── .env.example               ← Template for .env
├── run_daily_job_hunt.bat     ← Windows Task Scheduler runner
├── SETUP_JOB_HUNTER_AGENT.md  ← Full setup guide
├── QUICK_START.md             ← This file
├── outreach_log.json          ← Created automatically, all emails sent
└── job_tracking.xlsx          ← Created automatically, Excel tracking
```

---

## Next Steps

1. ✅ Copy `.env.example` → `.env` and fill in your secrets
2. ✅ Edit `resume.tex` with your real experience
3. ✅ Run: `python main.py dry-run "test"` (verify no errors)
4. ✅ Run: `python main.py daily` (send real emails!)
5. ✅ Check email for daily report with Excel attachment
6. ✅ Set up Windows Task Scheduler for automatic daily runs

---

## Questions?

Check these files:
- **"How do I set up?"** → `SETUP_JOB_HUNTER_AGENT.md`
- **"What tools exist?"** → `tools.py` (8 tools, well documented)
- **"How do I run custom searches?"** → `python main.py` (shows all commands)
- **"What's in the code?"** → `main.py` (heavily commented)

---

## You're Ready! 🚀

Your job hunting agent is ready to work for you.

**Start with:**

```powershell
.\.venv\Scripts\Activate.ps1
python main.py daily
```

**Check email in ~5 minutes for your first report!**

Good luck with your job search! 🎯
