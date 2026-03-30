"""
Email Service — Welcome email + daily digest.

HOW TO CONNECT SENDGRID OR GMAIL
=================================
Gmail (smtplib) is already wired up. Just make sure these two secrets are set:
  GMAIL_ADDRESS       — the sending Gmail account (e.g. yourapp@gmail.com)
  GMAIL_APP_PASSWORD  — the 16-character App Password (not your regular password)

SendGrid alternative:
    import sendgrid
    from sendgrid.helpers.mail import Mail
    sg = sendgrid.SendGridAPIClient(api_key=os.environ["SENDGRID_API_KEY"])
    message = Mail(from_email="noreply@yourapp.com", to_emails=to_email,
                   subject=subject, html_content=body_html)
    sg.send(message)
"""

import os
import smtplib
import ssl
from datetime import date
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import psycopg2
import psycopg2.extras

from .database import get_conn


UNSUBSCRIBE_BASE_URL = os.environ.get("APP_BASE_URL", "https://yourapp.com")


# ── Shared SMTP helper ────────────────────────────────────────────────────────

def _send_html_email(to_email: str, subject: str, body_html: str) -> None:
    """Send a single HTML email via Gmail SMTP. Raises on failure."""
    gmail_address  = os.environ.get("GMAIL_ADDRESS")
    gmail_password = os.environ.get("GMAIL_APP_PASSWORD")

    if not gmail_address or not gmail_password:
        print("WARNING: GMAIL_ADDRESS or GMAIL_APP_PASSWORD not set — email not sent.")
        return

    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"]    = gmail_address
    msg["To"]      = to_email
    msg.attach(MIMEText(body_html, "html"))

    with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=ssl.create_default_context()) as server:
        server.login(gmail_address, gmail_password)
        server.send_message(msg)


# ── Welcome email (sent on subscription) ─────────────────────────────────────

def send_welcome_email(to_email: str) -> None:
    """Send a one-time confirmation email when a user subscribes."""
    unsubscribe_link = f"{UNSUBSCRIBE_BASE_URL}/unsubscribe?email={to_email}"
    subject = "Subscription Confirmed — Market News Daily"

    body_html = f"""
    <html>
      <body style="font-family: Arial, sans-serif; color: #1e293b; max-width: 600px; margin: auto; padding: 24px;">

        <!-- Header -->
        <div style="background: linear-gradient(135deg, #0f172a, #1e3a8a); border-radius: 12px 12px 0 0; padding: 36px 32px; text-align: center;">
          <div style="font-size: 48px; margin-bottom: 12px;">✅</div>
          <h1 style="color: #ffffff; margin: 0; font-size: 22px;">Subscription Confirmed!</h1>
          <p style="color: #93c5fd; margin: 8px 0 0; font-size: 14px;">You have successfully subscribed to Market News Daily.</p>
        </div>

        <!-- Body -->
        <div style="background: #ffffff; border: 1px solid #e2e8f0; border-top: none; border-radius: 0 0 12px 12px; padding: 32px;">
          <p style="margin: 0 0 16px; font-size: 15px;">
            Starting tomorrow, you'll receive AI-powered financial analysis every morning at <strong>7 AM PST</strong> — delivered straight to this inbox.
          </p>

          <p style="margin: 0 0 12px; font-size: 14px; font-weight: 600; color: #475569;">Each daily email includes:</p>
          <ul style="margin: 0 0 24px; padding-left: 20px; font-size: 14px; color: #475569; line-height: 1.8;">
            <li>Top 5 market headlines of the day</li>
            <li>AI-generated article summaries</li>
            <li>Sentiment gauge — Bullish, Neutral, or Bearish</li>
          </ul>

          <hr style="border: none; border-top: 1px solid #e2e8f0; margin: 24px 0;" />

          <p style="margin: 0 0 12px; font-size: 13px; color: #94a3b8; text-align: center;">
            Changed your mind or received this by mistake?
          </p>
          <div style="text-align: center;">
            <a href="{unsubscribe_link}"
               style="display: inline-block; padding: 12px 28px; background-color: #dc2626; color: #ffffff;
                      font-size: 14px; font-weight: 600; text-decoration: none; border-radius: 8px;">
              Unsubscribe
            </a>
          </div>

          <p style="margin: 20px 0 0; font-size: 11px; color: #cbd5e1; text-align: center;">
            You subscribed at {UNSUBSCRIBE_BASE_URL}. This email was sent to {to_email}.
          </p>
        </div>

      </body>
    </html>
    """

    _send_html_email(to_email, subject, body_html)


# ── Daily digest (sent by the 7 AM scheduler) ────────────────────────────────

def _sentiment_badge(label: str, score: int) -> str:
    """Return an inline-styled HTML sentiment chip suitable for email clients."""
    styles = {
        "Bullish": ("↑", "#15803d", "#f0fdf4", "#bbf7d0"),
        "Bearish": ("↓", "#dc2626", "#fef2f2", "#fecaca"),
        "Neutral": ("—", "#b45309", "#fffbeb", "#fde68a"),
    }
    arrow, text_color, bg_color, border_color = styles.get(label, styles["Neutral"])
    return (
        f'<span style="display:inline-block; padding:3px 10px; border-radius:999px; '
        f'background:{bg_color}; border:1px solid {border_color}; '
        f'color:{text_color}; font-size:12px; font-weight:700;">'
        f'{arrow} {label} {score}/100</span>'
    )


