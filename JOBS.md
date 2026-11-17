# Backend Jobs (Celery + Redis)

## Scheduled jobs

### a. Daily Examination Reminder — `app.push_exam_reminders`
Runs every day at **9:00 AM** (`Asia/Kolkata`).

Sends reminders to students with bookings for **today** via:
- **Email** (Flask-Mail / SMTP)
- **Google Chat** (optional webhook)

Each reminder includes:
- Examination name
- Date and time
- Assigned examiner
- Examination instructions

### b. Monthly Examination Report — `app.push_monthly_report`
Runs on the **1st of every month** at **9:00 AM**.

Builds an **HTML** report for Admin covering the previous month:
- Number of examinations conducted
- Number of students evaluated
- Number of completed bookings
- Pending evaluations
- Most active examiners

Sent to all users with role `Admin` by email (HTML). Also posts a short summary to Google Chat if configured.

## Setup

1. Install Redis and start it:
```bash
redis-server
```

2. Install Python deps:
```bash
pip install -r requirements.txt
```

3. Configure email (and optional Chat) via environment variables:
```bash
set MAIL_USERNAME=your@gmail.com
set MAIL_PASSWORD=your_app_password
set GOOGLE_CHAT_WEBHOOK=https://chat.googleapis.com/v1/spaces/.../messages?key=...
```

4. Start Flask API:
```bash
python app.py
```

5. Start Celery worker (separate terminal). On Windows use `--pool=solo`:
```bash
celery -A app.celery worker --loglevel=info --pool=solo
```

6. Start Celery Beat scheduler (separate terminal):
```bash
celery -A app.celery beat --loglevel=info
```

## Manual test (optional)

From a Python shell with the app context, you can run:

```python
from app import push_exam_reminders, push_monthly_report
push_exam_reminders.delay()
push_monthly_report.delay()
```

To change the daily reminder time, edit `beat_schedule` in `app.py` (`crontab(hour=..., minute=...)`).
