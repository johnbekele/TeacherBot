# Teacherbot

**AI-powered learning platform** — structured learning paths, step-by-step content, coding exercises with AI grading, and an in-app AI tutor.

**Developed by Yohans Bekele**

---

## Prerequisites

- **Node.js** 18+ and npm  
- **Python** 3.10+ and pip  
- **MongoDB** 6+  
- **Redis** 7+ (optional)

---

## Setup and Run

### 1. Clone and open the project

```bash
git clone <your-repo-url>
cd myteacher
```

### 2. Backend

```bash
cd backend
python3 -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
```

Edit **backend/.env** and set at least:

- `SECRET_KEY` — long random string (e.g. `openssl rand -hex 32`)
- `MONGODB_URL` — e.g. `mongodb://localhost:27017`
- `MONGODB_DB_NAME` — e.g. `myteacher`
- `ANTHROPIC_API_KEY` — your Anthropic API key (for AI tutor and grading)
- `REDIS_URL` — e.g. `redis://localhost:6379` (optional)

Start the API:

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

- **API:** http://localhost:8000  
- **OpenAPI (Swagger):** http://localhost:8000/docs  

### 3. Frontend

In a new terminal:

```bash
cd frontend
npm install
cp .env.example .env
```

Edit **frontend/.env** and set:

- `NEXT_PUBLIC_API_URL` — backend URL, e.g. `http://localhost:8000`

Start the app:

```bash
npm run dev
```

- **App:** http://localhost:3000  

### 4. (Optional) Seed the database

From the project root, with MongoDB running and backend venv activated:

```bash
python3 scripts/seed_database.py
```

---

## Test the app

### Create an account and log in

1. Open http://localhost:3000  
2. Click **Register**  
3. Enter email, password, full name and register  
4. You are logged in; complete onboarding if shown  
5. Use **Dashboard**, **Learning paths**, **Learn**, **Exercises**, and the **Chat** tutor  

### Run frontend lint and build

```bash
cd frontend
npm run lint
npm run build
```

### Run backend type-check (optional)

```bash
cd frontend
npx tsc --noEmit
```

---

## Run with Docker

From the project root:

```bash
docker-compose up -d
```

This starts MongoDB, Redis, and the backend. Then run the frontend locally:

```bash
cd frontend
npm run dev
```

Set **frontend/.env** `NEXT_PUBLIC_API_URL=http://localhost:8000` so the app talks to the backend in Docker.

---

## Environment variables

### Backend (backend/.env)

| Variable | Description | Example |
|----------|-------------|---------|
| SECRET_KEY | JWT signing key | Long random string |
| MONGODB_URL | MongoDB connection URL | mongodb://localhost:27017 |
| MONGODB_DB_NAME | Database name | myteacher |
| REDIS_URL | Redis URL (optional) | redis://localhost:6379 |
| ANTHROPIC_API_KEY | Anthropic API key for AI | Your key |
| CORS_ORIGINS | Allowed frontend origins (optional) | http://localhost:3000 |

### Frontend (frontend/.env)

| Variable | Description | Example |
|----------|-------------|---------|
| NEXT_PUBLIC_API_URL | Backend API base URL | http://localhost:8000 |

For production, set `NEXT_PUBLIC_API_URL` to your deployed backend URL (e.g. https://myteacher-rr7d.onrender.com).

---

## Tech stack

| Layer | Technology |
|-------|------------|
| Frontend | Next.js 14, React 18, TypeScript, Tailwind, Zustand, Monaco Editor |
| Backend | FastAPI, Python 3.x, Pydantic |
| Database | MongoDB (Motor) |
| Cache | Redis (optional) |
| AI | Anthropic Claude (tutor, grading) |
| Auth | JWT |
| Version control | Git (GitHub) |
| Containers | Docker, docker-compose (optional) |

---

## Project structure

```
myteacher/
├── backend/              # FastAPI API
│   ├── app/
│   │   ├── api/v1/       # Auth, nodes, exercises, chat, learning_paths, etc.
│   │   ├── ai/           # Tutor, hint agent, orchestrator, content generator
│   │   ├── db/           # MongoDB, Redis
│   │   ├── models/       # Pydantic models
│   │   └── services/     # AI grading
│   ├── requirements.txt
│   └── .env.example
├── frontend/             # Next.js app
│   ├── src/
│   │   ├── app/          # Pages (login, dashboard, learn, exercise, etc.)
│   │   ├── components/
│   │   ├── stores/       # Zustand (auth, chat, exercise, node)
│   │   ├── lib/          # api.ts, utils.ts
│   │   └── types/
│   ├── package.json
│   └── .env.example
├── scripts/              # seed_database.py, etc.
├── docker-compose.yml
└── README.md
```

---

## Deployment

- **Frontend:** Build with `npm run build`, then run `npm start` or deploy the output (e.g. Vercel). Set `NEXT_PUBLIC_API_URL` to your production backend URL at build time.  
- **Backend:** Run with Uvicorn (e.g. on Render). Set `CORS_ORIGINS` or rely on the defaults (Vercel URLs are already allowed in code). Use a production `SECRET_KEY`, MongoDB URL, and Anthropic API key.

---

## License

(Add your license here.)
