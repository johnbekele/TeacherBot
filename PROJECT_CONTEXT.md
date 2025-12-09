# MyTeacher AI - Complete Project Context

**Last Updated:** December 9, 2025
**Version:** 2.0 - Production Ready
**Status:** ✅ Fully Functional with AI-Driven Adaptive Learning

---

## 📋 Executive Summary

MyTeacher AI is an adaptive learning platform powered by Claude AI that provides personalized programming education with real-time feedback, dynamic content generation, and intelligent exercise creation. The system features three specialized AI agents (Planning AI, Learning Orchestrator, and Tutor Agent) that work together to create a seamless, proactive learning experience.

### Key Achievements
- ✅ **AI-Driven Learning**: Fully autonomous AI teacher that creates content and exercises on-demand
- ✅ **Proactive Progression**: Automatic navigation and progression without manual button clicks
- ✅ **Unified Chat Interface**: All AI interactions consolidated in chat with rich formatting
- ✅ **Dark Mode Support**: Complete theme support across all components
- ✅ **Real-time Code Execution**: Sandboxed Python/JavaScript execution with instant feedback
- ✅ **Adaptive Difficulty**: AI adjusts based on user performance and weak points
- ✅ **One-Question-at-a-Time**: Natural conversational flow for better engagement

---

## 🏗️ System Architecture

### Technology Stack

#### Backend (Python/FastAPI)
- **Framework**: FastAPI 0.104.1
- **AI Integration**: Anthropic Claude 3.5 Sonnet (claude-3-5-sonnet-20241022)
- **Database**: MongoDB (Motor async driver)
- **Caching**: Redis
- **Tool Calling**: Custom tool registry with 12+ AI-callable tools
- **Authentication**: JWT with bcrypt password hashing

#### Frontend (Next.js 14)
- **Framework**: Next.js 14.2.5 with App Router
- **Language**: TypeScript 5.x
- **Styling**: TailwindCSS 3.4 with dark mode
- **State Management**: Zustand 4.5
- **UI Components**: shadcn/ui (Radix UI primitives)
- **Animations**: Framer Motion 11.11
- **Code Editor**: Monaco Editor (@monaco-editor/react)
- **Markdown**: react-markdown with syntax highlighting

#### Infrastructure
- **Containerization**: Docker + Docker Compose
- **Services**: Backend (FastAPI), MongoDB, Redis
- **Ports**: Backend :8000, MongoDB :27017, Redis :6379, Frontend :3000

---

## 🤖 AI System Architecture

### Three-Agent System

#### 1. **Planning AI** (`context_type='planning'`)
**Purpose**: Creates personalized learning paths by asking questions and generating nodes

**Tools Available**:
- `create_learning_node` - Generate new learning topics
- `show_interactive_component` - Display quizzes/visualizations
- `execute_code` - Demonstrate concepts live

**Behavior**:
- Asks ONE question at a time (discovery phase)
- Assesses user's level and goals
- Creates structured learning paths with prerequisites
- Generates nodes that appear in user's learning dashboard

**Location**: FloatingChat component on Dashboard (bottom-right floating button)

---

#### 2. **Learning Orchestrator** (`context_type='learning_session'`)
**Purpose**: Main teaching AI that actively teaches through content and exercise generation

**Tools Available** (12 total):
- `display_learning_content` - Create explanatory notes
- `generate_exercise` - Create practice problems
- `provide_feedback` - Give detailed, personalized feedback
- `navigate_to_next_step` - Auto-navigate to exercises/content
- `update_user_progress` - Track learning milestones
- `execute_code` - Run code snippets and show output
- `show_interactive_component` - Render interactive elements
- `save_user_profile` - Store user preferences from onboarding
- `create_learning_node` - Generate new topics mid-session

**Behavior**:
- Proactive: Creates exercises immediately after explanations
- Automatic: Navigates user to next steps without manual clicks
- Adaptive: Adjusts difficulty based on weak points
- Conversational: ONE question at a time when needed
- Tool-driven: Never just describes - always uses tools to create

**Location**: Active learning sessions (learn/[nodeId], exercise/[exerciseId])

---

#### 3. **Tutor Agent** (`context_type='general'`)
**Purpose**: Simple Q&A assistant for quick explanations without tool usage

