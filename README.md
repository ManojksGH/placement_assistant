
# AI Based Placement Assistant with Remainder Notification 

## Problem

Students frequently miss placement drives, pre-placement talks, tests, and deadlines because:

* Important emails get lost in a crowded inbox
* Event times are manually added to calendars (usually forgotten)
* No reminders → students miss events completely
* Last minute checking = unnecessary stress

This leads to missed opportunities and regret.

## Our Solution

A **smart assistant** that automatically:
# Scans Gmail for placement-related emails
# Extracts event details (date, venue, title)
# Instantly adds them to Google Calendar
# Sends SMS reminders before the event

No manual typing. No missed events.

# Key Features

| Feature                             | Benefit                                    |
| ----------------------------------- | ------------------------------------------ |
| Gmail auto scan                     | No need to search emails manually          |
| ML-based classification             | Only placement-related mails are processed |
| Auto Google Calendar event creation | Events added instantly                     |
| SMS reminder 2 hours before         | Never miss an event again                  |
| Full privacy (local ML model)       | No external data sharing with LLMs         |

# Workflow
1. Login via Google → grant Gmail + Calendar access
2. Backend scans inbox for new mails
3. Model checks: **Is this a placement event?**
4. Extracts date/time/venue if yes
5. Event added to Calendar immediately after scanning mail
6. SMS scheduled **2 hours before** event
   
# Email Classification : How It Works 

The system retrieves the subject and body of each new email from Gmail.
The text is cleaned and converted into numerical vectors using a TF-IDF feature extractor, 
which captures important words and phrases related to placement events. These vectors 
are passed into a Logistic Regression classifier, trained specifically on placement-related emails,
to decide whether the email is relevant (pre-placement talk, offline test, OA, deadline, etc.) or just
general mail. If classified as a placement email, the system uses regex-based parsing to automatically detect
and extract the date, time, and venue mentioned in the content. As soon as valid event details are found,
a Google Calendar event is created instantly, and a reminder SMS is scheduled 2 hours before the event. 
Each email is marked as processed so no duplicate events are created.

# Tech Stack

| Layer         | Tools                                  |
| ------------- | -------------------------------------- |
| Frontend      | React + Vite                           |
| Backend       | FastAPI (Python)                       |
| ML            | Logistic Regression (Email classifier) |
| Notifications | Twilio SMS API                         |
| Integrations  | Google Gmail + Calendar APIs           |


# Backend API Endpoints

| Method | Endpoint                | Purpose                           |
| ------ | ----------------------- | --------------------------------- |
| GET    | `/google/login`         | Login & authorize                 |
| GET    | `/gmail/scan?email=...` | Process inbox and trigger actions |
| POST   | `/user/phone`           | Register phone number             |

# Developed By
Manoj K S
Engineering Student at 
RV college of engineering

