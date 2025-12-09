# MyTeacher - AI DevOps Mentor

A hyper-personalized AI-powered DevOps learning platform designed for ADHD-friendly, step-by-step learning with persistent memory and adaptive teaching strategies.

## Features

- **Personalized Learning**: AI mentor adapts to your learning style and pace
- **ADHD-Friendly**: Focus mode, micro-steps, and break reminders
- **Dual-Panel Interface**: Learning pad on left, AI chat on right
- **Interactive Exercises**: Code in Python, Bash, Terraform, Pulumi with auto-grading
- **Progress Tracking**: Never lose your progress, AI remembers your struggles
- **Node-Based Curriculum**: Unlock advanced topics as you master prerequisites

## Tech Stack

### Backend
- **FastAPI** (Python 3.11+)
- **MongoDB** for data storage
- **Redis** for caching and job queues
- **JWT** authentication
- **Docker** for sandbox code execution

### Frontend
- **Next.js 14** (React 18)
- **TypeScript**
- **TailwindCSS** for styling
- **Zustand** for state management
- **Monaco Editor** for code editing

### AI
- **Claude** (Anthropic) for AI mentor
- **Pinecone/Weaviate** for vector memory (Phase 2)

## Project Structure

```
myteacher/
├── backend/                 # FastAPI backend
│   ├── app/
│   │   ├── api/            # API routes
│   │   ├── models/         # Pydantic models
│   │   ├── services/       # Business logic
│   │   ├── db/             # Database connections
│   │   └── utils/          # Utilities
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/               # Next.js frontend
│   ├── src/
│   │   ├── app/           # Next.js pages
│   │   ├── components/    # React components
│   │   ├── stores/        # Zustand stores
│   │   ├── lib/           # API client
│   │   └── types/         # TypeScript types
│   └── package.json
├── scripts/               # Utility scripts
│   └── seed_database.py  # Database seeding
├── docker-compose.yml    # Local development
└── README.md
```

## Getting Started

### Prerequisites

- Docker & Docker Compose
- Node.js 18+ (for frontend development)
- Python 3.11+ (for backend development)

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/johnbekele/myTeach.git
   cd myteacher
   ```

2. **Set up environment variables**

   Backend:
   ```bash
   cd backend
   cp .env.example .env
   # Edit .env with your configuration
   ```

   Frontend:
   ```bash
   cd frontend
   cp .env.example .env.local
   # Edit .env.local with your configuration
   ```

3. **Start services with Docker Compose**
   ```bash
   docker-compose up -d
   ```

   This starts:
   - MongoDB on `localhost:27017`
   - Redis on `localhost:6379`
   - Backend API on `localhost:8000`

4. **Seed the database**
   ```bash
   cd scripts
   python seed_database.py
   ```

5. **Install frontend dependencies**
   ```bash
   cd frontend
   npm install
   ```

6. **Start frontend development server**
   ```bash
   npm run dev
   ```

   Frontend runs on `http://localhost:3000`

### Testing the Application

1. Open `http://localhost:3000` in your browser
2. Register a new account
3. Login and explore the dashboard
4. Navigate to Learning Path to see available modules
5. Chat with the AI mentor in the right panel

## API Documentation

Once the backend is running, visit:
- **API Docs**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

## Development Workflow

### Backend Development

```bash
cd backend
# Install dependencies
pip install -r requirements.txt

# Run locally (without Docker)
uvicorn app.main:app --reload --port 8000
```

### Frontend Development

```bash
cd frontend
# Install dependencies
npm install

# Run dev server
npm run dev

# Build for production
npm run build
```

### Database Management

**Seed database:**
```bash
python scripts/seed_database.py
```

**Connect to MongoDB:**
```bash
docker exec -it myteacher-mongodb mongosh
use myteacher
db.users.find()
```

## Phase 1 Completion Status

✅ Backend API structure with FastAPI
✅ MongoDB and Redis integration
✅ User authentication (JWT)
✅ Node and Exercise models
✅ Frontend with Next.js and TailwindCSS
✅ Dual-panel layout (Learning Pad + AI Chat)
✅ State management with Zustand
✅ Docker Compose for local development
✅ Database seeding script

## Roadmap

### Phase 2: Exercise System (Week 3-4)
- Sandbox execution for Python and Bash
- Auto-grader implementation
- Monaco code editor integration
- Exercise submission and results

### Phase 3: AI Integration (Week 5-6)
- Claude API integration
- AI mentor chat functionality
- Exercise grading agent
- Teaching strategy agent

### Phase 4: Memory & Personalization (Week 7-8)
- Vector database setup (Pinecone)
- Memory agent for tracking weaknesses
- Personalized exercise generation
- Adaptive difficulty

### Phase 5: ADHD Features (Week 9)
- Focus mode implementation
- Panic button (simplify content)
- Break reminders
- Step-by-step micro-tasks

### Phase 6: Production (Week 10+)
- Terraform/Pulumi exercise support
- Advanced grading rubrics
- Performance optimization
- Deployment to cloud

## Contributing

This is currently a solo development project. Contributions will be welcomed after Phase 1 is complete.

## License

MIT License

## Contact

For questions or feedback, please open an issue on GitHub.

---

**Built with ❤️ for ADHD learners who want to master DevOps**
