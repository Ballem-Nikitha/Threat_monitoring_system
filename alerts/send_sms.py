import os
try:
    from twilio.rest import Client
except ImportError:
    Client = None

# ==============================================================================
# ⚠️ SETUP REQUIRED: To send real SMS messages, you need a Twilio account.
# 1. Sign up at https://www.twilio.com/ (Free Trial Available)
# 2. Get your Account SID, Auth Token, and Twilio phone number.
# 3. Enter them below:
# ==============================================================================
TWILIO_ACCOUNT_SID = "your_account_sid"
TWILIO_AUTH_TOKEN = "your_auth_token"
TWILIO_PHONE_NUMBER = "+1234567890" 


def send_sms(number, message):
    print(f"[send_sms] Attempting to send real SMS to {number}...")
    
    if TWILIO_ACCOUNT_SID == "your_account_sid":
        print("[send_sms] ❌ ERROR: You haven't configured TWILIO credentials in alerts/send_sms.py yet! Using print stub instead.")
        print(f"[send_sms stub] To: {number} | Message: {message}")
        return

    if Client is None:
         print("[send_sms] ❌ ERROR: Built-in Twilio library not found! Please run `pip install twilio`")
         print(f"[send_sms stub] To: {number} | Message: {message}")
         return

    try:
        client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
        msg = client.messages.create(
            body=message,
            from_=TWILIO_PHONE_NUMBER,
            to=number
        )
        print(f"[send_sms] ✔ Successfully sent real SMS to {number} (SID: {msg.sid})!")
    except Exception as e:
        print(f"[send_sms] ❌ Failed to send SMS: {e}")
