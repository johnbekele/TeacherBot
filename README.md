# Teacherbot

**AI-powered learning platform** — structured learning paths, step-by-step content, coding exercises with AI grading, and an in-app AI tutor.

---

## Quick Start

### Prerequisites

- Node.js 18+, npm
- Python 3.10+, pip
- MongoDB 6+
- Redis 7+ (optional)

### Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env      # Edit: SECRET_KEY, MONGODB_URL, ANTHROPIC_API_KEY, CORS_ORIGINS
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

API: **http://localhost:8000** · Docs: **http://localhost:8000/docs**

### Frontend

```bash
cd frontend
npm install
cp .env.example .env      # Set NEXT_PUBLIC_API_URL=http://localhost:8000
npm run dev
```

App: **http://localhost:3000**

### With Docker

```bash
docker-compose up -d       # MongoDB, Redis, backend
cd frontend && npm run dev # Frontend locally
```

---

## Tech Stack

| Layer      | Technology                          |
|-----------|--------------------------------------|
| Frontend  | Next.js 14, React 18, TypeScript, Tailwind, Zustand, Monaco Editor |
| Backend   | FastAPI, Python 3.x, Pydantic       |
| Database  | MongoDB (Motor)                     |
| Cache     | Redis (optional)                    |
| AI        | Anthropic Claude (tutor, grading)   |
| Auth      | JWT                                 |
| Version   | Git (GitHub)                        |
| Containers| Docker, docker-compose (optional)   |

---

## Documentation

| Document | Description |
|----------|-------------|
| [**docs/PROJECT_DOCUMENTATION.md**](docs/PROJECT_DOCUMENTATION.md) / [**.docx**](docs/PROJECT_DOCUMENTATION.docx) | **Main project doc** — concept, design, implementation, testing, evaluation criteria |
| [**docs/USER_MANUAL.md**](docs/USER_MANUAL.md) / [**.docx**](docs/USER_MANUAL.docx) | End-user guide — registration, onboarding, learning paths, exercises, chat, settings |
| [**docs/ADMIN_MANUAL.md**](docs/ADMIN_MANUAL.md) / [**.docx**](docs/ADMIN_MANUAL.docx) | Administrator guide — env, Docker, DB setup, deployment |
| [**docs/TESTING.md**](docs/TESTING.md) / [**.docx**](docs/TESTING.docx) | Testing strategy — unit, integration, E2E, beta testing |
| [**docs/DEVELOPMENT_IMPLEMENTATION.md**](docs/DEVELOPMENT_IMPLEMENTATION.md) / [**.docx**](docs/DEVELOPMENT_IMPLEMENTATION.docx) | Development and implementation process |

**Regenerate Word (.docx) from Markdown:**

```bash
python3 -m venv .venv-docs && .venv-docs/bin/pip install -r scripts/requirements-docs.txt
.venv-docs/bin/python scripts/md_to_docx.py
```

---

## Project Structure

```
myteacher/
├── backend/          # FastAPI API, AI agents, DB
│   ├── app/
│   │   ├── api/v1/   # Auth, nodes, exercises, chat, learning_paths, etc.
│   │   ├── ai/       # Tutor, hint agent, orchestrator, content generator
│   │   ├── db/       # MongoDB, Redis
│   │   ├── models/   # Pydantic models
│   │   └── services/ # AI grading, etc.
│   ├── requirements.txt
│   └── .env.example
├── frontend/         # Next.js app
│   ├── src/
│   │   ├── app/      # Pages (login, dashboard, learn, exercise, etc.)
│   │   ├── components/
│   │   ├── stores/   # Zustand (auth, chat, exercise, node)
│   │   ├── lib/      # api.ts, utils.ts
│   │   └── types/
│   ├── package.json
│   └── .env.example
├── docs/             # Project documentation
├── scripts/          # seed_database.py, etc.
├── docker-compose.yml
└── README.md
```

---

## License

(Add your license here.)
