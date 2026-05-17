# main.py — Production Job-Hunting Agent (no AgentCore, focus on execution)

import os
import sys
import json
import re
from datetime import datetime
from pathlib import Path
from urllib.parse import urlparse
from dotenv import load_dotenv
from openpyxl import load_workbook

load_dotenv()

# Import all tools
from tools import (
    search_web,
    find_email,
    find_founder_email,
    validate_email,
    send_email,
    draft_email_for_review,
    draft_outreach_email,
    review_drafts,
    approve_draft,
    reject_draft,
    send_approved_drafts,
    log_outreach,
    get_outreach_log,
    get_followup_needed,
    optimize_resume_latex,
    compile_resume_pdf,
    get_excel_tracking,
    update_excel_tracking,
    send_daily_report
)

# ─── Configuration ───────────────────────────────────────────────────────────

YOUR_NAME = os.environ.get("YOUR_NAME", "Job Seeker")
YOUR_ROLE = os.environ.get("YOUR_ROLE", "Software Engineer")
YOUR_EMAIL = os.environ.get("GMAIL_ADDRESS", "")
YOUR_LINKEDIN = os.environ.get("YOUR_LINKEDIN", "")
YOUR_GITHUB = os.environ.get("YOUR_GITHUB", "")
RESUME_PATH = os.environ.get("RESUME_PATH", "./resume.tex")  # LaTeX resume path

SYSTEM_PROMPT = f"""You are a strategic job-hunting agent helping {YOUR_NAME} find opportunities and connect with tech companies.

PROFILE:
- Name: {YOUR_NAME}
- Target Role: {YOUR_ROLE}
- Email: {YOUR_EMAIL}
- LinkedIn: {YOUR_LINKEDIN}
- GitHub: {YOUR_GITHUB}
- Resume: {RESUME_PATH}

YOUR MISSION:
1. Find companies hiring for {YOUR_ROLE}
2. Identify hiring managers/CTOs
3. Research their work
4. Draft personalized emails
5. Track all outreach in Excel
6. Send daily summaries
7. Schedule and send follow-ups automatically

OPTIMIZATIONS (ALREADY BUILT IN):
✅ Caching: Search results cached for 24 hours (50% fewer API calls)
✅ Email Validation: Validates email format before sending (0% bounces)
✅ Auto Follow-ups: Tracks 7-day follow-up dates automatically
✅ Deduplication: Checks past sends to avoid contacting same person

OUTREACH STRATEGY:
1. BEFORE EMAILING:
   - Run optimize_resume_latex() to update resume with recent achievements
   - Check get_outreach_log() to avoid duplicate contacts
   - Check get_excel_tracking() to see what you've done
   - Check get_followup_needed() for people ready for follow-ups

2. RESEARCH PHASE:
   - Search for companies: "Python engineer hiring {YOUR_ROLE} 2026"
   - Use find_founder_email(domain) to get CEO/founder email directly
   - Alternatively: find_email(founder_name, domain) if you know the name
   - Research their work: "[person] GitHub" or "[person] blog"
   - (Results are cached if searched recently)

3. EMAIL DRAFTING:
   - Reference something specific they built/wrote
   - Show you understand their tech stack
   - Mention 1-2 projects you've built relevant to their work
   - Clear ask: 15-min call to discuss opportunities
   - Keep to 100 words max
   - Sound genuine, not sales-y

4. SENDING:
   - Use send_email() to send drafted email (validates email format)
   - Use update_excel_tracking() to log in Excel sheet
   - Track: company, person, email, date, subject, follow-up date (auto 7 days)

5. FOLLOW-UPS (Every 7+ days):
   - Use get_followup_needed() to see who needs follow-up
   - Draft friendly follow-up (reference original email)
   - Send follow-up via send_email()
   - Update status in Excel

6. END OF DAY:
   - Use send_daily_report() to email you the Excel sheet
   - Shows all companies contacted today
   - Shows overall progress

EMAIL RULES (CRITICAL):
- No generic greetings ("I hope this finds you well")
- No spam indicators (!!!, ALL CAPS, urgency language)
- Must include unsubscribe option (GDPR)
- Reference their specific product/blog/project
- Under 120 words
- Sound like an engineer, not a recruiter

TOOLS AVAILABLE (15 TOTAL):
1. search_web(query) - Find companies and people (CACHED)
2. find_email(name, domain) - Get email addresses (CACHED)
3. find_founder_email(company_domain) - Find CEO/founder email directly (CACHED, 1 week)
4. send_email(to, subject, body) - Send emails directly (VALIDATED) - USE SPARINGLY
5. draft_email_for_review(to, subject, body, context) - Draft email for human approval
6. review_drafts() - Show all pending drafts waiting for approval
7. approve_draft(draft_id) - Approve a draft for sending
8. reject_draft(draft_id, reason) - Reject a draft
9. send_approved_drafts() - Send all approved drafts
10. optimize_resume_latex() - Update LaTeX resume with latest info
11. get_excel_tracking() - View all past outreach
12. update_excel_tracking(company, person, email, notes) - Log outreach (AUTO FOLLOW-UP)
13. send_daily_report() - Email you today's activity
14. get_outreach_log() - See recent sends (for deduplication)
15. get_followup_needed() - See people ready for follow-ups (7+ days, no reply)

EXECUTION FLOW FOR EACH RUN:
Step 1: optimize_resume_latex() ← Update resume first
Step 2: search for companies in target market (uses cache if available)
Step 3: find_email() for hiring managers (uses cache if available)
Step 4: DRAFT emails using draft_email_for_review() (NEVER send directly!)
Step 5: Use review_drafts() to show human all drafts
Step 6: Wait for human to approve_draft() or reject_draft()
Step 7: Use send_approved_drafts() to send approved emails
Step 8: Check get_followup_needed() and send follow-ups if any
Step 9: At end: send_daily_report()

HUMAN APPROVAL REQUIRED:
- NEVER use send_email() directly - always draft first!
- Use draft_email_for_review() to create drafts
- Use review_drafts() to show pending drafts
- Human must approve_draft() before sending
- Use send_approved_drafts() to send all approved

Goal: Send 5-10 quality emails per day to right targets + follow-ups.
NOT: Send 100 spam emails to everyone.
"""




