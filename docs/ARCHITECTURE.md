# Architecture & Maintenance Guide

## Project Structure

```
performance-tracker/
├── .env                          # Your secrets (PIN, Leetify key)
├── .env.example                  # Template for .env
├── run.py                        # Entry point — starts Flask on port 1337
├── README.md                     # Quick-start guide
│
├── backend/
│   ├── app.py                    # Flask app factory, registers all blueprints
│   ├── config.py                 # Loads .env, exposes config values
│   ├── database.py               # SQLAlchemy instance (shared across app)
│   ├── models.py                 # All database table definitions
│   ├── requirements.txt          # Python dependencies
│   ├── data/                     # Auto-created, holds SQLite DB file
│   │
│   ├── templates/                # Jinja2 HTML templates
│   │   ├── base.html             # Base layout (sidebar, bottom nav, shared CSS/JS)
│   │   ├── login.html            # PIN entry screen
│   │   ├── dashboard.html        # Overview cards for all modules
│   │   ├── cs2.html              # CS2 match data, charts, profile
│   │   ├── gym.html              # Gym weight + cardio + exercise library
│   │   ├── weight.html           # Body weight tracking + chart
│   │   └── mental.html           # Mental health metrics + charts
│   │
│   ├── static/
│   │   ├── css/style.css         # Dark theme, responsive layout, all components
│   │   └── js/app.js             # API client, helpers, icons, period filters
│   │
│   └── api/
│       ├── auth.py               # PIN verification, session management
│       ├── cs2.py                # CS2 stats endpoints (Leetify sync, matches, profile)
│       ├── gym.py                # Gym weight + cardio + exercise library endpoints
│       ├── weight.py             # Body weight logging endpoints
│       ├── mental.py             # Mental health tracking endpoints
│       │
│       └── games/
│           └── leetify.py        # Leetify Public CS API client
│
└── docs/
    ├── ARCHITECTURE.md           # This file
    └── DEPLOYMENT.md             # Hosting & deployment guide
```

---

## Component Reference

### Backend Components

#### `run.py`
Entry point. Adds `backend/` to the Python path and starts Flask on `0.0.0.0:1337` using werkzeug's `run_simple` with `SO_REUSEADDR`.

#### `backend/app.py` — App Factory
- Creates the Flask app with `create_app()`
- Sets `template_folder` to `backend/templates/` and `static_folder` to `backend/static/`
- Registers all API blueprints (auth, cs2, gym, weight, mental)
- Applies auth middleware: all `/api/` and page routes (except `/login` and `/static/`) require an authenticated session
- Serves Jinja2 templates for each page route (`/`, `/cs2`, `/gym`, `/weight`, `/mental`)
- Injects SVG icons into all templates via context processor
- Creates all database tables on startup

#### `backend/config.py`
Loads values from `.env`:
| Variable | Purpose |
|----------|---------|
| `SECRET_KEY` | Flask session encryption key |
| `APP_PIN` | The PIN users enter to unlock the app |
| `STEAM_ID` | Your Steam64 ID (used by Leetify to identify player) |
| `LEETIFY_API_KEY` | API key for Leetify Public CS API |

#### `backend/database.py`
Single shared `SQLAlchemy()` instance imported by models and routes.

#### `backend/models.py`
All database tables:

| Model | Table | Purpose |
|-------|-------|---------|
| `CS2Match` | `cs2_matches` | Per-match data synced from Leetify (K/D/A, ADR, HS%, Leetify rating, accuracy, multi-kills) |
| `CS2Comment` | `cs2_comments` | Free-text session notes for CS2 |
| `Exercise` | `exercises` | Saved exercise library for autocomplete (name, category, type) |
| `GymWeightSet` | `gym_weight_sets` | Individual sets: exercise, reps, weight, rest, set# |
| `GymCardioEntry` | `gym_cardio_entries` | Cardio sessions: exercise, distance, time, calories |
| `BodyWeight` | `body_weight` | Daily body weight (unique per date) |
| `MentalHealth` | `mental_health` | Daily mental metrics: mood, stress, sleep, energy, anxiety |

Each model has a `to_dict()` method for JSON serialization.

#### `backend/api/auth.py`
- `POST /api/auth/verify` — Check PIN, set session cookie
- `GET /api/auth/check` — Check if session is authenticated
- `POST /api/auth/logout` — Clear session

#### `backend/api/cs2.py`
- `POST /api/cs2/sync` — Pull match history from Leetify API, upsert matches by `game_id`
- `GET /api/cs2/matches` — All stored matches (newest first)
- `DELETE /api/cs2/matches/<id>` — Delete a match
- `GET /api/cs2/profile` — Live Leetify profile (ratings, ranks, skill breakdown)
- `GET /api/cs2/comments` — All session notes
- `POST /api/cs2/comments` — Add a note
- `DELETE /api/cs2/comments/<id>` — Delete a note