def _build_digest_html(items: list[dict], subscriber_email: str) -> str:
    """Render the full digest HTML for one subscriber."""
    today = date.today().strftime("%B %d, %Y")
    unsubscribe_link = f"{UNSUBSCRIBE_BASE_URL}/unsubscribe?email={subscriber_email}"

    # Build one article block per news item
    article_blocks = ""
    for i, item in enumerate(items, start=1):
        title   = item.get("title", "No title")
        url     = item.get("url", "#")
        source  = item.get("source", "")
        summary = item.get("summary", "")
        label   = item.get("sentiment_label", "Neutral")
        score   = item.get("sentiment_score", 50)
        badge   = _sentiment_badge(label, score)
        source_chip = (
            f'<span style="display:inline-block; padding:2px 8px; border-radius:4px; '
            f'background:#eff6ff; border:1px solid #bfdbfe; '
            f'color:#1d4ed8; font-size:11px; font-weight:600;">{source}</span> '
            if source else ""
        )

        article_blocks += f"""
        <div style="border:1px solid #e2e8f0; border-radius:10px; padding:20px 22px; margin-bottom:16px; background:#ffffff;">
          <!-- title row -->
          <table width="100%" cellpadding="0" cellspacing="0" border="0">
            <tr>
              <td style="vertical-align:top; padding-right:12px;">
                <span style="display:inline-block; width:24px; height:24px; border-radius:50%; background:#2563eb;
                             color:#fff; font-size:11px; font-weight:700; text-align:center; line-height:24px;">{i}</span>
              </td>
              <td style="vertical-align:top; width:100%;">
                <a href="{url}" style="color:#0f172a; font-size:15px; font-weight:700; text-decoration:none; line-height:1.4;">{title}</a>
              </td>
              <td style="vertical-align:top; white-space:nowrap; padding-left:12px;">
                {badge}
              </td>
            </tr>
          </table>
          <!-- source + summary -->
          <div style="margin-top:10px; padding-left:36px;">
            <div style="margin-bottom:8px;">{source_chip}</div>
            <p style="margin:0; font-size:13px; color:#475569; line-height:1.6;">{summary}</p>
          </div>
        </div>
        """

    return f"""
    <!DOCTYPE html>
    <html lang="en">
    <head><meta charset="UTF-8" /><meta name="viewport" content="width=device-width, initial-scale=1.0" /></head>
    <body style="margin:0; padding:0; background:#f1f5f9; font-family:Arial,sans-serif;">
      <div style="max-width:640px; margin:32px auto; padding:0 16px;">

        <!-- Header -->
        <div style="background:linear-gradient(135deg,#0f172a,#1e3a8a); border-radius:12px 12px 0 0; padding:32px; text-align:center;">
          <div style="font-size:36px; margin-bottom:8px;">📈</div>
          <h1 style="color:#ffffff; margin:0; font-size:22px; font-weight:700;">Market News Daily</h1>
          <p style="color:#93c5fd; margin:6px 0 0; font-size:13px;">Top 5 stories for {today}</p>
        </div>

        <!-- Body -->
        <div style="background:#f8fafc; border:1px solid #e2e8f0; border-top:none; border-radius:0 0 12px 12px; padding:28px 24px;">

          <p style="margin:0 0 20px; font-size:14px; color:#475569;">
            Here are today's five biggest market stories, with AI-powered sentiment analysis.
          </p>

          {article_blocks}

          <div style="text-align:center; margin-top:24px;">
            <a href="{UNSUBSCRIBE_BASE_URL}"
               style="display:inline-block; padding:12px 28px; background:#2563eb; color:#fff;
                      font-size:14px; font-weight:600; text-decoration:none; border-radius:8px;">
              View Full Analysis →
            </a>
          </div>

          <hr style="border:none; border-top:1px solid #e2e8f0; margin:28px 0 20px;" />

          <p style="margin:0; font-size:11px; color:#94a3b8; text-align:center;">
            You're receiving this because you subscribed at {UNSUBSCRIBE_BASE_URL}.<br/>
            This email was sent to {subscriber_email}.<br/><br/>
            <a href="{unsubscribe_link}" style="color:#94a3b8;">Unsubscribe</a>
          </p>
        </div>

      </div>
    </body>
    </html>
    """


def send_daily_digest(news_items: list[dict]) -> None:
    """
    Send today's news digest to every active subscriber.
    Called by the 7 AM PST scheduler immediately after news is fetched and stored.
    """
    if not news_items:
        print("[Digest] No news items — skipping email send.")
        return

    # Load all subscribers
    try:
        conn = get_conn()
        cur  = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cur.execute("SELECT first_name, last_name, email FROM subscribers ORDER BY subscribed_at")
        subscribers = cur.fetchall()
        cur.close()
        conn.close()
    except Exception as e:
        print(f"[Digest] Could not load subscribers: {e}")
        return

    if not subscribers:
        print("[Digest] No subscribers found — nothing to send.")
        return

    print(f"[Digest] Sending daily digest to {len(subscribers)} subscriber(s)...")
    sent = 0
    failed = 0

    for sub in subscribers:
        email = sub["email"]
        try:
            html    = _build_digest_html(news_items, email)
            subject = f"📈 Market News Daily — {date.today().strftime('%B %d, %Y')}"
            _send_html_email(email, subject, html)
            sent += 1
            print(f"[Digest] ✓ Sent to {email}")
        except Exception as e:
            failed += 1
            print(f"[Digest] ✗ Failed for {email}: {e}")

    print(f"[Digest] Done — {sent} sent, {failed} failed.")
