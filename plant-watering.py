import csv
import os
import sys
from datetime import datetime, timedelta
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv


def load_plants(file_path):
    """Load plant data from a CSV file."""
    plants = []
    try:
        with open(file_path, mode='r') as file:
            reader = csv.DictReader(file)
            for row in reader:
                row['watering_frequency'] = int(row['watering_frequency'])
                row['last_watered'] = datetime.strptime(row['last_watered'], '%Y-%m-%d').date()
                plants.append(row)
    except FileNotFoundError:
        print(f"File {file_path} not found. Starting with an empty list.")
    return plants

def save_plants(file_path, plants):
    """Save plant data to a CSV file."""
    with open(file_path, mode='w', newline='') as file:
        fieldnames = ['plant_name', 'watering_frequency', 'last_watered']
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        for plant in plants:
            writer.writerow({
                'plant_name': plant['plant_name'],
                'watering_frequency': plant['watering_frequency'],
                'last_watered': plant['last_watered'].strftime('%Y-%m-%d')
            })

def send_notification(plants_to_water, sender_email, sender_password, receiver_emails):
    """Send an email notification for plants that need watering."""

    subject = "Plants That Need Watering Today"
    body = "The following plants need to be watered today:\n\n"
    body += "\n".join([plant['plant_name'] for plant in plants_to_water])

    message = MIMEMultipart()
    message['From'] = sender_email
    message['Subject'] = subject

    message.attach(MIMEText(body, 'plain'))
    for receiver_email in receiver_emails:
        message['To'] = receiver_email
        try:
            with smtplib.SMTP('smtp.gmail.com', 465) as server:
                server.starttls()
                server.login(sender_email, sender_password)
                server.sendmail(sender_email, receiver_email, message.as_string())
            print("Notification email sent successfully.")
        except Exception as e:
            print(f"Failed to send email: {e}")

def check_and_update_watering(plants, sender_email, sender_password, receiver_emails):
    """Check if plants need watering and update their last watered date if watered."""
    today = datetime.now().date()
    plants_to_water = []

    for plant in plants:
        days_since_last_watered = (today - plant['last_watered']).days
        if days_since_last_watered >= plant['watering_frequency']:
            print(f"{plant['plant_name']} needs watering. Watering now...")
            plant['last_watered'] = today
            plants_to_water.append(plant)
        else:
            print(f"{plant['plant_name']} does not need watering today.")

    if plants_to_water:
        send_notification(plants_to_water, sender_email, sender_password, receiver_emails)

def main():
    load_dotenv()
    sender_email = os.getenv("SENDER_EMAIL")
    sender_password = os.getenv("SENDER_EMAIL_PASSWORD")
    receiver_emails = os.getenv("RECEIVER_EMAIL")
    file_path = 'plants.csv'
    plants = load_plants(file_path)

    if not plants:
        print("No plants found. Ending script.")
        sys.exit()
    check_and_update_watering(plants, sender_email, sender_password, receiver_emails)
    save_plants(file_path, plants)

if __name__ == "__main__":
    main()