#### `backend/api/gym.py`
- `GET /api/gym/exercises?type=weight|cardio` — Get saved exercise library (filtered by type)
- `POST /api/gym/exercises` — Add exercise to library (name, category, type; duplicate-safe)
- `DELETE /api/gym/exercises/<id>` — Remove from library
- `GET /api/gym/weight?date=YYYY-MM-DD` — Weight sets (optionally filter by date)
- `POST /api/gym/weight` — Add a single set
- `POST /api/gym/weight/batch` — Add multiple sets at once
- `PUT /api/gym/weight/<id>` — Update a set
- `DELETE /api/gym/weight/<id>` — Delete a set
- `GET /api/gym/weight/exercises` — Unique exercise names from logged data (legacy autocomplete)
- Same pattern for `/api/gym/cardio`

#### `backend/api/weight.py`
- `GET /api/weight` — All entries (newest first)
- `POST /api/weight` — Add/update weight for a date (auto-upserts if date exists)
- `DELETE /api/weight/<id>` — Delete entry

#### `backend/api/mental.py`
- `GET /api/mental` — All entries (newest first)
- `POST /api/mental` — Add entry
- `PUT /api/mental/<id>` — Update entry
- `DELETE /api/mental/<id>` — Delete entry

#### `backend/api/games/leetify.py`
Leetify Public CS API client (`LeetifyAPI` class):
- `get_profile()` — Fetch player profile (ratings, ranks, skill ratings)
- `get_match_history()` — Fetch recent matches (up to 100)
- `get_match_detail(game_id)` — Fetch detailed stats for a specific match
- `parse_profile(data)` — Extract flat dict with Leetify rating, Faceit ELO/level, competitive ranks, skill ratings
- `parse_match(match_data)` — Extract our player's stats from a match object

API base URL: `https://api-public.cs-prod.leetify.com`
Auth: `Authorization: Bearer <key>` header

### Frontend Components

The frontend uses **Jinja2 server-side templates** with vanilla CSS and JS. No build step required.

#### `base.html`
Base layout inherited by all pages:
- Fixed left sidebar (desktop) with nav links + lock button
- Fixed bottom nav bar (mobile) with icons
- Includes Chart.js v4 defaults and shared JS (`app.js`) and CSS (`style.css`)

#### `login.html`
Full-screen PIN entry. Numeric input, auto-focuses. On success, redirects to dashboard.

#### `dashboard.html`
Overview grid with 4 cards (CS2/Gym/Weight/Mental). Each shows latest key metrics.

#### `cs2.html`
- Rank cards (Leetify Rating, Faceit Level/ELO, Premier, Win Rate)
- Leetify Skill Ratings radar chart (Aim, Positioning, Utility, Clutch, Opening)
- Stat cards (avg K/D, ADR, HS%, Win Rate from filtered matches)
- Tabs: Matches (table), Charts (rating/KD/ADR/HS% over time), Notes
- Period filter: Today / 7d / 30d / 90d / All Time

#### `gym.html`
- Exercise picker with autocomplete dropdown + exercise library modal
- Tabs: Weight (add sets), Cardio (add entries), History (tables), Progress (charts per exercise)
- Period filter on History and Progress tabs

#### `weight.html`
- Log tab: date + weight input + comment
- Chart tab: line chart of weight over time
- Table tab: all entries with delete

#### `mental.html`
- Log tab: tap 1-10 for each metric + notes textarea
- Charts tab: radar chart + line charts of all metrics over time
- Table tab: all entries with delete

#### `style.css`
Dark theme (zinc palette), responsive grid, cards, tabs, forms, buttons, modals, exercise picker, tables, scrollbars.

#### `app.js`
- `API` object with all fetch methods (auth, cs2, gym, weight, mental, exercises)
- Helpers: `todayISO()`, `formatDate()`, `$()`, `el()`, `initTabs()`
- `ICONS` object with inline SVGs
- `buildPeriodFilter()` / `filterByPeriod()` for time range filtering
- Chart.js dark theme defaults

---

## Database Management

The SQLite database lives at `backend/data/performance_tracker.db`. It is created automatically on first run.

### Backup
```bash
cp backend/data/performance_tracker.db backend/data/backup_$(date +%Y%m%d).db
```

### Reset Everything
```bash
rm backend/data/performance_tracker.db
python run.py  # Recreates empty tables
```

### Schema Changes
Since we use SQLite with SQLAlchemy and no migration tool, for schema changes you have two options:
1. **Delete the DB** — loses all data, tables are recreated on startup
2. **ALTER TABLE manually** — preserves data, run SQL directly:
   ```bash
   sqlite3 backend/data/performance_tracker.db
   ALTER TABLE table_name ADD COLUMN new_col TYPE;
   ```

If the app grows, consider adding Flask-Migrate (Alembic) for proper migrations.
