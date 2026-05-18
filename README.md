# Job Hunting Agent

A local Python workflow for automated job outreach, resume optimization, and outreach tracking.

## What this repo does

- Searches for companies hiring your role
- Finds decision-maker email addresses
- Drafts personalized outreach using Bedrock / Claude
- Sends emails through your Gmail account
- Compiles and attaches your `resume.pdf` from `resume.tex`
- Logs outreach in `job_tracking.xlsx`
- Sends daily summary reports

## Files you need

- `main.py` — CLI entrypoint for the workflow
- `tools.py` — core functions for search, email, resume, tracking
- `requirements.txt` — Python dependencies
- `.env.example` — environment variable template
- `resume.tex` — your LaTeX resume source
- `run_daily_job_hunt.bat` — optional Windows scheduler entrypoint

## Setup (from scratch)

1. Install Python 3.11 or newer.
2. Open PowerShell and install dependencies:

```powershell
python -m pip install --upgrade pip
pip install -r requirements.txt
```

3. Copy `.env.example` to `.env` and fill in your values:

```powershell
copy .env.example .env
```

Required variables:

- `YOUR_NAME`
- `YOUR_ROLE`
- `YOUR_EMAIL`
- `GMAIL_ADDRESS`
- `GMAIL_APP_PASSWORD`
- `TAVILY_API_KEY`
- `HUNTER_API_KEY`
- `AWS_REGION`
- `BEDROCK_MODEL`

Optional but recommended:

- `SERPAPI_API_KEY` (for higher-quality company search results)

4. Edit `resume.tex` with your real experience.

5. (Optional) Install a LaTeX distribution with `pdflatex` if you want PDF resume attachment.
   - On Windows, use MikTeX or TeX Live.
   - If `pdflatex` is not installed, the workflow still runs but will send emails without the attached resume.

## Recommended first test

Run a dry run so the system researches and drafts without sending email:

```powershell
python main.py dry-run "Find 3 companies hiring for my role and draft emails"
```

## Primary commands

```powershell
python main.py daily
  # Full run: search, draft, send, log, report

python main.py daily-force
  # Same as daily, but ignores previous outreach history

python main.py dry-run "<query>"
  # Research and draft only; no emails are sent

python main.py resume
  # Optimize your LaTeX resume text only

python main.py report
  # Send today’s activity report

python main.py track
  # Show current Excel tracking status
```

## Draft approval workflow

Use this if you want to review drafts before sending:

```powershell
python main.py review
python main.py approve
python main.py send-approved
```

For quick approval or rejection:

```powershell
python main.py approve-draft <draft_id>
python main.py reject-draft <draft_id> "reason"
```

## Notes for new users

- `job_tracking.xlsx` and `outreach_log.json` are generated automatically.
- `.env` should never be committed.
- `main.py daily` is the main one-command automation.
- If you want the system to start from nothing, delete `job_tracking.xlsx`, `outreach_log.json`, and `.api_cache.json` before running.

## Cleanup

This repo keeps only the required workflow files. Extra guide files and legacy docs were removed so setup is simpler for strangers.