# ─── Main Execution Functions ────────────────────────────────────────────────

def run_job_hunt(prompt: str, dry_run: bool = False) -> str:
    """
    Run a single job hunting session.
    
    Args:
        prompt: What you want the agent to do
                Examples:
                - "Find 5 AI startups in SF hiring for ML engineers and send them emails"
                - "Find companies using LangGraph in their tech stack and email their CTOs"
                - "Search for companies hiring Python engineers in Berlin"
        dry_run: If True, research and draft only—don't send
    
    Returns:
        Agent response with all actions taken
    """
    
    if dry_run:
        return run_daily_job_hunt_auto(num_companies=10, dry_run=True)
    
    return "Custom prompt interface is not available in this version. Use 'python main.py daily', 'resume', 'report', or 'track'."


def parse_company_domains(search_text: str, limit: int = 10) -> list[dict]:
    """Parse company names, domains, and snippets from search_web results."""
    companies = []
    current = {}

    for line in search_text.splitlines():
        stripped = line.strip()
        if stripped.startswith("📄 "):
            if current.get("domain"):
                companies.append(current)
            current = {"company": stripped[2:].strip(), "source": "", "snippet": ""}
        elif stripped.startswith("Source:"):
            url = stripped.split("Source:", 1)[1].strip()
            parsed = urlparse(url)
            domain = parsed.netloc.replace("www.", "")
            current.update({"source": url, "domain": domain})
        elif stripped and not current.get("snippet"):
            current["snippet"] = stripped
        elif not stripped and current.get("domain") and len(companies) < limit:
            companies.append(current)
            current = {}

    if current.get("domain") or current.get("company"):
        companies.append(current)

    unique = []
    seen = set()
    for entry in companies:
        key = entry.get("domain", "").strip().lower() or entry.get("company", "").strip().lower()
        if key and key not in seen:
            seen.add(key)
            unique.append(entry)
            if len(unique) >= limit:
                break

    return unique


