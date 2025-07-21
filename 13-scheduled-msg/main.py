
# project Setup:
# 1.twilio client setup
# 2. user inputs
# 3. scheduling logic
# 4. send message

#  video link: https://www.youtube.com/watch?v=z5RwpJn86-U
import time
from datetime import datetime, timedelta
from twilio.rest import Client
import os
from dotenv import load_dotenv

load_dotenv()
# Twilio credentials/ Repalace with ultramsg credentials
account_sid = os.getenv('TWILIO_ACCOUNT_SID')
auth_token = os.getenv('TWILIO_AUTH_TOKEN')

client = Client(account_sid, auth_token)
def send_whatsapp_message(recipient, message):
    """
    Send a WhatsApp message using Twilio.
    :param recipient: The recipient's WhatsApp number in the format 'whatsapp:+1234567890'.
    :param message: The message to be sent.
    """
    try:
        message = client.messages.create(
            body=message,
            from_='whatsapp:+14155238886',  # Twilio sandbox number
            to=recipient
        )
        print(f"Message sent successfully: {message.sid}")
    except Exception as e:
        print(f"Failed to send message: {e}")

name = input("Enter your name: ")
recipient = input("Enter the recipient's WhatsApp number (in the format 'whatsapp:+1234567890'): ")
message = input("Enter your message: ")

# Schedule the message to be sent at a specific time
date_str = input("Enter the date to send the message (YYYY-MM-DD): ")
time_str = input("Enter the time to send the message (HH:MM): ")

schedule_time = datetime.strptime(f"{date_str} {time_str}", "%Y-%m-%d %H:%M")
current_time = datetime.now()

# Calculate the time difference between the current time and the scheduled time
time_difference = schedule_time - current_time
delay_seconds = time_difference.total_seconds()

# Send the message after the specified delay
if delay_seconds < 0:
    print("Invalid schedule time. It should be in the future.")
else:
    print(f"Scheduling message to be sent at {schedule_time}...")
    time.sleep(delay_seconds)
    send_whatsapp_message(recipient, f"Hello {name}, {message}")