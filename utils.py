from twilio.rest import Client
from flask import current_app
from nltk.sentiment import SentimentIntensityAnalyzer
import nltk

nltk.download('vader_lexicon')

def analyze_leave_reason(reason):
    """Analyze sentiment using VADER."""
    sia = SentimentIntensityAnalyzer()
    score = sia.polarity_scores(reason)['compound']
    if score > 0.2:
        return "Positive"
    elif score < -0.2:
        return "Negative"
    else:
        return "Neutral"

def send_notification(to_number, message):
    """Send SMS notifications via Twilio."""
    client = Client(current_app.config['TWILIO_ACCOUNT_SID'], current_app.config['TWILIO_AUTH_TOKEN'])
    client.messages.create(
        from_=current_app.config['TWILIO_PHONE_NUMBER'],
        to=to_number,
        body=message
    )
