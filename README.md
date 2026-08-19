# Weather Bot

[![Python](https://img.shields.io/badge/Python-3.13-blue?logo=python&logoColor=white)](https://www.python.org/)
[![Aiogram](https://img.shields.io/badge/Aiogram-3.x-orange?logo=telegram&logoColor=white)](https://docs.aiogram.dev/)
[![FastAPI](https://img.shields.io/badge/FastAPI-Standard-009688?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![Docker](https://img.shields.io/badge/Docker-Compose-2496ED?logo=docker&logoColor=white)](https://www.docker.com/)
[![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-2.0-D71F00?logo=sqlalchemy&logoColor=white)](https://www.sqlalchemy.org/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-4169E1?logo=postgresql&logoColor=white)](https://www.postgresql.org/)
[![Poetry](https://img.shields.io/badge/Poetry-2.0+-blueviolet?logo=poetry&logoColor=white)](https://python-poetry.org/)

**SkySentry** is a high-performance, asynchronous weather forecasting service and Telegram bot. The project is built on a decoupled architecture separating the FastAPI backend, scheduled background dispatchers, and an interactive Telegram client.


## ✨ Bot Features

- ⚡ **Real-Time Weather Reports:** Instant current conditions with comprehensive metrics (apparent temperature, humidity, wind speed, precipitation, cloud cover).
- 🖼️ **On-the-Fly Image Generation:** Dynamic rendering of stylish weather cards using Pillow.
- 🔄 **Interactive Forecast Carousel:** Multi-day forecast navigation (3, 7, 14 days) using inline buttons and seamless `edit_media` updates without chat spam.
- ⏰ **Timezone-Aware Scheduling:** Automated daily weather broadcasts powered by APScheduler, adjusting dispatch times to the user's exact city timezone via `timezonefinder`.
- 📍 **Smart Geocoding:** Flexible location setup supporting both textual city queries and native Telegram GeoPoints with reverse geocoding.
- 🗄️ **Robust Persistence & Migrations:** Asynchronous database access via SQLAlchemy 2.0 + asyncpg with schema versioning via Alembic.

## 🛠️ Technology Stack

| Component | Technologies |
| :--- | :--- |
| **Backend & API** | Python 3.12+, FastAPI, Uvicorn, Pydantic v2, HTTPX |
| **Telegram Bot** | Aiogram 3.x (Asyncio, FSM, Inline & Reply Markups) |
| **Database & ORM** | PostgreSQL 16, SQLAlchemy 2.0 (Async), asyncpg |
| **Migrations** | Alembic |
| **Scheduling** | APScheduler, TimezoneFinder, pytz |
| **Graphics** | Pillow (PIL) |
| **DevOps & Packaging** | Docker, Docker Compose, Poetry |

## Project Architecture: 
```text
skysentry/
├── backend/               # FastAPI application & core backend logic
│   ├── database/          # SQLAlchemy models, async engines & CRUD queries
│   ├── routes/            # REST API endpoints (weather, locations, schedules, geocoding)
│   ├── scheduler/         # APScheduler background jobs & automated broadcast tasks
│   ├── services/          # Weather API (Open-Meteo) & Geocoding integrations
│   ├── config.py          # Backend settings & environment configuration
│   └── main.py            # FastAPI entry point & application lifespan
├── bot/                   # Aiogram 3.x Telegram client
│   ├── api/               # Async HTTP client communicating with backend API
│   ├── assets/            # Static assets (fonts, icons, templates for cards)
│   ├── handlers/          # Command, message, and callback query handlers
│   ├── keyboards/         # Inline and Reply keyboard markups
│   ├── states/            # FSM (Finite State Machine) state groups
│   ├── utils/             # Pillow card rendering engine & helper formatters
│   ├── config.py          # Bot configuration & token settings
│   └── main.py            # Telegram bot entry point & dispatcher polling runner
├── migrations/            # Alembic database migration scripts
├── .env.example           # Template for environment variables
├── .gitignore             # Git ignored files specification
├── alembic.ini            # Alembic migration environment config
├── poetry.lock            # Locked package dependencies tree
├── pyproject.toml         # Project dependencies & Poetry configuration
└── README.md              # Project documentation
```

## 🤖 Bot Commands

| Command | Description |
| :--- | :--- |
| **/daily** | Receive today's comprehensive daily weather forecast |
| **/forecast_range** | Receive multi-day forecasts for a specified range of days |
| **/now** | Receive real-time weather for your saved location |
| **/city_weather** | Receive current weather for any specified city or coordinates |
| **/set_city** | Configure or update your default city |
| **/set_schedule** | Create automated recurring daily weather alerts |
| **/settings** | View and manage your saved profile configurations |
| **/help** | Display the interactive usage guide and bot instructions |

## 🚀 Local Installation & Setup

#### Prerequisites

- **Python 3.12+**
- **Poetry**
- **PostgreSQL instance**

### 1. Clone the repository
```bash
git clone https://github.com/your-username/skysentry.git
cd skysentry
```

### 2. Install dependencies

```bash
poetry install
```

### 3. Configure environment variables
Copy the template and fill in your credentials: 
```bash
cp .env.example .env
```

Ensure your `.env` contains the required keys:

```text
BOT_TOKEN=your_telegram_bot_token

# PostgreSQL Configuration
DB_HOST=localhost
DB_PORT=5432
DB_USER=weather_user
DB_PASS=your_password
DB_NAME=weatherbot

# API URL
BACKEND_URL=[http://127.0.0.1:8000/api/v1](http://127.0.0.1:8000/api/v1)
```

### 4. Run database migrations

```bash
poetry run alembic upgrade head
```

### 5. Start the services

**Terminal 1 — FastAPI Backend & Scheduler:**

```bash
poetry run uvicorn backend.main:app --reload --port 8000
```

**Terminal 2 — Telegram Bot Client**

```bash
poetry run python -m bot.main
```