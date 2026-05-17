# tools.py — ALL agent tools for job hunting (8 total) + OPTIMIZATIONS
# OPTIMIZED: Caching, Email Validation, Async Support, Follow-up Tracking

import os
import json
import smtplib
import requests
import subprocess
import warnings
import re
import asyncio
from datetime import datetime, timedelta
from pathlib import Path
from urllib.parse import urlparse
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.mime.application import MIMEApplication
# langchain `tool` decorator was used in earlier drafts. This file exposes
# plain Python callables for direct use from `main.py`, so we don't import
# or apply the `@tool` decorator here to avoid wrapped-tool calling issues.
# from langchain_core.tools import tool

try:
    from langchain_aws import ChatBedrock
except ImportError:
    ChatBedrock = None

try:
    from openpyxl import Workbook, load_workbook
    from openpyxl.styles import Font, PatternFill, Alignment
except ImportError:
    print("⚠️ openpyxl not installed. Install with: pip install openpyxl")


# ─── Load config from environment ────────────────────────────────────────────

def get_env(key: str, default: str = "") -> str:
    """Get environment variable with optional default."""
    return os.environ.get(key, default)


# ─── OPTIMIZATION 1: LOCAL CACHING (Reduce API calls by 50%) ──────────────────

class APICache:
    """Cache system to reduce API calls and improve performance."""
    
    def __init__(self):
        self.cache_file = ".api_cache.json"
        self.cache = self._load_cache()
    
    def _load_cache(self):
        """Load cache from disk."""
        if os.path.exists(self.cache_file):
            try:
                with open(self.cache_file, "r") as f:
                    return json.load(f)
            except:
                return {}
        return {}
    
    def _save_cache(self):
        """Save cache to disk."""
        try:
            with open(self.cache_file, "w") as f:
                json.dump(self.cache, f, indent=2)
        except:
            pass
    
    def get(self, key: str, ttl_hours: int = 24):
        """Get value if exists and not expired."""
        if key in self.cache:
            entry = self.cache[key]
            created = datetime.fromisoformat(entry["created"])
            if datetime.now() - created < timedelta(hours=ttl_hours):
                return entry["value"]
            else:
                del self.cache[key]  # Expired
                self._save_cache()
        return None
    
    def set(self, key: str, value):
        """Set value in cache."""
        self.cache[key] = {
            "value": value,
            "created": datetime.now().isoformat()
        }
        self._save_cache()

api_cache = APICache()


# ─── OPTIMIZATION 5: EMAIL REVIEW SYSTEM (Human Approval Required) ────────