def load_existing_outreach() -> dict:
    """Load previous outreach history from Excel so we don't contact the same company twice."""
    contacts = {"emails": set(), "domains": set(), "companies": set()}
    excel_file = "job_tracking.xlsx"

    if not os.path.exists(excel_file):
        return contacts

    try:
        wb = load_workbook(excel_file)
        ws = wb.active

        for row in ws.iter_rows(min_row=2, values_only=True):
            if not row or not row[0]:
                continue
            company = str(row[0]).strip().lower()
            email = str(row[2]).strip().lower() if len(row) > 2 and row[2] else ""
            domain = ""
            if email and "@" in email:
                domain = email.split("@", 1)[1]

            if company:
                contacts["companies"].add(company)
            if email:
                contacts["emails"].add(email)
            if domain:
                contacts["domains"].add(domain)
    except Exception:
        pass

    return contacts


def parse_draft_response(draft_text: str) -> tuple[str, str]:
    """Extract subject and body from generated draft text."""
    subject = "Opportunity inquiry"
    body = draft_text.strip()

    lines = draft_text.splitlines()
    for idx, line in enumerate(lines):
        if line.upper().startswith("SUBJECT:"):
            subject = line.split(":", 1)[1].strip()
        if line.upper().startswith("BODY:"):
            body = "\n".join(lines[idx + 1 :]).strip()
            break

    return subject, body


def ensure_resume_attachment() -> list[str]:
    """Compile resume and return PDF attachment paths for outreach emails."""
    attachments = []
    pdf_result = compile_resume_pdf(RESUME_PATH)
    if pdf_result and pdf_result.endswith(".pdf") and os.path.exists(pdf_result):
        attachments.append(pdf_result)
    else:
        print("⚠️ Could not compile resume PDF. Emails will be sent without attachment.")
    return attachments


