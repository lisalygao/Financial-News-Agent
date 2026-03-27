"""
Email Service — Welcome email sent on subscription.

HOW TO CONNECT SENDGRID OR GMAIL
=================================
Replace the body of send_welcome_email() with your provider's SDK call.

SendGrid example:
    import sendgrid
    from sendgrid.helpers.mail import Mail
    sg = sendgrid.SendGridAPIClient(api_key=os.environ["SENDGRID_API_KEY"])
    message = Mail(
        from_email="noreply@yourapp.com",
        to_emails=to_email,
        subject=subject,
        html_content=body_html,
    )
    sg.send(message)

Gmail (smtplib) example:
    import smtplib, ssl
    from email.mime.text import MIMEText
    msg = MIMEText(body_html, "html")
    msg["Subject"] = subject
    msg["From"] = os.environ["GMAIL_ADDRESS"]
    msg["To"] = to_email
    with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=ssl.create_default_context()) as s:
        s.login(os.environ["GMAIL_ADDRESS"], os.environ["GMAIL_APP_PASSWORD"])
        s.send_message(msg)
"""

import os


UNSUBSCRIBE_BASE_URL = os.environ.get("APP_BASE_URL", "https://yourapp.com")


def send_welcome_email(to_email: str) -> None:
    """
    Send a welcome email to a new subscriber.
    Currently a placeholder — wire up SendGrid or Gmail using the instructions above.
    """
    subject = "Welcome to Market News Daily!"
    unsubscribe_link = f"{UNSUBSCRIBE_BASE_URL}/unsubscribe?email={to_email}"

    body_html = f"""
    <html>
      <body style="font-family: Arial, sans-serif; color: #1e293b; max-width: 600px; margin: auto;">
        <h2 style="color: #1d4ed8;">Welcome to Market News Daily</h2>
        <p>Thank you for subscribing! You'll receive AI-powered financial analysis every morning at 7 AM PST.</p>
        <p>Here's what to expect:</p>
        <ul>
          <li>Top 5 market headlines, summarised by AI</li>
          <li>Step-by-step analytical breakdown</li>
          <li>Sentiment gauge: Bullish, Neutral, or Bearish</li>
        </ul>
        <hr style="border: none; border-top: 1px solid #e2e8f0; margin: 24px 0;" />
        <p style="font-size: 12px; color: #94a3b8;">
          You received this because you subscribed at {UNSUBSCRIBE_BASE_URL}.<br/>
          Don't want these emails?
          <a href="{unsubscribe_link}" style="color: #64748b;">Unsubscribe here</a>.
        </p>
      </body>
    </html>
    """

    # ── Placeholder: log instead of sending ───────────────────────────────────
    print(f"[EMAIL PLACEHOLDER] Would send welcome email to: {to_email}")
    print(f"  Subject : {subject}")
    print(f"  Unsub   : {unsubscribe_link}")
    # ── Replace the three lines above with your provider SDK call ─────────────