**Tools Available**: None (pure conversational)

**Behavior**:
- Answers specific questions about concepts
- Provides explanations and clarifications
- No content/exercise generation
- Fallback when tools aren't needed

**Location**: Triggered by semantic intent detection for pure Q&A

---

### AI Routing Logic

**Decision Flow** (`backend/app/api/v1/chat.py`):
```python
# Step 1: Check context_type
if context_type == "onboarding":
    → Use ONBOARDING_PROMPT
elif context_type == "planning":
    → Use PLANNING_PROMPT ✅ Fixed!
elif context_type in ["learning_session", "exercise", "node"]:
    → Use LEARNING_ORCHESTRATOR_PROMPT
else:
    # Step 2: Semantic intent detection with Claude Haiku
    requires_tools = await should_use_orchestrator(message)
    if requires_tools:
        → Use LEARNING_ORCHESTRATOR_PROMPT
    else:
        → Use TUTOR_AGENT (simple Q&A)
```

**Critical Fix Applied**: FloatingChat was sending `'planner'` instead of `'planning'`, causing routing to fail and use Learning Orchestrator instead of Planning AI.

---

## 🔧 Recent Critical Fixes

### 1. **Planning AI Routing Bug** ✅ FIXED
**Problem**: FloatingChat sent `context_type='planner'` but backend expected `'planning'`
**Impact**: Planning AI never activated - Learning Orchestrator responded instead
**Fix**: Changed all `'planner'` references to `'planning'` in FloatingChat.tsx
**Files Modified**:
- `frontend/src/components/chat/FloatingChat.tsx` (4 changes)
- Added diagnostic logging to `backend/app/api/v1/chat.py`
- Added endpoint logging to `frontend/src/stores/chatStore.ts`

### 2. **Proactive AI Teacher** ✅ IMPLEMENTED
**Problem**: Required manual "Continue Practice" button clicks
**Fix**: Auto-navigation + 3-second auto-continue timer
**Files Modified**:
- `frontend/src/components/chat/ChatPanel.tsx` - Auto-navigation via router.push
- `frontend/src/app/learn/[nodeId]/page.tsx` - Auto-continue timer
- `backend/app/ai/tool_handlers.py` - navigate_to_next_step tool

### 3. **Unified Chat Interface** ✅ IMPLEMENTED
**Problem**: Split feedback (ExerciseResults panel + Chat)
**Fix**: Everything in chat with rich formatting
**Files Modified**:
- `frontend/src/components/exercise/ExerciseView.tsx` - Removed ExerciseResults
- `frontend/src/components/chat/MessageBubble.tsx` - Added grading display
- `backend/app/ai/prompts/system_prompts.py` - EXERCISE_FEEDBACK_PROMPT

### 4. **Dark Mode UI** ✅ FIXED
**Problem**: 60+ hardcoded light mode colors causing confusion
**Fix**: Added `dark:` variants to all components
**Files Modified** (32+ locations):
- `frontend/src/components/exercise/ExerciseView.tsx` (14 fixes)
- `frontend/src/components/learning/DynamicContentRenderer.tsx` (18 fixes)
- `frontend/src/components/exercise/CodeEditor.tsx` - Monaco theme switching
- `frontend/src/styles/globals.css` - Scrollbar dark mode

### 5. **AI Conversation Rules** ✅ ENFORCED
**Problem**: AI asking multiple questions at once
**Fix**: Added explicit ONE-question-at-a-time rules with examples
**Files Modified**:
- `backend/app/ai/prompts/system_prompts.py` - Both PLANNING_PROMPT and LEARNING_ORCHESTRATOR_PROMPT
- Added ❌ WRONG / ✅ CORRECT examples
- Added visual indicators (🚨, 👉, 🛑)

### 6. **DateTime Serialization** ✅ FIXED
**Problem**: `datetime.utcnow()` not JSON serializable in provide_feedback tool
**Fix**: Changed to `datetime.utcnow().isoformat()`
**Files Modified**: `backend/app/ai/tool_handlers.py:167`

---

## 📁 Project Structure

