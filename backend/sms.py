# backend/sms.py
import os
from datetime import datetime, timedelta
from twilio.rest import Client
from apscheduler.schedulers.background import BackgroundScheduler

TWILIO_SID = os.getenv("TWILIO_SID")
TWILIO_AUTH = os.getenv("TWILIO_AUTH")
TWILIO_PHONE = os.getenv("TWILIO_PHONE")

client = Client(TWILIO_SID, TWILIO_AUTH) if TWILIO_SID and TWILIO_AUTH else None
scheduler = BackgroundScheduler()
scheduler.start()

def send_sms_now(phone: str, message: str):
    if client is None: return None
    return client.messages.create(body=message, from_=TWILIO_PHONE, to=phone)

def schedule_sms_for_event(phone: str, title: str, event_iso: str, job_id: str=None):
    event_dt = datetime.fromisoformat(event_iso)
    reminder_dt = event_dt - timedelta(hours=2)
    now = datetime.now(event_dt.tzinfo) if event_dt.tzinfo else datetime.now()
    if reminder_dt <= now:
        body = f"Reminder: {title} at {event_dt.isoformat()}"
        return send_sms_now(phone, body) or {"status":"sent_immediately"}
    if not job_id:
        job_id = f"sms_{phone}_{int(event_dt.timestamp())}"
    def task():
        try:
            client.messages.create(body=f"Reminder: {title} at {event_dt.isoformat()}", from_=TWILIO_PHONE, to=phone)
        except Exception as e:
            print("[sms] send error:", e)
    scheduler.add_job(task, "date", run_date=reminder_dt, id=job_id, replace_existing=True)
    return {"status":"scheduled","when":reminder_dt.isoformat()}
