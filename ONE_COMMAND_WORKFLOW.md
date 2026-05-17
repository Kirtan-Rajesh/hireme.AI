# 🚀 ONE-COMMAND JOB HUNT SYSTEM

**Everything you need: Find companies → Draft emails → Review emails → Send emails → Track in Excel**

All in **ONE command**: `python main.py daily`

---

## 🎯 Quick Start (2 Minutes)

```powershell
# Activate virtual environment
.\.venv\Scripts\Activate.ps1

# Run the one-command workflow
python main.py daily
```

**That's it!** The system will:
1. Ask you for location and number of companies
2. Search for companies hiring your role
3. Find founder/CEO emails
4. Draft personalized emails
5. Show you each email for approval/rejection
6. Send approved emails
7. Update job_tracking.xlsx automatically

---

## 📋 The Workflow (Step-by-Step)

### **Step 1: Start the Workflow**
```powershell
python main.py daily
```

**Output:**
```
╔════════════════════════════════════════════════════════════════╗
║      🚀 ONE-COMMAND JOB HUNT WORKFLOW
╚════════════════════════════════════════════════════════════════╝

Location to search for [Your Role] jobs (default: Berlin): 
```

### **Step 2: Tell Agent What You Want**

```
Location: Berlin
How many companies to find? 5
```

Agent then searches for 5 companies hiring in Berlin.

### **Step 3: Review Email Drafts**

Agent creates email drafts for each company and **shows you each one**:

```
[1/5] DRAFT: draft_1715892345_789
──────────────────────────────────────────────────────────────────
Company: SoundCloud
Contact: Alexander Ljung (CEO & Founder)
Email:   alexander@soundcloud.com

Subject: Python Engineer - Audio Infrastructure Interest

Body:
Hi Alexander,

I've been following SoundCloud's infrastructure work with Scala/Python 
microservices. I'm a GenAI software developer interested in how you're 
scaling audio processing with modern ML.

I've built LangGraph agents for real-time data processing on AWS—
similar to your challenges. Would love a 15-min chat about contributing 
to your platform.

GitHub: https://github.com/your-profile
LinkedIn: https://linkedin.com/in/your-profile

Best,
Kirtan

---
Unsubscribe: Reply with "STOP"
──────────────────────────────────────────────────────────────────
(a)pprove, (r)eject, (s)kip, or (q)uit?
```

### **Step 4: Approve/Reject Each Email**

For each draft, respond with:

- **`a`** - Approve & send this email
- **`r`** - Reject (will ask reason)
- **`s`** - Skip for now
- **`q`** - Quit (stop reviewing)

```
(a)pprove, (r)eject, (s)kip, or (q)uit? a
✅ Approved: draft_1715892345_789
```

### **Step 5: Send All Approved Emails**

After reviewing all drafts:

```
📊 APPROVAL SUMMARY
══════════════════════════════════════════════════════════════════
✅ Approved: 4
❌ Rejected: 1

Send 4 approved emails now? (y/n) y

✅ Sent 4 emails!
📊 Updated: job_tracking.xlsx
```

### **Step 6: Check Results**

Excel file automatically updated with:
- Company name
- Contact person (CEO/Founder)
- Email address
- Send date & time
- Automatic 7-day follow-up date
- Notes

---

## 📁 Where Everything Lives

### **Draft Emails (Temporary Files)**
```
todays_drafts/
├── draft_1715892345_789_SoundCloud_Alexander_Ljung.txt
├── draft_1715892346_456_Zalando_David_Schneider.txt
└── draft_1715892347_123_N26_Valentin_Stalf.txt
```

Each `.txt` file is human-readable with full email details.

### **Excel Tracking Sheet**
```
job_tracking.xlsx
├─ Company    | SoundCloud
├─ Person     | Alexander Ljung
├─ Email      | alexander@soundcloud.com
├─ Date       | 2026-05-15 14:32
├─ Status     | Sent
├─ Notes      | CEO/Founder, Python engineer
└─ Follow-up  | 2026-05-22  (Auto-set to 7 days)
```

### **Tracking Files**
- `email_drafts.json` - Internal tracking of all drafts/statuses
- `outreach_log.json` - Historical log of all emails sent
- `.api_cache.json` - Caching layer (saves API calls)

---

## 🛠️ Advanced Commands

If you want to skip the interactive flow and use commands directly:

### **View Pending Drafts**
```powershell
python main.py review
```

Shows all drafts waiting for approval.

### **Interactively Review**
```powershell
python main.py approve
```

Same as Step 3-4 above (review each draft interactively).

### **Approve Single Draft**
```powershell
python main.py approve-draft draft_1715892345_789
```

