# Trello Calendar Bridge

A lightweight integration that syncs Trello cards into a shared calendar and a structured database, without requiring Trello Premium.

The project reads booking-style Trello cards, parses structured data from the card description, and:

- 📅 Creates read-only calendar events (Google Calendar compatible)
- 🗄️ Stores normalized booking data in Supabase
- 📊 Logs each sync run and failures for reporting and monitoring
- 🔄 Runs automatically via GitHub Actions (daily or twice daily)

Designed for small teams and businesses that want calendar visibility, reporting, and automation — without changing how they work in Trello.

---

## ✨ Features

- **No Trello Premium required**
- **Read-only calendar sync**
- **Structured data parsing** from Trello card descriptions
- **Google Calendar support** (shareable to Outlook, iCal, etc.)
- **Supabase database integration**
- **Run-level logging** (success, partial, failed)
- **Failure-only error logging**
- **Local development + GitHub Actions support**
- **Privacy-aware** (no customer PII stored in logs)

---

## 🧱 Architecture Overview
```bash
Trello Board
│
│ (API)
▼
Trello Calendar Bridge
├─ Parse card description → Booking model
├─ Upsert booking into Supabase
├─ Create calendar event
└─ Log sync run + failures
│
▼
Google Calendar (read-only)
Supabase (data + logs)
```
## 📁 Project Structure
```bash
trello-calendar-bridge/
├─.github/
| ├─workflows/
|   ├─sync.yml # Defines the GitHub Actions workflow
├─ main.py # Orchestration entry point
├─ config.py # Environment variables & constants
├─ clients/
│ ├─ trello_client.py # Trello API client
│ └─ gcal_client.py # Google Calendar client
├─ models/
│ └─ booking_model.py # Booking parser & domain model
├─ mappers/
│ └─ calendar_mapper.py # Trello → Calendar mapping logic
├─ services/
│ ├─ database_service.py # Supabase upserts
│ └─ sync_logger.py # Run & failure logging
├─ secrets/ # Local-only credentials (gitignored)
├─ .env # Local environment variables (gitignored)
└─ requirements.txt
```
## 📝 Trello Card Format

The integration expects structured fields inside the **card description**, for example:

Name: John Doe
Email: somecoolemail@awesomeplace.com
mobile: +354 123 4567
Something Else: Hello World!

Fields are optional, but consistent formatting improves results.
The fields provided in the project are just an example and can easily be replaced and the parser updated accordingly. The idea is to provide the structure to build upon. 

---

## 🗄️ Database Tables (Supabase)

### `bookings`
Stores parsed booking data per Trello card (one row per card).

### `sync_runs`
One row per script execution:
- total cards
- processed / skipped / failed
- run status
- timestamps

### `sync_failures`
Only created when a card fails processing:
- card ID
- failure step
- error message

> No customer PII is stored in logging tables.

---

## ⚙️ Environment Variables

### Required (Local & CI)

| Variable | Description |
|--------|-------------|
| `TRELLO_KEY` | Trello API key |
| `TRELLO_TOKEN` | Trello API token |
| `TRELLO_BOARD_ID` | Trello board ID |
| `GOOGLE_CALENDAR_ID` | Target calendar ID |
| `SUPABASE_URL` | Supabase project URL |
| `SUPABASE_KEY` | Supabase service or insert-capable key |

### Google Service Account

- **Local**: use a file path
```env
GOOGLE_SERVICE_ACCOUNT_FILE=secrets/service_account.json
```
- **GitHub Actions**: store full JSON in
```env
GOOGLE_SERVICE_ACCOUNT_JSON
```

## ▶️ Running Locally

- Clone the repo

```bash
git clone https://github.com/gizmo1105/trello-calendar-bridge.git
cd trello-calendar-bridge
```

- Create and activate virtual environment (Windows or Git Bash)
```bash
python -m venv .venv
source .venv/Scripts/activate   
```

- Install dependencies 
```bash
pip install -r requirements.txt
```

- Create .env (see Environment Variables)

- Run the script
```bash
python main.py
```