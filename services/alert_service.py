import smtplib, requests
from email.message import EmailMessage

def send_email_alert(to, subject, body):
    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = "noreply@stockalert.com"
    msg["To"] = to
    msg.set_content(body)
    with smtplib.SMTP("localhost") as smtp:
        smtp.send_message(msg)

def send_slack_alert(webhook_url, message):
    requests.post(webhook_url, json={"text": message})