### **Reject Single Draft**
```powershell
python main.py reject-draft draft_1715892345_789 "Email too generic"
```

### **Send All Approved**
```powershell
python main.py send-approved
```

Sends everything that's been approved.

---

## 💡 Typical Workflow Example

### **Day 1: Initial Outreach**
```powershell
.\.venv\Scripts\Activate.ps1
python main.py daily

# Answer prompts:
# Location: Berlin
# Companies: 5

# Review and approve 4 emails, reject 1

# Result: 4 emails sent, tracked in Excel
```

### **Day 7: Follow-ups**
```powershell
python main.py review

# See follow-up dates marked for 7+ days ago
# Approve follow-up emails
# python main.py send-approved
```

### **Daily Tracking**
```powershell
python main.py track

# Shows job_tracking.xlsx contents
```

---

## ✅ Quality Assurance

**Why this system is better than auto-sending:**

1. ✅ **YOU approve every email** - no spam, no generic messages
2. ✅ **Founder/CEO emails** - not generic hiring teams
3. ✅ **Personalized for each company** - researched by AI agent
4. ✅ **Review before sending** - catch mistakes
5. ✅ **Complete tracking** - know exactly who you've contacted
6. ✅ **7-day follow-ups** - automatically scheduled
7. ✅ **One Excel sheet** - all company info in one place

---

## 🔄 One-Command Pros vs Cons

### **Pros:**
- ✅ Finds companies automatically
- ✅ Gets founder/CEO emails (not generic hiring managers)
- ✅ Drafts personalized emails
- ✅ You review before sending (NO spam)
- ✅ Single command to do everything
- ✅ Complete tracking in Excel
- ✅ Auto follow-ups at 7 days

### **Cons:**
- ⚠️ Interactive (requires you to approve each email)
- ⚠️ Takes time to review (but worth it!)
- ⚠️ Needs all .env variables set up

---

## 🎯 Success Metrics

**Track these over time:**

```
Weekly Progress:
├─ Companies Found: 5
├─ Emails Drafted: 5
├─ Emails Approved: 4 (80%)
├─ Emails Sent: 4
├─ Email Bounces: 0 (0%)
├─ Replies: 1 (25%)
└─ Interviews Scheduled: 0

Follow-ups (Day 7-14):
├─ Follow-up Emails: 3
├─ Replies to Follow-ups: 1 (33%)
└─ Total Conversations: 2
```

---

## ❓ FAQ

### **Q: Why does it ask me to approve every email?**
A: Because AI sometimes makes mistakes. You're the human—trust yourself more than the bot. Review each email before it goes out.

### **Q: Where are the drafted emails saved?**
A: In `todays_drafts/` folder as `.txt` files. Open them in any text editor.

### **Q: Can I edit drafted emails?**
A: Currently, you can reject and ask the agent to redraft. Edit the `.txt` file preview to see what you want, then reject with feedback.

### **Q: What if an email bounces?**
A: The email validation catches 99% of bad addresses. If one slips through, it gets caught by Gmail and logged in outreach_log.json.

### **Q: How do I schedule this to run daily?**
A: Use Windows Task Scheduler:
1. Win+R → taskschd.msc
2. Create Basic Task
3. Name: "Daily Job Hunt"
4. Trigger: Daily 9:00 AM
5. Action: `python main.py daily`

But note: `python main.py daily` requires **interactive input**, so it won't work well fully automated. Better to run it manually each morning.

### **Q: Can I run it automatically without interaction?**
A: Not yet. Current system is interactive to prevent spam. Consider it a feature, not a bug!

### **Q: Where's the Excel file created?**
A: `job_tracking.xlsx` in your project folder. Email yourself daily copy with `python main.py report`.

---

## 🚀 Next Steps

1. **Set up `.env`** file with all API keys (Tavily, Hunter, Gmail, AWS)
2. **Edit `resume.tex`** with your real experience
3. **Run first test:**
   ```powershell
   python main.py daily
   ```
4. **Approve drafts** carefully
5. **Check Excel** for tracking
6. **Setup Windows Task Scheduler** for daily 9 AM runs (manual better than auto)

---

## 🎉 You're Ready!

The system is designed to be:
- ✅ **Smart** - Finds founders, researches companies, personalizes emails
- ✅ **Safe** - You review everything before sending
- ✅ **Tracked** - Complete Excel sheet of all outreach
- ✅ **Optimized** - Caching reduces API calls, validation prevents bounces
- ✅ **Simple** - One command: `python main.py daily`

**Start now:**
```powershell
.\.venv\Scripts\Activate.ps1
python main.py daily
```

Good luck! 🎯
