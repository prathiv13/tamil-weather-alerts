import os
import requests
from flask import Flask, render_template, request, redirect, url_for
from datetime import datetime
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

app = Flask(__name__)

# Environment variables for security
OPENWEATHER_API_KEY = os.environ.get("OPENWEATHER_API_KEY")
EMAIL_ADDRESS = os.environ.get("EMAIL_ADDRESS")
EMAIL_PASSWORD = os.environ.get("EMAIL_PASSWORD")

CITY = "Chennai"
COUNTRY = "IN"
subscribers = set()

def get_weather():
    try:
        url = f"http://api.openweathermap.org/data/2.5/weather?q={CITY},{COUNTRY}&appid={OPENWEATHER_API_KEY}&units=metric&lang=ta"
        return requests.get(url).json()
    except:
        return {}

def get_forecast():
    try:
        url = f"http://api.openweathermap.org/data/2.5/forecast?q={CITY},{COUNTRY}&appid={OPENWEATHER_API_KEY}&units=metric&lang=ta"
        return requests.get(url).json()
    except:
        return {}

def send_email_alert(subject, body):
    if not EMAIL_ADDRESS or not EMAIL_PASSWORD:
        print("Email credentials not set")
        return
    msg = MIMEMultipart()
    msg['From'] = EMAIL_ADDRESS
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))
    for recipient in subscribers:
        msg['To'] = recipient
        try:
            server = smtplib.SMTP("smtp.gmail.com", 587)
            server.starttls()
            server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
            server.sendmail(EMAIL_ADDRESS, recipient, msg.as_string())
            server.quit()
        except Exception as e:
            print(f"Email failed for {recipient}: {e}")

@app.route('/')
def home():
    weather = get_weather()
    forecast_data = get_forecast()
    forecast_days = []
    if 'list' in forecast_data:
        for i in range(0, len(forecast_data['list']), 8):
            day = forecast_data['list'][i]
            forecast_days.append({
                'date': datetime.fromtimestamp(day['dt']).strftime('%d %b'),
                'temp_min': day['main']['temp_min'],
                'temp_max': day['main']['temp_max'],
                'desc': day['weather'][0]['description']
            })
    return render_template("index.html", weather=weather, forecast=forecast_days)

@app.route('/subscribe', methods=['POST'])
def subscribe():
    email = request.form.get('email')
    if email:
        subscribers.add(email)
    return redirect(url_for('home'))

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