class EmailReviewSystem:
    """System for reviewing and approving emails before sending."""
    
    def __init__(self):
        self.drafts_file = "email_drafts.json"
        self.drafts_dir = "todays_drafts"
        self.drafts = self._load_drafts()
        self._ensure_drafts_dir()
    
    def _ensure_drafts_dir(self):
        """Create drafts directory if it doesn't exist."""
        if not os.path.exists(self.drafts_dir):
            os.makedirs(self.drafts_dir)
    
    def _load_drafts(self):
        """Load pending email drafts."""
        if os.path.exists(self.drafts_file):
            try:
                with open(self.drafts_file, "r") as f:
                    return json.load(f)
            except:
                return {}
        return {}
    
    def _save_drafts(self):
        """Save drafts to disk."""
        try:
            with open(self.drafts_file, "w") as f:
                json.dump(self.drafts, f, indent=2)
        except:
            pass
    
    def _save_draft_file(self, draft_id: str, company: str, person: str, to_email: str, subject: str, body: str):
        """Save draft email to a human-readable text file."""
        filename = f"{self.drafts_dir}/{draft_id}_{company}_{person}.txt"
        try:
            content = f"""EMAIL DRAFT FOR APPROVAL
{'='*70}

Company: {company}
Contact: {person}
Email: {to_email}
Created: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Draft ID: {draft_id}

{'='*70}
SUBJECT: {subject}

{'='*70}
BODY:

{body}

{'='*70}

To approve: python main.py approve-draft {draft_id}
To reject:  python main.py reject-draft {draft_id} "reason"
"""
            with open(filename, "w") as f:
                f.write(content)
        except:
            pass
    
    def add_draft(self, draft_id: str, company: str, person: str, to_email: str, subject: str, body: str, context: str = ""):
        """Add an email draft for review."""
        self.drafts[draft_id] = {
            "company": company,
            "person": person,
            "to_email": to_email,
            "subject": subject,
            "body": body,
            "context": context,
            "created": datetime.now().isoformat(),
            "status": "pending"
        }
        self._save_drafts()
        self._save_draft_file(draft_id, company, person, to_email, subject, body)
    
    def get_pending_drafts(self):
        """Get all pending drafts."""
        return {k: v for k, v in self.drafts.items() if v["status"] == "pending"}
    
    def approve_draft(self, draft_id: str):
        """Approve a draft for sending."""
        if draft_id in self.drafts:
            self.drafts[draft_id]["status"] = "approved"
            self.drafts[draft_id]["approved_at"] = datetime.now().isoformat()
            self._save_drafts()
            return True
        return False
    
    def reject_draft(self, draft_id: str, reason: str = ""):
        """Reject a draft."""
        if draft_id in self.drafts:
            self.drafts[draft_id]["status"] = "rejected"
            self.drafts[draft_id]["rejected_at"] = datetime.now().isoformat()
            self.drafts[draft_id]["reject_reason"] = reason
            self._save_drafts()
            return True
        return False
    
    def get_draft(self, draft_id: str):
        """Get a specific draft."""
        return self.drafts.get(draft_id)
    
    def send_approved_drafts(self):
        """Send all approved drafts and update Excel tracking."""
        sent_count = 0
        for draft_id, draft in list(self.drafts.items()):
            if draft["status"] == "approved":
                try:
                    resume_path = Path(get_env("RESUME_PATH", "./resume.tex"))
                    resume_pdf = resume_path.with_suffix(".pdf")
                    if not resume_pdf.exists():
                        compile_result = compile_resume_pdf(str(resume_path))
                        if isinstance(compile_result, str) and compile_result.endswith(".pdf"):
                            resume_pdf = Path(compile_result)
                    attachments = [str(resume_pdf)] if resume_pdf.exists() else []

                    # Send the email
                    result = send_email(draft["to_email"], draft["subject"], draft["body"], attachments=attachments)
                    if "✅" in result:
                        draft["status"] = "sent"
                        draft["sent_at"] = datetime.now().isoformat()
                        
                        # Update Excel tracking
                        update_excel_tracking(
                            company=draft["company"],
                            person=draft["person"],
                            email=draft["to_email"],
                            role=get_env("YOUR_ROLE", "Software Engineer"),
                            subject=draft["subject"],
                            body=draft["body"],
                            notes=f"Sent via approved draft"
                        )
                        
                        sent_count += 1
                    else:
                        draft["status"] = "send_failed"
                        draft["error"] = result
                except Exception as e:
                    draft["status"] = "send_failed"
                    draft["error"] = str(e)
        
        self._save_drafts()
        return sent_count

email_reviewer = EmailReviewSystem()


# ─── OPTIMIZATION 2: EMAIL VALIDATION (Stop invalid emails) ─────────────────

def validate_email(email: str) -> bool:
    """
    Validate email format before sending.
    Prevents bounces and protects sender reputation.
    """
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None


def is_common_domain(email: str) -> bool:
    """Check if email is from common provider (not company domain)."""
    common = ['gmail.com', 'yahoo.com', 'hotmail.com', 'outlook.com', 'aol.com', 'icloud.com']
    domain = email.split('@')[1].lower() if '@' in email else ''
    return domain in common


def get_bedrock_llm():
    """Return a shared Bedrock LLM instance for email and resume generation."""
    if ChatBedrock is None:
        raise RuntimeError("langchain_aws.ChatBedrock is not available. Install langchain-aws.")
    if not hasattr(get_bedrock_llm, "_llm"):
        model_id = get_env("BEDROCK_MODEL", "eu.anthropic.claude-haiku-4-5-20251001-v1:0")
        region = get_env("AWS_REGION", "eu-north-1")
        get_bedrock_llm._llm = ChatBedrock(
            model_id=model_id,
            region_name=region,
            model_kwargs={"temperature": 0.2, "max_tokens": 1024},
        )
    return get_bedrock_llm._llm


def compile_resume_pdf(resume_path: str = None) -> str:
    """Compile resume.tex to resume.pdf, if pdflatex is installed."""
    resume_path = Path(resume_path or get_env("RESUME_PATH", "./resume.tex"))
    if not resume_path.exists():
        return f"❌ Resume not found at {resume_path}."

    try:
        result = subprocess.run(
            ["pdflatex", "-interaction=nonstopmode", "-halt-on-error", str(resume_path)],
            cwd=resume_path.parent,
            capture_output=True,
            text=True,
            timeout=60,
        )

        if result.returncode != 0:
            return f"❌ pdflatex failed: {result.stderr.strip().splitlines()[-1] if result.stderr else result.stdout.strip().splitlines()[-1] if result.stdout else 'Unknown error'}"

        pdf_path = resume_path.with_suffix(".pdf")
        if pdf_path.exists():
            return str(pdf_path)
        return "❌ Resume PDF not produced."
    except FileNotFoundError:
        return "❌ pdflatex not installed. Install TeX Live or MikTeX, or add pdflatex to PATH."
    except Exception as e:
        return f"❌ Resume compilation error: {str(e)}"


