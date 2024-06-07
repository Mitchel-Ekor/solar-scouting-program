import requests
import pandas as pd
import smtplib
from email.mime.text import MIMEText
from datetime import datetime

# Constants (replace with your actual data)
API_KEY = 'your_api_key'
LATITUDE = 'your_latitude'
LONGITUDE = 'your_longitude'
EMAIL_FROM = 'your_email@example.com'
EMAIL_TO = 'recipient_email@example.com'
EMAIL_SUBJECT = 'Solar Scouting Alert'
SMTP_SERVER = 'smtp.example.com'
SMTP_PORT = 587
EMAIL_PASSWORD = 'your_email_password'

# Function to get solar data from a weather API
def get_solar_data(api_key, latitude, longitude):
    url = f"http://api.weatherapi.com/v1/forecast.json?key={api_key}&q={latitude},{longitude}&days=1"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        print("Failed to get data from the API")
        return None

# Function to process data and check solar potential
def process_solar_data(data):
    forecast = data['forecast']['forecastday'][0]
    solar_info = {
        'date': forecast['date'],
        'max_temp': forecast['day']['maxtemp_c'],
        'total_sun_hours': forecast['day'].get('total_sunshine_hours', 0), # Adjust based on your API response
        'solar_potential': forecast['day'].get('total_sunshine_hours', 0) > 6 # Simple threshold
    }
    return solar_info

# Function to log data
def log_data(data):
    df = pd.DataFrame([data])
    # Check if the file exists to write headers or not
    write_headers = not pd.read_csv('solar_log.csv').shape[0] > 0
    df.to_csv('solar_log.csv', mode='a', index=False, header=write_headers)

# Function to send an email alert
def send_email_alert(data):
    msg = MIMEText(f"Solar scouting alert for {data['date']}:\n\n"
                   f"Max Temperature: {data['max_temp']}C\n"
                   f"Total Sun Hours: {data['total_sun_hours']}\n"
                   f"Solar Potential: {'High' if data['solar_potential'] else 'Low'}")
    msg['Subject'] = EMAIL_SUBJECT
    msg['From'] = EMAIL_FROM
    msg['To'] = EMAIL_TO

    with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
        server.starttls()
        server.login(EMAIL_FROM, EMAIL_PASSWORD)
        server.sendmail(EMAIL_FROM, EMAIL_TO, msg.as_string())

# Main function to run the solar scouting system
def main():
    data = get_solar_data(API_KEY, LATITUDE, LONGITUDE)
    if data:
        solar_info = process_solar_data(data)
        log_data(solar_info)
        
        if solar_info['solar_potential']:
            send_email_alert(solar_info)

if __name__ == "__main__":
    main()