```
myteacher/
├── backend/
│   ├── app/
│   │   ├── ai/
│   │   │   ├── agents/
│   │   │   │   ├── hint_agent.py          # Tiered hints system
│   │   │   │   ├── learning_orchestrator.py # Main teaching AI
│   │   │   │   └── tutor_agent.py         # Simple Q&A agent
│   │   │   ├── prompts/
│   │   │   │   └── system_prompts.py      # All AI prompts (3 agents)
│   │   │   ├── behavioral_tools.py        # Behavioral tracking (future)
│   │   │   ├── chat_service.py            # Claude API integration + retry logic
│   │   │   ├── tool_handlers.py           # 12 tool implementations
│   │   │   └── tool_registry.py           # Tool definitions for Claude
│   │   ├── api/
│   │   │   └── v1/
│   │   │       ├── auth.py                # JWT authentication
│   │   │       ├── chat.py                # AI routing logic ⭐ CRITICAL
│   │   │       ├── exercises.py           # Exercise submission + grading
│   │   │       ├── learning_session.py    # Learning session endpoints
│   │   │       ├── nodes.py               # Learning node CRUD
│   │   │       ├── onboarding.py          # User profiling
│   │   │       └── progress.py            # Progress tracking
│   │   ├── models/
│   │   │   ├── user_profile.py            # User learning profile
│   │   │   └── (schemas.py)               # Pydantic models
│   │   ├── services/
│   │   │   └── ai_grading_service.py      # AI-powered grading (future)
│   │   ├── config.py                      # Settings management
│   │   ├── database.py                    # MongoDB connection
│   │   └── dependencies.py                # FastAPI dependencies
│   ├── util/                              # ⭐ DEPLOYMENT DOCS HERE
│   │   ├── AWS_DEPLOYMENT.md              # AWS architecture
│   │   └── DEPLOYMENT_PLAN.md             # Step-by-step guide
│   ├── Dockerfile
│   ├── requirements.txt
│   └── main.py
├── frontend/
│   ├── src/
│   │   ├── app/
│   │   │   ├── dashboard/page.tsx         # Dashboard with stats
│   │   │   ├── exercise/[exerciseId]/page.tsx # Exercise page
│   │   │   ├── learn/[nodeId]/page.tsx    # Learning content page
│   │   │   ├── login/page.tsx             # Authentication
│   │   │   ├── register/page.tsx
│   │   │   ├── settings/page.tsx
│   │   │   └── layout.tsx                 # Root layout + FloatingChat
│   │   ├── components/
│   │   │   ├── chat/
│   │   │   │   ├── ChatPanel.tsx          # Main chat component ⭐
│   │   │   │   ├── FloatingChat.tsx       # Planning AI chat ⭐ FIXED
│   │   │   │   ├── FloatingChatWrapper.tsx
│   │   │   │   ├── MessageBubble.tsx      # Rich message rendering
│   │   │   │   └── InteractiveComponent.tsx
│   │   │   ├── exercise/
│   │   │   │   ├── CodeEditor.tsx         # Monaco editor wrapper
│   │   │   │   └── ExerciseView.tsx       # Exercise interface
│   │   │   ├── learning/
│   │   │   │   └── DynamicContentRenderer.tsx # AI-generated content
│   │   │   ├── layout/
│   │   │   │   ├── AppLayout.tsx          # Main layout wrapper
│   │   │   │   ├── AppSidebar.tsx
│   │   │   │   ├── LeftPanel.tsx          # Learning pad
│   │   │   │   └── RightPanel.tsx         # Chat panel
│   │   │   ├── providers/
│   │   │   │   ├── AuthProvider.tsx
│   │   │   │   └── ThemeProvider.tsx      # Dark mode provider
│   │   │   └── ui/                        # shadcn/ui components
│   │   ├── stores/
│   │   │   ├── authStore.ts               # Authentication state
│   │   │   ├── chatStore.ts               # Chat + AI actions ⭐
│   │   │   └── exerciseStore.ts           # Exercise state
│   │   ├── contexts/
│   │   │   └── ChatContext.tsx            # Chat context provider
│   │   ├── lib/
│   │   │   ├── api.ts                     # API client
│   │   │   └── utils.ts
│   │   └── styles/
│   │       └── globals.css                # Global styles + dark mode
│   ├── package.json
│   └── tailwind.config.js
├── docker-compose.yml
├── PROJECT_CONTEXT.md                     # ⭐ THIS FILE
└── README.md
```