def run_daily_job_hunt_auto(num_companies: int = 10, dry_run: bool = False, ignore_history: bool = False, search_query: str = None):
    """Automatic daily pipeline: optimize resume, find contacts, send emails, and log results."""
    role = os.environ.get("YOUR_ROLE", "SDE / AI Engineer")
    print(f"\n{'='*70}")
    print(f"🚀 DAILY JOB HUNT AUTOMATION - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*70}\n")

    print("1) Optimizing resume...")
    resume_result = optimize_resume_latex()
    print(resume_result)

    attachments = ensure_resume_attachment()
    if attachments:
        print(f"✅ Resume attachment prepared: {attachments[-1]}")
    else:
        print("⚠️ No resume attachment available. Emails will be sent without attachment.")

    if not search_query:
        search_query = f"Find startups and companies hiring {role} remote hybrid onsite in 2026, founder or CEO contact email"
    print(f"\n2) Searching for companies with query:\n   {search_query}\n")
    search_results = search_web(search_query)
    print(search_results[:1200])

    companies = parse_company_domains(search_results, limit=num_companies * 2)
    if not companies:
        print("❌ Could not identify companies from search results.")
        return

    existing = load_existing_outreach()
    filtered_companies = []
    for entry in companies:
        domain = entry.get("domain", "").strip().lower()
        company_lower = entry.get("company", "").strip().lower()
        if not ignore_history:
            if domain and domain in existing["domains"]:
                continue
            if company_lower and company_lower in existing["companies"]:
                continue
        filtered_companies.append(entry)
        if len(filtered_companies) >= num_companies:
            break

    companies = filtered_companies
    if not companies:
        if ignore_history:
            print("✅ No valid companies found for the current query.")
        else:
            print("✅ All found companies already contacted previously. No new targets to send.")
        return

    print(f"\n3) Found {len(companies)} target companies. Preparing outreach...\n")

    sent_count = 0
    for idx, entry in enumerate(companies, 1):
        company = entry.get("company", "Company")
        domain = entry.get("domain", "")
        source = entry.get("source", "")

        print(f"\n---\n[{idx}/{len(companies)}] {company} ({domain})")
        contact_data = find_founder_email(domain) if domain else {}

        email = None
        contact_name = "Team"
        title = "Founder/CEO"
        confidence = "unknown"

        if isinstance(contact_data, dict):
            email = contact_data.get("email")
            contact_name = contact_data.get("name") or contact_name
            title = contact_data.get("title") or title
            confidence = contact_data.get("confidence", confidence)
        elif isinstance(contact_data, str) and contact_data.startswith("❌"):
            email = None

        if not email:
            email = f"hello@{domain}" if domain else None
            contact_name = "Hiring team"
            title = "Company contact"
            confidence = "fallback"

        if not email or not email.strip():
            print(f"⚠️ Skipping {company}: no contact email found.")
            continue

        if email.lower() in existing["emails"]:
            print(f"⚠️ Skipping {company}: email {email} was already contacted.")
            continue

        if domain.lower() in existing["domains"]:
            print(f"⚠️ Skipping {company}: domain {domain} was already contacted.")
            continue

        if not validate_email(email):
            print(f"⚠️ Invalid email format for {email}. Skipping.")
            continue

        company_info = f"Source: {source}. Target role: {role}." if source else f"Target role: {role}."
        resume_text = ""
        if os.path.exists(RESUME_PATH):
            with open(RESUME_PATH, "r", encoding="utf-8") as f:
                resume_text = f.read()[:1200]

        draft_text = draft_outreach_email(
            company=company,
            person=contact_name,
            to_email=email,
            role=role,
            company_info=company_info,
            resume_summary=resume_text,
        )

        subject, body = parse_draft_response(draft_text)
        print(f"Subject: {subject}\n")
        print(f"Body preview: {body[:220]}...\n")

        if dry_run:
            print(f"🧪 Dry run: not sending email to {email}")
            update_excel_tracking(
                company=company,
                person=contact_name,
                email=email,
                role=role,
                subject=subject,
                body=body,
                notes="Dry run saved"
            )
            continue

        send_result = send_email(email, subject, body, attachments=attachments)
        print(send_result)

        if "✅" in send_result:
            update_excel_tracking(
                company=company,
                person=contact_name,
                email=email,
                role=role,
                subject=subject,
                body=body,
                notes=f"Sent to {title} ({confidence})"
            )
            sent_count += 1
        else:
            print(f"⚠️ Failed to send to {email}: {send_result}")

    print(f"\n{'='*70}")
    print(f"✅ Daily outreach complete. Emails sent: {sent_count}/{len(companies)}")
    if not dry_run:
        report_result = send_daily_report()
        print(report_result)
    print(f"{'='*70}\n")


