# backend/data_store.py
import datetime as dt
from googleapiclient.discovery import build
from .auth_google import get_creds
from .classifier import predict
from .utils import create_calendar_event
from .sms import schedule_sms_for_event


phones: dict[str,str] = {}
auto_process: dict[str,bool] = {}
processed_ids: set[str] = set()

def save_phone(email: str, phone: str):
    phones[email] = phone

def set_auto_process(email: str, flag: bool):
    auto_process[email] = bool(flag)

def get_user_phone(email: str):
    return phones.get(email)

def get_auto_process_emails():
    return [e for e,f in auto_process.items() if f]

def scan_inbox(email: str, max_results: int=10):
    creds = get_creds(email)
    if not creds:
        return []
    service = build("gmail", "v1", credentials=creds)
    results = service.users().messages().list(userId="me", maxResults=max_results, q="newer_than:2d").execute()
    messages = results.get("messages", [])
    out=[]
    for m in messages:
        mid = m["id"]
        if mid in processed_ids: continue
        processed_ids.add(mid)
        msg = service.users().messages().get(userId="me", id=mid, format="full").execute()
        subject = ""
        headers = msg.get("payload",{}).get("headers",[])
        for h in headers:
            if h.get("name","").lower()=="subject":
                subject = h.get("value","")
                break
        body = msg.get("snippet","") or ""
        text = f"{subject}\n{body}"
        cls = predict(text)
        label = cls.get("label","general")
        confidence = cls.get("confidence",0.0)
        item = {"id":mid,"subject":subject,"label":label,"confidence":confidence}
        # simple rule: if label != general and has date/time in subject/body, try create event
        # user can embed datetime in standardized ISO format in email for reliability; otherwise manual confirmation needed.
        # here we try to parse ISO datetime from model output 'datetime' if provided (classifier can be extended)
        dt_str = cls.get("datetime") or None
        if label!="general" and dt_str:
            try:
                start = dt.datetime.fromisoformat(dt_str)
                end = start + dt.timedelta(hours=1)
                event = create_calendar_event(email, subject or label, start.isoformat(), end.isoformat(), cls.get("venue"))
                item["event"] = event
                phone = get_user_phone(email)
                if phone:
                    schedule_sms_for_event(phone, subject or label, start.isoformat())
            except Exception as e:
                item["event_error"] = str(e)
        out.append(item)
    return out