---

## 🗄️ Database Schema

### Collections

#### 1. **users**
```javascript
{
  _id: ObjectId,
  email: string,
  hashed_password: string,
  full_name: string,
  created_at: datetime,
  is_active: boolean,
  settings: {
    pace_preference: "self_paced" | "structured",
    adhd_mode: boolean,
    focus_mode: boolean,
    break_reminders: boolean
  }
}
```

#### 2. **user_profiles**
```javascript
{
  _id: ObjectId,
  user_id: string,
  experience_level: "beginner" | "intermediate" | "advanced",
  learning_goals: string[],
  background: string,
  learning_style: "visual" | "hands-on" | "reading" | "mixed",
  adhd_accommodations: boolean,
  available_time: string,
  specific_interests: string[],
  weak_points: [{
    topic: string,
    description: string,
    identified_at: datetime,
    occurrences: int,  // Incremented on failures
    exercises_failed: [exercise_ids],
    last_seen: datetime
  }],
  strong_areas: string[],
  total_exercises_completed: int,
  total_exercises_failed: int,
  average_score: float,
  last_active: datetime,
  created_at: datetime
}
```

#### 3. **learning_nodes**
```javascript
{
  _id: ObjectId,
  node_id: string,
  title: string,
  description: string,
  difficulty: "beginner" | "intermediate" | "advanced",
  estimated_duration: int,  // minutes
  prerequisites: [node_ids],
  skills_taught: string[],
  content: {
    introduction: string,
    concepts: string[],
    learning_objectives: string[],
    practical_applications: string[],
    sections: []
  },
  exercises: [exercise_ids],
  created_by: "seed" | "ai",
  created_for_user: string | null,  // For AI-generated nodes
  created_at: datetime,
  tags: string[],
  status: "active" | "archived"
}
```

#### 4. **exercises**
```javascript
{
  _id: ObjectId,
  exercise_id: string,
  node_id: string,
  title: string,
  description: string,
  prompt: string,
  type: "python" | "javascript" | "multiple_choice",
  difficulty: "easy" | "medium" | "hard",
  starter_code: string,
  solution: string,
  test_cases: [{
    test_id: string,
    description: string,
    input: object,
    expected_output: object,
    validation_script: string
  }],
  hints: [string],
  grading_rubric: {
    correctness_weight: float,
    style_weight: float,
    efficiency_weight: float
  },
  generated_by_ai: boolean,
  created_for_user: string | null,
  created_at: datetime
}
```

#### 5. **exercise_attempts**
```javascript
{
  _id: ObjectId,
  user_id: string,
  exercise_id: string,
  code: string,
  language: "python" | "javascript",
  score: int,
  test_results: [{
    test_id: string,
    passed: boolean,
    output: string,
    error: string
  }],
  feedback: string,
  ai_feedback: string,  // From Learning Orchestrator
  ai_next_step: {
    navigation: [actions],
    exercise_id: string,
    content_id: string
  },
  submitted_at: datetime,
  graded_at: datetime
}
```

#### 6. **user_progress**
```javascript
{
  _id: ObjectId,
  user_id: string,
  node_id: string,
  status: "not_started" | "in_progress" | "completed",
  completion_percentage: int,
  started_at: datetime,
  completed_at: datetime,
  created_at: datetime,
  updated_at: datetime
}
```

#### 7. **chat_sessions**
```javascript
{
  _id: ObjectId,
  user_id: string,
  context_type: "planning" | "learning_session" | "onboarding" | "general",
  context_id: string,  // node_id, exercise_id, or "dashboard"
  is_active: boolean,
  created_at: datetime,
  updated_at: datetime
}
```

#### 8. **chat_messages**
```javascript
{
  _id: ObjectId,
  session_id: string,
  role: "user" | "assistant",
  content: string,
  created_at: datetime,
  tool_calls: [{
    tool_name: string,
    input: object,
    result: object
  }]
}
```

#### 9. **learning_content** (AI-generated)
```javascript
{
  _id: ObjectId,
  content_id: string,
  title: string,
  content_type: "note" | "tutorial" | "explanation",
  sections: [{
    heading: string,
    body: string,
    code_example: string,
    language: string
  }],
  created_for_user: string,
  generated_by_ai: boolean,
  created_at: datetime
}
```