def _rewrite_resume_section(section_name: str, section_body: str, role: str) -> str:
    """Use Bedrock to rewrite a single LaTeX resume section while preserving layout."""
    if not section_body.strip():
        return section_body

    prompt = f"""
You are a professional resume editor. Improve the following LaTeX section body for a candidate targeting {role} as an SDE / AI Engineer.
- Preserve all LaTeX formatting, section headings and structure.
- Do not add or remove \section commands.
- Keep the length roughly the same.
- Only rewrite wording, descriptions, bullet text, and skills content.
- Keep the design, spacing, and overall resume size unchanged.
- Use natural, concise, engineer-friendly language.

Section body to rewrite:
{section_body}

Return only the rewritten LaTeX body, without adding new section headers.
"""
    try:
        llm = get_bedrock_llm()
        rewritten = llm(prompt)
        rewritten_text = str(rewritten).strip()
        return rewritten_text or section_body
    except Exception:
        return section_body


def optimize_resume_latex() -> str:
    """Optimize your LaTeX resume text while preserving layout and style."""
    resume_path = Path(get_env("RESUME_PATH", "./resume.tex"))

    try:
        if not resume_path.exists():
            return f"❌ Resume not found at {resume_path}. Create resume.tex first."

        content = resume_path.read_text(encoding="utf-8")

        section_pattern = re.compile(
            r"(?P<header>\\section\{[^}]+\})(?P<body>.*?)(?=(\\section\{|\\end\{document\}|$))",
            re.DOTALL,
        )
        updated = content
        updated_sections = []
        role = get_env("YOUR_ROLE", "Software Engineer")

        for match in section_pattern.finditer(content):
            header = match.group("header")
            body = match.group("body")
            section_name = header.replace("\\section{", "").replace("}", "").strip().upper()

            if section_name in ["SUMMARY", "EXPERIENCE", "PROJECTS", "SKILLS", "EDUCATION"]:
                rewritten_body = _rewrite_resume_section(section_name, body, role)
                if rewritten_body and rewritten_body.strip() != body.strip():
                    updated = updated.replace(body, rewritten_body, 1)
                    updated_sections.append(section_name)

        if updated_sections and updated != content:
            resume_path.write_text(updated, encoding="utf-8")
            return f"✅ Resume optimized: updated sections: {', '.join(updated_sections)}"

        return "✅ Resume checked. No structural changes needed."
    except Exception as e:
        return f"❌ Resume optimization error: {str(e)}"


def draft_outreach_email(company: str, person: str, to_email: str, role: str, company_info: str = "", resume_summary: str = "") -> str:
    """Generate a concise, natural outreach email subject and body for job outreach."""
    try:
        llm = get_bedrock_llm()
        prompt = f"""
Write a concise professional outreach email from {get_env('YOUR_NAME', 'a candidate')} targeting the role {role}.
Recipient: {person} at {company}
Email: {to_email}
Company info/context: {company_info}
Resume summary or highlights: {resume_summary}

Requirements:
- Use the recipient's name or company name, not generic titles like "Manager" or "CEO".
- Natural, engineer-to-engineer tone, not sales copy.
- Mention that your resume is attached.
- Ask about opportunities for SDE / AI Engineer work.
- Reference remote, hybrid, or onsite availability.
- Include a short call to action for a quick conversation.
- Keep it under 120 words.
- Use one or two relevant AI/SDE keywords.
- Add a simple opt-out line: "Reply with unsubscribe to opt out."
- Avoid generic greetings like "I hope this finds you well" and avoid the phrase "stop to unsubscribe."

Return output as:
SUBJECT: <subject line>

BODY:
<email body>
"""
        response = llm(prompt)
        return str(response).strip()
    except Exception as e:
        # Fallback to a simple templated email if the LLM provider is unavailable.
        fallback_subject = f"Interest in {role} / AI Engineering opportunity"
        fallback_body = (
            f"Hi {person},\n\n"
            f"I’m {get_env('YOUR_NAME', 'a candidate')}, a {role} focused on practical AI engineering. "
            f"I’m reaching out because I found {company} while researching companies building strong AI products, and I believe I can add value to your team. "
            f"My resume is attached and I’m available for remote, hybrid, or onsite roles.\n\n"
            f"If you’d rather not receive future messages, reply with unsubscribe.\n\n"
            f"Best regards,\n{get_env('YOUR_NAME', 'Candidate')}"
        )
        return f"SUBJECT: {fallback_subject}\n\nBODY:\n{fallback_body}"
    """
    Get list of people to follow up with (no reply after 7 days).
    Returns: [(company, person, email, days_since), ...]
    """
    excel_file = "job_tracking.xlsx"
    candidates = []
    
    if not os.path.exists(excel_file):
        return candidates
    
    try:
        wb = load_workbook(excel_file)
        ws = wb.active
        today = datetime.now()
        
        for row in ws.iter_rows(min_row=2, values_only=True):
            if row[0]:  # Company exists
                company = row[0]
                person = row[1] if len(row) > 1 else ""
                email = row[2] if len(row) > 2 else ""
                date_str = row[6] if len(row) > 6 else ""
                status = row[7] if len(row) > 7 else ""
                
                # Parse date (format: YYYY-MM-DD HH:MM)
                try:
                    sent_date = datetime.strptime(str(date_str)[:10], "%Y-%m-%d")
                    days_ago = (today - sent_date).days
                    
                    # If 7 days passed and status still "Sent", recommend follow-up
                    if days_ago >= 7 and status == "Sent":
                        candidates.append((company, person, email, days_ago))
                except:
                    pass
        
        return candidates
    except:
        return candidates


