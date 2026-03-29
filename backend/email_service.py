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
    subject = "Subscription Confirmed — Market News Daily"
    unsubscribe_link = f"{UNSUBSCRIBE_BASE_URL}/api/unsubscribe?email={to_email}"

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
            <li>AI-generated article highlights</li>
            <li>Sentiment gauge — Bullish, Neutral, or Bearish</li>
          </ul>

          <hr style="border: none; border-top: 1px solid #e2e8f0; margin: 24px 0;" />

          <!-- Unsubscribe button -->
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

    import smtplib, ssl
    from email.mime.text import MIMEText
    from email.mime.multipart import MIMEMultipart

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