---

## 🔐 Authentication Flow

1. **Registration**: `/api/v1/auth/register`
   - Email + password + full name
   - Password hashed with bcrypt
   - Returns JWT access token

2. **Login**: `/api/v1/auth/login`
   - Email + password validation
   - Returns JWT with user_id and email claims
   - Token stored in localStorage

3. **Protected Routes**:
   - Token sent in `Authorization: Bearer <token>` header
   - FastAPI dependency `get_current_user_id` validates and extracts user_id
   - Auto-logout on 401 (token expiration)

4. **Token Expiration**: 7 days (configurable in `config.py`)

---

## 🎯 User Journey

### 1. **Onboarding** (First-time users)
- **Route**: `/onboarding`
- **AI**: Onboarding Agent
- **Flow**: Assessment questions → Profile creation → Welcome

### 2. **Planning** (Creating learning paths)
- **Route**: `/dashboard` (FloatingChat)
- **AI**: Planning AI ✅ FIXED
- **Flow**:
  1. AI asks: "What would you like to learn?"
  2. User: "I want to learn Python"
  3. AI asks: "What's your experience level with Python?"
  4. User: "Beginner"
  5. AI creates nodes: Python Basics, Variables & Types, etc.
  6. Nodes appear in dashboard

### 3. **Learning** (Active learning session)
- **Route**: `/learn/{node_id}`
- **AI**: Learning Orchestrator
- **Flow**:
  1. Auto-start: AI introduces topic with `display_learning_content`
  2. 3-second timer → auto-continue
  3. AI creates exercise with `generate_exercise`
  4. Auto-navigate to `/exercise/{exercise_id}`
  5. User submits code
  6. AI grades and provides feedback
  7. If passed → AI auto-creates next exercise
  8. If failed → AI offers hints or review

### 4. **Practice** (Exercise completion)
- **Route**: `/exercise/{exercise_id}`
- **AI**: Learning Orchestrator
- **Flow**:
  1. User writes code in Monaco editor
  2. Click "Submit Code"
  3. Backend executes in sandbox
  4. AI analyzes results + weak points
  5. Feedback in chat with score badge
  6. Auto-navigation to next exercise

---

## 🚀 Key Features

### AI-Driven
- ✅ Dynamic content generation based on user level
- ✅ Real-time exercise creation tailored to weak points
- ✅ Adaptive difficulty adjustment
- ✅ Personalized feedback with specific code references
- ✅ Proactive progression without manual intervention

### User Experience
- ✅ Dark mode with complete theme support
- ✅ ADHD-friendly design (focus mode, minimal distractions)
- ✅ Responsive layout (desktop, tablet, mobile)
- ✅ Rich markdown rendering with syntax highlighting
- ✅ Framer Motion animations (60 FPS)
- ✅ Code editor with autocomplete and error detection

### Performance
- ✅ Next.js 14 App Router (faster routing)
- ✅ React.memo for message bubbles (prevents re-renders)
- ✅ Debounced code editor (300ms) for smooth typing
- ✅ Auto-scroll chat with smooth behavior
- ✅ Lazy loading with dynamic imports

### Developer Experience
- ✅ TypeScript for type safety
- ✅ Modular architecture (easy to extend)
- ✅ Comprehensive logging for debugging
- ✅ Docker Compose for one-command setup
- ✅ Hot reload for frontend and backend

---

## 🐛 Known Issues & Future Enhancements

### Known Issues
1. **AI Grading Model 404**: `claude-3-5-sonnet-20241022` sometimes returns 404 → Falls back to heuristic grading (50/100)
2. **Memory Usage**: Chat history can grow large in long sessions → Need periodic cleanup
3. **Code Execution Security**: Currently sandboxed but not fully isolated → Consider AWS Lambda for execution

### Planned Enhancements
1. **Streaming Responses**: Server-Sent Events for token-by-token AI responses
2. **Message Virtualization**: `react-window` for 500+ messages without lag
3. **AI-Powered Grading**: Full Claude integration for nuanced feedback
4. **Behavioral Tracking**: Record struggle indicators and engagement metrics
5. **Error Pattern Analysis**: Categorize errors (syntax, logic, conceptual, algorithmic)
6. **Streak System**: Daily learning streaks with freeze days
7. **Progress Analytics**: Charts and insights dashboard
8. **Social Learning**: Code sharing and peer review
9. **Mobile App**: React Native with offline support
10. **Multi-language Support**: i18n for Spanish, French, etc.