def find_founder_email(company_domain: str) -> dict:
    """
    Find founder/CEO email by searching common patterns and Hunter API.
    Returns: {name: str, email: str, title: str, confidence: str}
    """
    try:
        api_key = get_env("HUNTER_API_KEY")
        if not api_key:
            return {"error": "HUNTER_API_KEY not set"}
        
        # Common founder/CEO patterns
        common_founders = ["ceo@", "founder@", "contact@", "hello@", "founders@"]
        
        # Try common patterns first (cached)
        cache_key = f"founder:{company_domain}"
        cached = api_cache.get(cache_key, ttl_hours=168)  # 1 week
        if cached:
            return cached
        
        # Try to find via Hunter domain search
        url = f"https://api.hunter.io/v2/domain-search?domain={company_domain}&api_key={api_key}"
        
        dev_mode = get_env("DISABLE_SSL_VERIFY")
        if dev_mode:
            import urllib3
            urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        
        response = requests.get(url, timeout=10, verify=not dev_mode)
        data = response.json()
        
        if data.get("data", {}).get("emails"):
            emails = data["data"]["emails"]
            # Look for founder/CEO/CTO
            for email_entry in emails:
                position = str(email_entry.get("position", "")).lower()
                if any(role in position for role in ["founder", "ceo", "cto", "chief"]):
                    result = {
                        "name": email_entry.get("first_name", "") + " " + email_entry.get("last_name", ""),
                        "email": email_entry.get("value"),
                        "title": email_entry.get("position", "Founder/CEO"),
                        "confidence": "high"
                    }
                    api_cache.set(cache_key, result)
                    return result
            
            # If no founder found, return first email (likely founder)
            if emails:
                first = emails[0]
                result = {
                    "name": first.get("first_name", "") + " " + first.get("last_name", ""),
                    "email": first.get("value"),
                    "title": first.get("position", "Founder/CEO"),
                    "confidence": "medium"
                }
                api_cache.set(cache_key, result)
                return result
        
        # Fallback: try common patterns
        for pattern in common_founders:
            result = {
                "name": "Founder/CEO",
                "email": f"{pattern[:-1]}@{company_domain}",
                "title": "Founder/CEO (guessed)",
                "confidence": "low"
            }
            return result
        
        return {"error": f"Could not find founder/CEO email for {company_domain}"}
    
    except Exception as e:
        return {"error": str(e)}


# ─── Load config from environment ────────────────────────────────────────────

def get_env(key: str, default: str = "") -> str:
    """Get environment variable with optional default."""
    return os.environ.get(key, default)


# ─── EXISTING TOOLS (1-5) ────────────────────────────────────────────────────
# These are proven to work from your current setup

