# Performance Tracker

Personal performance tracking app for CS2, gym, body weight, and mental health.

## Features

- **CS2 Stats** — Per-match K/D, HS%, ADR, Leetify Rating pulled from Leetify API with trend charts
- **Gym Tracker** — Log weight exercises (sets/reps/weight/rest) and cardio (distance/time/calories) with exercise library & autocomplete
- **Weight Tracker** — Daily body weight logging with trend chart
- **Mental Health** — Track mood, stress, sleep quality, energy, and anxiety (1-10 scales)
- **PIN Protection** — Simple session-based PIN auth, no user management
- **Mobile Friendly** — Bottom nav, touch-friendly inputs, responsive layout
- **Time Filters** — Today / 7d / 30d / 90d / All Time on every data page

## Tech Stack

- **Backend:** Flask + SQLite (SQLAlchemy)
- **Frontend:** Jinja2 templates + vanilla CSS + vanilla JS + Chart.js v4 (CDN)
- **Game API:** Leetify Public CS API

## Setup

### 1. Environment

```bash
cp .env.example .env
# Edit .env with your Leetify API key, Steam64 ID, and desired PIN
```

### 2. Backend

```bash
cd backend
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac
pip install -r requirements.txt
```

### 3. Run

```bash
python run.py
```

App runs on **http://localhost:1337**

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `SECRET_KEY` | Yes | Flask session encryption key |
| `APP_PIN` | Yes | PIN to unlock the app (default: `1337`) |
| `STEAM_ID` | For CS2 | Your Steam64 ID (find at https://steamid.io) |
| `LEETIFY_API_KEY` | For CS2 | Your Leetify API key |

## Port

Runs on port **1337** by default. Change in `run.py`.