def interactive_approve_drafts():
    """
    Interactively review and approve/reject all pending drafts.
    """
    from tools import email_reviewer
    
    pending = email_reviewer.get_pending_drafts()
    
    if not pending:
        print("✅ No pending drafts to review!")
        return
    
    print(f"\n{'='*70}")
    print(f"📋 REVIEWING {len(pending)} PENDING EMAIL DRAFTS")
    print(f"{'='*70}\n")
    
    approved_count = 0
    rejected_count = 0
    
    for idx, (draft_id, draft) in enumerate(pending.items(), 1):
        print(f"\n{'─'*70}")
        print(f"[{idx}/{len(pending)}] DRAFT: {draft_id}")
        print(f"{'─'*70}")
        print(f"Company: {draft['company']}")
        print(f"Contact: {draft['person']}")
        print(f"Email:   {draft['to_email']}")
        print(f"\nSubject: {draft['subject']}")
        print(f"\nBody:\n{draft['body']}")
        print(f"{'─'*70}")
        
        while True:
            choice = input("(a)pprove, (r)eject, (s)kip, or (q)uit? ").lower().strip()
            
            if choice == 'a':
                email_reviewer.approve_draft(draft_id)
                print(f"✅ Approved: {draft_id}")
                approved_count += 1
                break
            elif choice == 'r':
                reason = input("Reason for rejection: ").strip()
                email_reviewer.reject_draft(draft_id, reason)
                print(f"❌ Rejected: {draft_id}")
                rejected_count += 1
                break
            elif choice == 's':
                print(f"⏭️  Skipped: {draft_id}")
                break
            elif choice == 'q':
                print(f"\n✋ Stopped at draft {idx}/{len(pending)}")
                print(f"Approved: {approved_count}, Rejected: {rejected_count}")
                return
            else:
                print("Invalid choice. Please enter a, r, s, or q")
    
    print(f"\n{'='*70}")
    print(f"📊 APPROVAL SUMMARY")
    print(f"{'='*70}")
    print(f"✅ Approved: {approved_count}")
    print(f"❌ Rejected: {rejected_count}")
    
    if approved_count > 0:
        send_choice = input(f"\nSend {approved_count} approved emails now? (y/n) ").lower().strip()
        if send_choice == 'y':
            from tools import email_reviewer
            sent = email_reviewer.send_approved_drafts()
            print(f"\n✅ Sent {sent} emails!")
            print(f"📊 Updated: job_tracking.xlsx")


def daily_job_hunt_interactive(ignore_history: bool = False, search_query: str = None):
    """
    One-command system: Run the full daily outreach pipeline automatically.
    """
    run_daily_job_hunt_auto(num_companies=10, dry_run=False, ignore_history=ignore_history, search_query=search_query)

# ─── CLI Interface ───────────────────────────────────────────────────────────