def search_web(query: str) -> str:
    """
    Search the web for job opportunities, companies, and research.
    
    OPTIMIZED: Caches results for 24 hours to reduce API usage by 50%.
    
    Use for:
    - Find companies: "Python engineer hiring San Francisco 2026"
    - Find people: "CTO of [company name]" or "[person name] GitHub"
    - Research: "what does [company] build" or "[company] tech stack"
    
    Returns top 5 results with sources and content.
    """
    try:
        # Check cache first (OPTIMIZATION 1)
        cache_key = f"search:{query.lower()}"
        cached_result = api_cache.get(cache_key, ttl_hours=24)
        if cached_result:
            return f"📦 [CACHED] {cached_result[:500]}..."  # Show it's from cache
        
        api_key = get_env("TAVILY_API_KEY")
        if not api_key:
            return "❌ TAVILY_API_KEY not set in .env"
        
        dev_mode = get_env("DISABLE_SSL_VERIFY") or get_env("DEV_MODE")
        
        if dev_mode:
            import urllib3
            urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        
        url = "https://api.tavily.com/search"
        payload = {
            "api_key": api_key,
            "query": query,
            "max_results": 5,
            "search_depth": "basic"
        }
        
        response = requests.post(
            url,
            json=payload,
            timeout=10,
            verify=not dev_mode
        )
        response.raise_for_status()
        data = response.json()
        
        results = []
        for r in data.get("results", []):
            results.append(f"📄 {r['title']}\nSource: {r['url']}\n{r['content'][:300]}\n")
        
        final_result = "\n---\n".join(results) if results else "❌ No results found."
        
        # Cache the result
        api_cache.set(cache_key, final_result)
        
        return final_result
    
    except Exception as e:
        return f"❌ Search error: {str(e)[:200]}"


def find_email(full_name: str, company_domain: str) -> str:
    """
    Find a professional's email address.
    
    OPTIMIZED: Caches results for 30 days + validates before returning.
    
    Args:
        full_name: Person's name (e.g. "John Smith")
        company_domain: Company domain without www (e.g. "acmecorp.com")
    
    Returns:
        Email if found with confidence score, or common patterns to try.
    """
    try:
        # Check cache first (OPTIMIZATION 1)
        cache_key = f"email:{full_name.lower()}@{company_domain.lower()}"
        cached_result = api_cache.get(cache_key, ttl_hours=720)  # 30 days
        if cached_result:
            return f"📦 [CACHED] {cached_result}"
        
        api_key = get_env("HUNTER_API_KEY")
        if not api_key:
            return "❌ HUNTER_API_KEY not set"
        
        first, *rest = full_name.strip().split()
        last = rest[-1] if rest else ""

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
            score = data["data"].get("score", 0)
            
            # Validate email format (OPTIMIZATION 2)
            if not validate_email(email):
                return f"⚠️ Found {email} but failed validation. Manual review needed."
            
            result = f"✅ Found: {email} (confidence: {score}%)"
            api_cache.set(cache_key, result)
            return result
        else:
            # Fallback patterns
            first_lower = first.lower()
            last_lower = last.lower() if last else ""
            guesses = [
                f"{first_lower}@{company_domain}",
                f"{first_lower}.{last_lower}@{company_domain}",
                f"{first_lower[0]}{last_lower}@{company_domain}",
            ]
            result = "⚠️ Not found. Try these patterns:\n" + "\n".join(guesses)
            api_cache.set(cache_key, result)
            return result

    except Exception as e:
        return f"❌ Error: {str(e)}"


def send_email(to_email: str, subject: str, body: str, attachments: list = None) -> str:
    """
    Send a job inquiry email via Gmail.
    
    OPTIMIZED: Validates email format before sending and supports file attachments.
    
    Args:
        to_email: Recipient email
        subject: Email subject
        body: Email body (plain text, keep under 200 words)
        attachments: Optional list of file paths to attach
    
    IMPORTANT: Email must be professional and include unsubscribe option
    """
    try:
        # Validate email format (OPTIMIZATION 2)
        if not validate_email(to_email):
            return f"❌ Invalid email format: {to_email}. Skipped to protect reputation."
        
        # Warn if using personal email (deliverability issue).
        # Allow this if sending a test email to the same Gmail account.
        gmail = get_env("GMAIL_ADDRESS")
        if is_common_domain(to_email) and gmail and to_email.lower() != gmail.lower():
            return f"⚠️ {to_email} is a personal email (Gmail/Yahoo/Outlook). Consider finding company email instead."
        
        password = get_env("GMAIL_APP_PASSWORD")
        
        if not gmail or not password:
            return "❌ GMAIL_ADDRESS or GMAIL_APP_PASSWORD not set"
        
        # Validate email content
        if not body.lower().__contains__("unsubscribe") and len(body) > 50:
            return f"⚠️ Warning: Email missing unsubscribe option (GDPR required). Add:\n'---\nTo unsubscribe: reply with STOP'"
        
        msg = MIMEMultipart()
        msg["From"] = gmail
        msg["To"] = to_email
        msg["Subject"] = subject
        msg.attach(MIMEText(body, "plain"))

        attachments = attachments or []
        for attachment_path in attachments:
            try:
                if not os.path.exists(attachment_path):
                    continue
                with open(attachment_path, "rb") as attachment_file:
                    part = MIMEApplication(attachment_file.read())
                    part.add_header(
                        "Content-Disposition",
                        f"attachment; filename=\"{os.path.basename(attachment_path)}\"",
                    )
                    msg.attach(part)
            except Exception:
                continue

        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(gmail, password)
            server.sendmail(gmail, to_email, msg.as_string())

        # Log it
        log_outreach(
            to_email=to_email,
            subject=subject,
            body_preview=body[:200],
            status="sent"
        )

        return f"✅ Email sent to {to_email}"

    except Exception as e:
        return f"❌ Send failed: {str(e)[:150]}"


