# College ERP to Google Calendar Automation

This is a Python-based automation script that logs into a college ERP system, fetches today's class schedule, and automatically adds the events to your Google Calendar. It sends reminders 30 minutes before each class and provides attendance updates (present/absent) at 6:30 PM daily.

---

## 🚀 Features

- 📅 Fetches today's classes from your college ERP
- 🔔 Adds class events to Google Calendar with 30-minute reminders
- 📲 Sends attendance updates via SMS (using Twilio)
- ☁️ Hosted on Apify cloud for daily automation
- ⏰ Notifies you about attendance and other academic data in the evening

---

## 🧰 Tech Stack

- Python
- Google Calendar API
- `requests` module
- Twilio API (for SMS)
- Apify Cloud (for deployment and scheduling)
- College ERP (via scripted login)

---

## 🔒 Note on Security

This project **does not** include sensitive credentials like:

- `credentials.json` (Google OAuth2 credentials)
- `token.json` (OAuth access token)

These are listed in `.gitignore` and must be added manually before running.

---

## 🔧 Setup Instructions

1. **Clone the Repository**

```bash
git clone https://github.com/your-username/your-repo.git
cd your-repo