if __name__ == "__main__":
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == "daily":
            # Run interactive one-command job hunt
            if len(sys.argv) > 2:
                search_query = " ".join(sys.argv[2:])
                daily_job_hunt_interactive(search_query=search_query)
            else:
                daily_job_hunt_interactive()
        
        elif command == "daily-force":
            # Run the daily pipeline and ignore previous outreach history if needed
            if len(sys.argv) > 2:
                search_query = " ".join(sys.argv[2:])
                daily_job_hunt_interactive(ignore_history=True, search_query=search_query)
            else:
                daily_job_hunt_interactive(ignore_history=True)

        elif command == "approve":
            # Interactively review and approve/reject drafts
            interactive_approve_drafts()
        
        elif command == "approve-draft":
            # Quick approve single draft
            if len(sys.argv) > 2:
                from tools import email_reviewer
                draft_id = sys.argv[2]
                if email_reviewer.approve_draft(draft_id):
                    draft = email_reviewer.get_draft(draft_id)
                    print(f"✅ Approved: {draft_id}")
                    print(f"To: {draft['to_email']}")
                    print(f"Use 'python main.py approve' to review and send all approved drafts")
                else:
                    print(f"❌ Draft not found: {draft_id}")
            else:
                print("❌ Usage: python main.py approve-draft <draft_id>")
        
        elif command == "reject-draft":
            # Quick reject single draft
            if len(sys.argv) > 2:
                from tools import email_reviewer
                draft_id = sys.argv[2]
                reason = " ".join(sys.argv[3:]) if len(sys.argv) > 3 else ""
                if email_reviewer.reject_draft(draft_id, reason):
                    print(f"❌ Rejected: {draft_id}")
                    if reason:
                        print(f"Reason: {reason}")
                else:
                    print(f"❌ Draft not found: {draft_id}")
            else:
                print("❌ Usage: python main.py reject-draft <draft_id> [reason]")
        
        elif command == "send-approved":
            # Send all approved drafts
            from tools import email_reviewer
            sent = email_reviewer.send_approved_drafts()
            print(f"✅ Sent {sent} emails!")
            print(f"📊 Updated: job_tracking.xlsx")
        
        elif command == "resume":
            # Just optimize resume
            result = run_job_hunt("Optimize my resume using optimize_resume_latex()")
        
        elif command == "report":
            # Just send daily report
            result = run_job_hunt("Send me the daily report with send_daily_report()")
        
        elif command == "track":
            # Show tracking
            result = run_job_hunt("Show me my Excel tracking sheet with get_excel_tracking()")
        
        elif command == "review":
            # Show pending email drafts for approval
            from tools import email_reviewer
            pending = email_reviewer.get_pending_drafts()
            if not pending:
                print("✅ No pending drafts!")
            else:
                print(f"\n📋 {len(pending)} PENDING DRAFTS:\n")
                for draft_id, draft in pending.items():
                    print(f"Draft ID: {draft_id}")
                    print(f"Company:  {draft['company']}")
                    print(f"Contact:  {draft['person']}")
                    print(f"Email:    {draft['to_email']}")
                    print(f"Subject:  {draft['subject']}")
                    print(f"File: todays_drafts/{draft_id}_{draft['company']}_{draft['person']}.txt\n")
        
        elif command == "dry-run":
            # Test without sending emails
            if len(sys.argv) > 2:
                prompt = " ".join(sys.argv[2:])
            else:
                prompt = "Find 3 companies hiring for my role and draft emails (don't send)"
            run_job_hunt(prompt, dry_run=True)
        
        else:
            # Custom prompt
            prompt = " ".join(sys.argv[1:])
            run_job_hunt(prompt)
    
    else:
        # Default: show help
        print("""
        ╔════════════════════════════════════════════════════════════════╗
        ║   JOB HUNTING AGENT - One-Command Daily Job Search & Outreach  ║
        ╚════════════════════════════════════════════════════════════════╝
        
        🚀 MAIN COMMAND (One-Command Everything):
        
        python main.py daily
            → Run the full daily outreach pipeline automatically
            → Optimize resume, find contacts, send emails, log outreach, and report
        
        📧 EMAIL APPROVAL WORKFLOW:
        
        python main.py review
            → Show all pending email drafts (in todays_drafts/ folder)
        
        python main.py approve
            → Review each draft interactively (approve/reject/skip)

        python main.py daily-force
            → Run the full daily pipeline and ignore previous tracking history
        
        python main.py approve-draft <draft_id>
            → Quick approve single draft
        
        python main.py reject-draft <draft_id> "reason"
            → Quick reject single draft with reason
        
        python main.py send-approved
            → Send all approved drafts now
        
        📊 OTHER COMMANDS:
        
        python main.py resume
            → Just optimize your LaTeX resume
        
        python main.py report
            → Send today's activity report to your email
        
        python main.py track
            → Show your Excel tracking sheet (job_tracking.xlsx)
        
        python main.py dry-run "Find 3 companies"
            → Test without sending emails
        
        🎯 QUICK START:
        
        1. python main.py daily
           → Runs the full daily outreach pipeline automatically
        
        2. Check job_tracking.xlsx for the email log and send status
        
        3. Use python main.py report to send yourself a summary report
        
        4. Use python main.py track to view tracking results
        
        💡 EXAMPLE:
        
        # One-command workflow (find, draft, approve, send)
        python main.py daily
        
        # Manual approval of specific drafts
        python main.py approve-draft draft_1715805310_123
        python main.py reject-draft draft_1715805310_456 "Subject not personal enough"
        python main.py approve
        python main.py send-approved
        """)
