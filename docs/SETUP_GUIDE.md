# Setup Guide

## Prerequisites

| Tool | Min Version | Install |
|------|------------|---------|
| Python | 3.11+ | python.org |
| Node.js | 18+ | nodejs.org |
| PostgreSQL | 15+ (or use SQLite for dev) | postgresql.org |
| Redis | 6+ (optional, for Celery) | redis.io |
| Ollama | latest (optional, for AI) | ollama.ai |

---

## 1. Clone and Create Virtual Environment

```bash
git clone <repo-url> D:\CSP
cd D:\CSP
python -m venv .venv
.venv\Scripts\activate          # Windows
# source .venv/bin/activate     # Mac/Linux
```

## 2. Install Python Dependencies

```bash
pip install -r requirements.txt
```

## 3. Configure Environment Variables

```bash
copy .env.example .env
```

Edit `.env` with your values:

```env
SECRET_KEY=your-secret-key-here
DEBUG=True
DATABASE_URL=sqlite:///db.sqlite3          # dev (SQLite)
# DATABASE_URL=postgresql://user:pass@host:5432/csp_db  # production (Neon)
OLLAMA_BASE_URL=http://localhost:11434     # if using AI assistant
OLLAMA_MODEL=mistral:latest
OLLAMA_EMBED_MODEL=nomic-embed-text:latest
```

## 4. Run Migrations

```bash
python manage.py migrate
```

## 5. Load Village Data

```bash
python manage.py loaddata apps/villages/fixtures/villages.json
```

## 6. Create Superuser

```bash
python manage.py createsuperuser
```

## 7. Build Tailwind CSS (Development)

Tailwind is loaded via CDN in development — no build step required.

For production builds:
```bash
npm install
npm run build:css
```

## 8. Collect Static Files (Production)

```bash
python manage.py collectstatic --no-input
```

## 9. Run the Development Server

```bash
python manage.py runserver
```

Open http://127.0.0.1:8000

---

## Optional: AI Assistant Setup

1. Install Ollama: https://ollama.ai
2. Pull a model: `ollama pull llama3`
3. Start Ollama: `ollama serve`
4. Set in `.env`: `OLLAMA_BASE_URL=http://localhost:11434`, `OLLAMA_MODEL=mistral:latest`, and `OLLAMA_EMBED_MODEL=nomic-embed-text:latest`
5. Install LangChain extras from `requirements.txt`
6. Build the knowledge base: `python manage.py build_knowledge_base`

---

## Optional: Celery Background Tasks

Start Redis, then:
```bash
# Terminal 1 - worker
celery -A config worker --loglevel=info

# Terminal 2 - beat scheduler
celery -A config beat --loglevel=info
```

---

## Docker (All-in-one)

```bash
docker-compose up --build
```

This starts: web, worker, beat, redis, nginx.

---

## Settings Modules

| Module | Use when |
|--------|----------|
| `config.settings.development` | Local development |
| `config.settings.production` | Deployment |

Set with: `DJANGO_SETTINGS_MODULE=config.settings.development`
