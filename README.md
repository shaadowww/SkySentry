# Weather Bot

[![Python](https://img.shields.io/badge/Python-3.13-blue?logo=python&logoColor=white)](https://www.python.org/)
[![Aiogram](https://img.shields.io/badge/Aiogram-3.x-orange?logo=telegram&logoColor=white)](https://docs.aiogram.dev/)
[![FastAPI](https://img.shields.io/badge/FastAPI-Standard-009688?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![Poetry](https://img.shields.io/badge/Poetry-2.0+-blueviolet?logo=poetry&logoColor=white)](https://python-poetry.org/)

An asynchronous weather monitoring service. Built on a modern stack with a focus on performance and code cleanliness.


## Main Features:

- Real-time weather updates for your city.
- Request caching in Redis to optimize API limits.
- Fully asynchronous architecture.
- Daily weather dispatch scheduling.

## Technology Stack
- **Backend** Python 3.13 (Asyncio)
- **Dependency Manager** Poetry
- **Bot Logic** Aiogram 3.x
- **API Framework** FastAPI [standard]
- **Database** SQLAlchemy + PostgreSQL (asyncpg)
- **Cache** Redis

Project Architecture: 
```text
shadow_weather_bot/
├── bot/                # Command handling and bot logic
├── database/           # Table models and asynchronous sessions
├── fastapi/            # API endpoints and logic
├── redis/              # Cache interaction layer
├── .env.example        # Configuration template
└── pyproject.toml      # Project configuration and dependencies
```