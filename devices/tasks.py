import smtplib
from email.mime.text import MIMEText

import pytz
from celery.decorators import task

from devices.models import Device
from noise_dashboard.settings import TIME_ZONE


@task(name="send_email_alert")
def send_email_alert():
    # Get all devices
    devices = Device.objects.all()
    timezone = pytz.timezone(TIME_ZONE)

    for device in devices:
        # Get last seen time
        last_seen_time = device.lastseen

        # Check for conditions and send emails
        if last_seen_time is not None:
            current_time = timezone.now()
            uptime_hours = (current_time - last_seen_time).total_seconds() / 3600

            if uptime_hours >= 120:
                send_critical_email(device)
            elif uptime_hours >= 72:
                send_flagged_email(device)
            elif uptime_hours >= 24:
                send_device_off_email(device)


def send_critical_email(device):
    subject = "Critical Uptime Alert"
    message = f"The device {device.device_name} has been offline for more than 5 days."
    send_email(subject, message)


def send_flagged_email(device):
    subject = "Flagged Uptime Alert"
    message = f"The device {device.device_name} has been offline for more than 3 days."
    send_email(subject, message)


def send_device_off_email(device):
    subject = "Device Offline Alert"
    message = f"The device {device.device_name} has been offline for 24 hours."
    send_email(subject, message)


def send_email(subject, message):
    # Modify the email sending logic based on your project's email settings
    # send_mail(subject, message, 'vigidaiz15@gmail.com', ['gilbertyiga15@gmail.com'],  fail_silently=False,)
    from_email = "vigidaiz15@gmail.com"
    to_email = "gilbertyiga15@gmail.com"
    password = "mfww omdz cowe ipgt"

    try:
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(from_email, password)

        message = MIMEText(message)
        message["From"] = from_email
        message["To"] = to_email
        message["Subject"] = subject

        server.sendmail(from_email, to_email, message.as_string())
        server.quit()

        print("Email sent!")
    except Exception as e:
        print(f"Error sending email: {e}")