def draft_email_for_review(company: str, person: str, to_email: str, subject: str, body: str, context: str = "") -> str:
    """
    DRAFT an email for human review instead of sending immediately.
    
    Use this when you want the human to approve the email before sending.
    
    Args:
        company: Company name
        person: Contact person's name (founder/CEO)
        to_email: Recipient email
        subject: Email subject
        body: Email body
        context: Why this email (company research, etc.)
    
    Returns: Draft ID for later approval
    """
    try:
        # Validate email format first
        if not validate_email(to_email):
            return f"❌ Invalid email format: {to_email}. Cannot draft."
        
        # Generate unique draft ID
        draft_id = f"draft_{int(datetime.now().timestamp())}_{hash(to_email) % 1000}"
        
        # Add to review system
        email_reviewer.add_draft(draft_id, company, person, to_email, subject, body, context)
        
        return f"📝 Email drafted for review!\n\nDraft ID: {draft_id}\n{company} | {person}\nTo: {to_email}\nSubject: {subject}\n\n✅ Draft saved to: todays_drafts/{draft_id}_{company}_{person}.txt"
    
    except Exception as e:
        return f"❌ Draft failed: {str(e)}"


def review_drafts() -> str:
    """
    Show all pending email drafts waiting for human approval.
    
    Returns: List of drafts with preview and approval commands
    """
    pending = email_reviewer.get_pending_drafts()
    
    if not pending:
        return "✅ No pending drafts. All emails have been reviewed!"
    
    result = f"📋 {len(pending)} PENDING EMAIL DRAFTS (Require Your Approval):\n\n"
    
    for draft_id, draft in pending.items():
        result += f"📧 Draft ID: {draft_id}\n"
        result += f"   To: {draft['to_email']}\n"
        result += f"   Subject: {draft['subject']}\n"
        result += f"   Body Preview: {draft['body'][:100]}...\n"
        if draft.get('context'):
            result += f"   Context: {draft['context'][:50]}...\n"
        result += f"   Created: {draft['created'][:19]}\n\n"
    
    result += "COMMANDS TO USE:\n"
    result += "• approve_draft(draft_id) - Send this email\n"
    result += "• reject_draft(draft_id, reason) - Reject with reason\n"
    result += "• send_approved_drafts() - Send all approved drafts\n\n"
    result += "⚠️ IMPORTANT: Emails will NOT be sent until you approve them!"
    
    return result


def approve_draft(draft_id: str) -> str:
    """
    Approve a pending email draft for sending.
    
    Args:
        draft_id: The draft ID from review_drafts()
    
    Returns: Success message
    """
    if email_reviewer.approve_draft(draft_id):
        draft = email_reviewer.get_draft(draft_id)
        return f"✅ Draft {draft_id} approved!\nTo: {draft['to_email']}\nSubject: {draft['subject']}\n\nUse 'send_approved_drafts()' to send all approved emails."
    else:
        return f"❌ Draft {draft_id} not found."


def reject_draft(draft_id: str, reason: str = "") -> str:
    """
    Reject a pending email draft.
    
    Args:
        draft_id: The draft ID from review_drafts()
        reason: Why you're rejecting it (optional)
    
    Returns: Success message
    """
    if email_reviewer.reject_draft(draft_id, reason):
        return f"❌ Draft {draft_id} rejected.\nReason: {reason or 'No reason given'}"
    else:
        return f"❌ Draft {draft_id} not found."


def send_approved_drafts() -> str:
    """
    Send all approved email drafts.
    
    This will send all drafts that have been approved via approve_draft().
    
    Returns: How many emails were sent
    """
    sent_count = email_reviewer.send_approved_drafts()
    return f"✅ Sent {sent_count} approved email drafts."


