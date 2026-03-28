# MediScript — Medical Prescription System

A production-ready Django web app for doctors to manage patients,
create prescriptions, generate PDFs, print, and receive documents via Telegram.

---

## Quick Start

### 1. Clone / enter the project

```bash
cd doc   # or wherever the project lives
```

### 2. Create and activate a virtual environment

```bash
python -m venv venv
# Windows
venv\Scripts\activate
# macOS / Linux
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

> **WeasyPrint on Windows** may need extra system libs. See:
> https://doc.courtbouillon.org/weasyprint/stable/first_steps.html#installation

### 4. Configure environment

```bash
cp .env.example .env
# Edit .env — set TELEGRAM_BOT_TOKEN and DJANGO_APP_URL at minimum
```

### 5. Run migrations

```bash
python manage.py migrate
```

### 6. Create a superuser (doctor account)

```bash
python manage.py createsuperuser
# Telegram ID: your numeric Telegram ID (e.g. 123456789)
# Full name:   Dr. Jane Smith
# Password:    yourpassword
```

> Find your Telegram ID by messaging @userinfobot on Telegram.

### 7. Add drugs via Admin

```bash
python manage.py runserver
# Open: http://localhost:8000/admin/
# Login with your superuser credentials
# Go to Drugs → Add Drug
```

### 8. Use the app

Open: http://localhost:8000/

Login with your `telegram_id` and password.

---

## Running the Telegram Bot

In a **separate terminal** (with venv active):

```bash
python bot/bot.py
```

The bot will:
- Respond to `/start` with an "Open MediScript" button
- Receive prescription PDFs when you click "Send via Telegram" in the web app

---

## Project Structure

```
config/          Django project config (settings, urls, wsgi)
apps/
  users/         Doctor model + login/logout
  patients/      Patient management
  drugs/         Drug database
  prescriptions/ Prescriptions, PDF, print, Telegram send
templates/       HTML templates (Django-rendered)
static/
  css/main.css   Medical UI styles
  js/prescription.js
bot/
  bot.py         Telegram bot (aiogram 3)
  sender.py      Async helper to send PDF via bot
```

---

## Features

| Feature | Location |
|---|---|
| Doctor login (Telegram ID + password) | `/login/` |
| Dashboard with stats | `/dashboard/` |
| Patient CRUD | `/patients/` |
| Drug search | `/drugs/` |
| Create prescription + drug formset | `/prescriptions/new/` |
| Prescription detail | `/prescriptions/<id>/` |
| Download PDF | `/prescriptions/<id>/pdf/` |
| Print (A4, clean) | `/prescriptions/<id>/print/` |
| Send PDF to Telegram | `/prescriptions/<id>/send-telegram/` |
| Django Admin | `/admin/` |

---

## PostgreSQL (production)

Uncomment the PostgreSQL block in `config/settings.py` and set:

```env
DB_NAME=medical_db
DB_USER=postgres
DB_PASSWORD=secret
DB_HOST=localhost
DB_PORT=5432
```

---

## Security checklist before production

- [ ] Set `DEBUG=False` in `.env`
- [ ] Set a strong `SECRET_KEY`
- [ ] Set correct `ALLOWED_HOSTS`
- [ ] Run `python manage.py collectstatic`
- [ ] Use HTTPS (required for Telegram WebApp)
- [ ] Set up proper WSGI server (gunicorn/uvicorn)
