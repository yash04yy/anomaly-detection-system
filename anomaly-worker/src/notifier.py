import os, smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

class Notifier:
    def __init__(self):
        self.email_enabled = os.getenv("ENABLE_EMAIL", "false").lower() == "true"

        if self.email_enabled:
            self.smtp_server = os.getenv("SMTP_SERVER", "smtp.gmail.com")
            self.smtp_port = int(os.getenv("SMTP_PORT", 587))
            self.smtp_user = os.getenv("SMTP_USER")
            self.smtp_pass = os.getenv("SMTP_PASS")
            self.email_to = os.getenv("EMAIL_TO")

    def send_email(self, subject, body):
        try:
            msg = MIMEMultipart()
            msg["From"] = self.smtp_user
            msg["To"] = self.email_to
            msg["Subject"] = subject
            msg.attach(MIMEText(body, "plain"))

            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.smtp_user, self.smtp_pass)
                server.sendmail(self.smtp_user, self.email_to, msg.as_string())

            print("[Notifier] Email sent successfully ✅")

        except Exception as e:
            print("[Notifier] Email error:", e)

    def notify(self, message):
        if self.email_enabled:
            self.send_email("Anomaly Alert 🚨", message)