---

## 📊 Testing Checklist

### Critical Paths to Test

#### 1. **Planning AI** ✅ FIXED
- [ ] Go to Dashboard
- [ ] Open FloatingChat (bottom-right)
- [ ] Send: "hi i want to learn python"
- [ ] Verify: Backend logs show `✅ ROUTING: Selected PLANNING prompt`
- [ ] Verify: AI asks ONE question at a time
- [ ] Verify: Nodes created after conversation

#### 2. **Proactive Learning** ✅ IMPLEMENTED
- [ ] Click on any learning node
- [ ] Verify: Auto-start (no manual click)
- [ ] Verify: 3-second timer auto-continues
- [ ] Verify: Auto-navigate to exercise
- [ ] Submit code
- [ ] Verify: Auto-navigate to next exercise if passed

#### 3. **Dark Mode** ✅ FIXED
- [ ] Toggle dark mode in header
- [ ] Verify: All text readable
- [ ] Verify: Monaco editor uses vs-dark theme
- [ ] Verify: No white backgrounds in dark mode
- [ ] Verify: Scrollbar visible and styled

#### 4. **Chat Interface** ✅ UNIFIED
- [ ] Submit exercise
- [ ] Verify: Score displayed in chat (not separate panel)
- [ ] Request hint
- [ ] Verify: Hint appears in chat
- [ ] Verify: No ExerciseResults panel visible

---

## 🔒 Security Considerations

### Implemented
- ✅ JWT token authentication with 7-day expiration
- ✅ Password hashing with bcrypt (cost factor 12)
- ✅ CORS configuration (FastAPI middleware)
- ✅ Input validation with Pydantic
- ✅ MongoDB injection prevention (parameterized queries)
- ✅ Code execution timeout (5 seconds)

### TODO
- [ ] Rate limiting on API endpoints (10 requests/minute per user)
- [ ] API key rotation for Anthropic
- [ ] Content Security Policy (CSP) headers
- [ ] HTTPS in production (Let's Encrypt)
- [ ] Database encryption at rest
- [ ] Audit logging for sensitive operations

---

## 📈 Metrics & Monitoring (Recommended)

### Application Metrics
- API response times (p50, p95, p99)
- AI tool execution success rates
- Error rates by endpoint
- Active user sessions
- Database query performance

### User Metrics
- Daily active users (DAU)
- Average session length
- Exercise completion rate
- AI interaction count per session
- Weak point identification accuracy
- Node completion time

### Business Metrics
- User retention (7-day, 30-day)
- Learning path completion rate
- Average exercises per node
- User satisfaction (feedback forms)

---

## 🤝 Contributing Guidelines

### Code Style
- **Python**: PEP 8, Black formatter, type hints
- **TypeScript**: Prettier, ESLint, strict mode
- **Commits**: Conventional Commits (feat:, fix:, docs:, etc.)

### Testing
- Backend: pytest with >80% coverage
- Frontend: Jest + React Testing Library
- E2E: Playwright for critical paths

### Pull Request Process
1. Create feature branch from `main`
2. Write descriptive commit messages
3. Add tests for new features
4. Update documentation
5. Request review from maintainers
6. Squash merge to main

---

## 📞 Support & Contact

### Documentation
- **README**: Quick start guide
- **API Docs**: http://localhost:8000/docs (FastAPI automatic docs)
- **Project Context**: This file

### Issues
- **Bug Reports**: GitHub Issues with label `bug`
- **Feature Requests**: GitHub Issues with label `enhancement`
- **Questions**: GitHub Discussions

---

## 📜 License

**Project**: MyTeacher AI
**License**: MIT (or specify your license)
**Copyright**: © 2025 Yohans Bekele

---

**Generated**: December 9, 2025
**AI Assistant**: Claude 3.5 Sonnet (Anthropic)
**Repository**: (Add your GitHub repo URL)

---

🎓 **MyTeacher AI - Learning, Personalized by AI** 🚀