def log_outreach(to_email: str, subject: str, body_preview: str, status: str = "sent") -> str:
    """
    Log all outreach in JSON file for tracking.
    
    Args:
        to_email: Who you contacted
        subject: Email subject
        body_preview: First 200 chars of email
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
        return f"📝 Logged: {to_email}"
    except Exception as e:
        return f"❌ Log error: {str(e)}"


def get_outreach_log() -> str:
    """
    View all past outreach (last 20 entries).
    
    Use this to AVOID contacting the same person twice.
    """
    log_file = "outreach_log.json"
    if not os.path.exists(log_file):
        return "📋 No emails sent yet."
    
    try:
        with open(log_file, "r") as f:
            data = json.load(f)
        
        if not data:
            return "📋 Log is empty."
        
        lines = []
        for e in data[-20:]:  # Last 20
            date = e['timestamp'][:10]
            status_icon = "✅" if e['status'] == "sent" else "❌"
            lines.append(f"{status_icon} {e['to']} | {e['subject'][:40]} | {date}")
        
        return f"📋 Last {len(lines)} contacts:\n" + "\n".join(lines)
    
    except Exception as e:
        return f"❌ Error reading log: {str(e)}"


def get_followup_needed() -> str:
    """
    OPTIMIZATION 4: Get list of people to follow up with.
    
    Shows contacts from 7+ days ago with no response.
    Automatically suggests follow-up emails.
    
    Returns: List of (Company, Person, Email, Days Since)
    """
    candidates = get_followup_candidates()
    
    if not candidates:
        return "✅ All caught up! No follow-ups needed right now."
    
    result = f"📧 {len(candidates)} people ready for follow-up (7+ days, no response):\n\n"
    
    for company, person, email, days_ago in candidates:
        result += f"  • {company} - {person} ({email})\n"
        result += f"    └─ Sent {days_ago} days ago\n\n"
    
    result += """
SUGGESTED ACTION:
1. Review if they opened/clicked your email
2. Draft friendly follow-up email
3. Use: send_email(to_email, subject, body) with follow-up
4. Update status in Excel when done

