import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# ==============================================================================
# ⚠️ SETUP REQUIRED: Enter the email you want to SEND alerts FROM
# If using Gmail, you MUST use an "App Password", not your normal password!
# Guide: https://support.google.com/accounts/answer/185833
# ==============================================================================
SENDER_EMAIL = "your_sender_email@gmail.com"  
SENDER_PASSWORD = "your_app_password_here"  


def send_email(to, subject, body):
    print(f"[send_email] Attempting to send real email to {to}...")
    
    if SENDER_EMAIL == "your_sender_email@gmail.com":
        print("[send_email] ❌ ERROR: You haven't configured SENDER_EMAIL and SENDER_PASSWORD in alerts/send_email.py yet! Using print stub instead.")
        print(f"[send_email stub] To: {to} | Subject: {subject} | Body: {body}")
        return

    msg = MIMEMultipart()
    msg['From'] = SENDER_EMAIL
    msg['To'] = to
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))

    try:
        # Connect to Gmail's SMTP server
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()  # Secure the connection
        server.login(SENDER_EMAIL, SENDER_PASSWORD)
        server.send_message(msg)
        server.quit()
        print(f"[send_email] ✔ Successfully sent real email to {to}!")
    except Exception as e:
        print(f"[send_email] ❌ Failed to send email: {e}")
