# Exam Portal Application (Aman)

Flask + Vue exam management portal with Celery/Redis backend jobs.

## Stack
- Backend: Flask, SQLAlchemy, JWT
- Frontend: Vue 3 + Vite
- Jobs / Broker: Celery + Redis
- Mail: Flask-Mail (SMTP)

## Quick start

```bash
pip install -r requirements.txt
python app.py
```

Frontend:

```bash
cd frontend
npm install
npm run dev
```

## Celery / Redis jobs

See [JOBS.md](JOBS.md) for:
- Daily examination reminders (email / Google Chat)
- Monthly HTML examination report to Admin

```bash
redis-server
celery -A app.celery worker --loglevel=info
celery -A app.celery beat --loglevel=info
```