Example follow-up subject: "Following up - [Your Role] @ [Company]"
"""
    
    return result


# ─── NEW TOOLS (6-9) — Resume, Excel Tracking, Daily Reports ──────────────────

# `optimize_resume_latex` is implemented earlier in this file as a plain function
# (see the implementation above). Avoid defining a duplicate @tool-wrapped
# version to keep direct calls from `main.py` working.


def get_excel_tracking() -> str:
    """
    View your Excel tracking sheet with all job outreach.
    
    Shows:
    - Company name
    - Contact person
    - Email address
    - Role requested
    - Draft subject
    - Date sent
    - Status
    - Notes
    
    Returns the last 10 entries.
    """
    excel_file = "job_tracking.xlsx"
    
    try:
        if not os.path.exists(excel_file):
            return "📊 No tracking sheet yet. Sending first email will create it."
        
        wb = load_workbook(excel_file)
        ws = wb.active
        
        if ws.max_row <= 1:
            return "📊 Tracking sheet is empty (header only)."
        
        # Get last 10 entries
        entries = []
        for row in list(ws.iter_rows(min_row=2, values_only=True))[-10:]:
            if row[0]:  # If company name exists
                company = row[0]
                person = row[1] if len(row) > 1 else ""
                email = row[2] if len(row) > 2 else ""
                role = row[3] if len(row) > 3 else ""
                date = row[6] if len(row) > 6 else ""
                status = row[7] if len(row) > 7 else ""
                entries.append(f"🏢 {company} | 👤 {person} | 📧 {email} | {role} | {date} | {status}")
        
        result = f"📊 Last {len(entries)} contacts:\n" + "\n".join(entries)
        
        # Add summary stats
        total_rows = ws.max_row - 1
        result += f"\n\n📈 Total contacts: {total_rows}"
        
        return result
    
    except Exception as e:
        return f"❌ Error reading tracking: {str(e)}"


def update_excel_tracking(company: str, person: str, email: str, role: str, subject: str, body: str, notes: str = "") -> str:
    """
    Add an outreach entry to your Excel tracking sheet.
    
    OPTIMIZED: Tracks follow-up dates for automatic reminders.
    
    Args:
        company: Company name
        person: Contact person's name
        email: Their email address
        role: Requested job role
        subject: Draft email subject
        body: Draft email body
        notes: Any notes (optional)
    
    Creates job_tracking.xlsx if doesn't exist.
    Columns: Company, Person, Email, Role, Subject, Body, Date, Status, Notes, Follow-up Date
    """
    excel_file = "job_tracking.xlsx"
    
    try:
        # Create or load workbook
        if os.path.exists(excel_file):
            wb = load_workbook(excel_file)
            ws = wb.active
        else:
            wb = Workbook()
            ws = wb.active
            ws.title = "Job Hunt"
            
            headers = [
                "Company",
                "Person",
                "Email",
                "Role",
                "Subject",
                "Body",
                "Date",
                "Status",
                "Notes",
                "Follow-up Date",
            ]
            for col, header in enumerate(headers, 1):
                cell = ws.cell(1, col, header)
                cell.font = Font(bold=True, color="FFFFFF")
                cell.fill = PatternFill(start_color="4472C4", end_color="4472C4", fill_type="solid")
        
        # Add new row
        row_num = ws.max_row + 1
        date_str = datetime.now().strftime("%Y-%m-%d %H:%M")
        followup_date = (datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d")  # Follow-up after 7 days
        
        ws.cell(row_num, 1, company)
        ws.cell(row_num, 2, person)
        ws.cell(row_num, 3, email)
        ws.cell(row_num, 4, role)
        ws.cell(row_num, 5, subject)
        ws.cell(row_num, 6, body)
        ws.cell(row_num, 7, date_str)
        ws.cell(row_num, 8, "Sent")
        ws.cell(row_num, 9, notes)
        ws.cell(row_num, 10, followup_date)
        
        widths = {
            'A': 20, 'B': 18, 'C': 25, 'D': 18, 'E': 30, 'F': 55, 'G': 18, 'H': 12, 'I': 28, 'J': 18
        }
        for column, width in widths.items():
            ws.column_dimensions[column].width = width
        
        wb.save(excel_file)
        return f"✅ Added to tracking: {company} | {person} | {email} (Follow-up: {followup_date})"
    
    except Exception as e:
        return f"❌ Tracking error: {str(e)}"


def send_daily_report() -> str:
    """
    Send yourself a daily report with:
    - All companies contacted today
    - Summary statistics
    - Excel attachment with full tracking
    
    Email sent to: GMAIL_ADDRESS
    """
    try:
        gmail = get_env("GMAIL_ADDRESS")
        password = get_env("GMAIL_APP_PASSWORD")
        
        if not gmail or not password:
            return "❌ GMAIL_ADDRESS or GMAIL_APP_PASSWORD not set"
        
        excel_file = "job_tracking.xlsx"
        
        if not os.path.exists(excel_file):
            return "📊 No outreach yet today. Start with 'search_web' to find companies."
        
        # Read tracking sheet
        wb = load_workbook(excel_file)
        ws = wb.active
        
        # Get today's entries
        today = datetime.now().strftime("%Y-%m-%d")
        today_entries = []
        
        for row in ws.iter_rows(min_row=2, values_only=True):
            if row[0]:  # If company exists
                date_str = str(row[6]) if len(row) > 6 and row[6] else ""
                if today in date_str:
                    today_entries.append(row)
        
        # Build email body
        body = f"""
JOB HUNT DAILY REPORT
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Date: {today}

CONTACTS TODAY: {len(today_entries)}

"""
        
        for row in today_entries:
            company = row[0] if len(row) > 0 else ""
            person = row[1] if len(row) > 1 else ""
            email = row[2] if len(row) > 2 else ""
            role = row[3] if len(row) > 3 else ""
            subject = row[4] if len(row) > 4 else ""
            body += f"  • {company} - {person} ({email}) | Role: {role} | Subject: {subject}\n"
        
        # Add overall stats
        total_contacts = ws.max_row - 1
        body += f"""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
OVERALL STATS:
• Total Companies Contacted: {total_contacts}
• This Week: (see attachment)
• Response Rate: (check email replies)

NEXT STEPS:
1. Review any replies that came in
2. Follow up with promising contacts
3. Continue outreach tomorrow

Full tracking sheet attached! 📊

Good luck! 🚀
"""
        
        # Create email with attachment
        msg = MIMEMultipart()
        msg["From"] = gmail
        msg["To"] = gmail
        msg["Subject"] = f"Daily Job Hunt Report - {today}"
        msg.attach(MIMEText(body, "plain"))
        
        # Attach Excel file
        with open(excel_file, "rb") as attachment:
            part = MIMEApplication(attachment.read())
            part.add_header("Content-Disposition", "attachment", filename=excel_file)
            msg.attach(part)
        
        # Send
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(gmail, password)
            server.sendmail(gmail, gmail, msg.as_string())
        
        return f"✅ Daily report sent! ({len(today_entries)} contacts today)"
    
    except Exception as e:
        return f"❌ Report error: {str(e)}"