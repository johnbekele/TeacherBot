# Engineering Project Documentation

## MyTeacher: AI-Powered Adaptive Learning Platform

---

**Course:** Engineering Project
**Student Name:** Yohans Bekele
**Project Title:** MyTeacher - Hyper-Personalized AI Learning Platform for DevOps
**Date:** January 2025

---

## Table of Contents

1. [Executive Summary](#1-executive-summary)
2. [Project Concept](#2-project-concept)
   - 2.1 Problem Statement
   - 2.2 Needs Analysis
   - 2.3 User Requirements
   - 2.4 Functional Specification
   - 2.5 Technical Specification
3. [System Design](#3-system-design)
   - 3.1 Technology Selection
   - 3.2 System Architecture
   - 3.3 Database Design
   - 3.4 API Design
   - 3.5 User Interface Design
4. [Implementation](#4-implementation)
   - 4.1 Backend Development
   - 4.2 Frontend Development
   - 4.3 AI Integration
   - 4.4 Database Implementation
   - 4.5 Authentication & Security
5. [Testing](#5-testing)
   - 5.1 Unit Testing
   - 5.2 Integration Testing
   - 5.3 System Testing
   - 5.4 User Acceptance Testing
6. [Technical Documentation](#6-technical-documentation)
   - 6.1 Source Code Documentation
   - 6.2 User Manual
   - 6.3 Administrator Manual
   - 6.4 Deployment Guide
7. [Conclusion](#7-conclusion)
8. [References](#8-references)
9. [Appendices](#9-appendices)

---

## 1. Executive Summary

**MyTeacher** is an innovative AI-powered learning platform designed to revolutionize how individuals learn DevOps technologies. The platform leverages advanced artificial intelligence through Claude API (Anthropic) to provide hyper-personalized, adaptive learning experiences with special consideration for ADHD-friendly features.

### Key Achievements:
- Developed a full-stack web application with Next.js 14 and FastAPI
- Integrated Claude AI for intelligent tutoring and content generation
- Implemented adaptive learning algorithms that respond to user behavior
- Created a comprehensive exercise system with auto-grading capabilities
- Designed an ADHD-friendly interface with focus mode and break reminders
- Built a scalable architecture using MongoDB and Redis

### Technical Stack:
- **Frontend:** Next.js 14, React 18, TypeScript, TailwindCSS
- **Backend:** FastAPI (Python 3.11+), MongoDB, Redis
- **AI:** Claude API (Anthropic) with tool calling support
- **Infrastructure:** Docker, Docker Compose

---

## 2. Project Concept

### 2.1 Problem Statement

The traditional e-learning landscape faces several critical challenges:

1. **One-Size-Fits-All Approach:** Most learning platforms deliver identical content to all users, ignoring individual learning styles, pace, and background knowledge.

2. **Lack of Personalization:** Students with different experience levels receive the same content, leading to boredom for advanced learners and frustration for beginners.

3. **Limited Adaptability:** Static curricula fail to adapt to student struggles, often leaving learners stuck without appropriate support.

4. **ADHD Accessibility Gap:** Learners with ADHD face significant challenges with traditional platforms that don't account for attention management needs.

5. **Delayed Feedback:** Traditional assessment methods provide feedback too late to be actionable for learning improvement.

### 2.2 Needs Analysis

#### Target Users:
- Software developers transitioning to DevOps roles
- IT professionals seeking to upskill
- Students learning infrastructure technologies
- Individuals with ADHD requiring adaptive learning environments

#### User Needs Identified:

| Need Category | Specific Requirements |
|---------------|----------------------|
| **Personalization** | Content adapted to skill level, learning style, and goals |
| **Interactivity** | Hands-on exercises with real-time feedback |
| **Accessibility** | ADHD-friendly features, focus mode, break reminders |
| **Progress Tracking** | Visual progress indicators, achievement tracking |
| **Flexibility** | Self-paced learning, mobile-responsive design |
| **Support** | AI tutor available 24/7 for questions and guidance |

### 2.3 User Requirements

#### Functional Requirements:

**FR1 - User Management**
- Users shall be able to register and create accounts
- Users shall be able to login securely with JWT authentication
- Users shall be able to manage their profiles and settings

**FR2 - Learning Path Management**
- System shall provide pre-defined learning paths
- Users shall be able to create custom learning paths via AI
- System shall track progress across learning paths

**FR3 - Content Delivery**
- System shall deliver personalized learning content
- Content shall include lectures, code examples, and exercises
- System shall support multiple programming languages (Python, Bash, Terraform, etc.)

**FR4 - AI Tutoring**
- System shall provide AI-powered Q&A assistance
- AI shall generate personalized hints without revealing solutions
- AI shall create dynamic exercises based on user progress

**FR5 - Exercise System**
- Users shall be able to submit code solutions
- System shall auto-grade submissions with test cases
- System shall provide progressive hints

**FR6 - Progress Tracking**
- System shall track completion status of all modules
- System shall maintain streak tracking and engagement metrics
- System shall identify and record user struggle patterns

#### Non-Functional Requirements:

| Requirement | Specification |
|-------------|---------------|
| **Performance** | Page load < 3 seconds, API response < 500ms |
| **Scalability** | Support 1000+ concurrent users |
| **Availability** | 99.5% uptime target |
| **Security** | JWT authentication, password hashing, CORS protection |
| **Usability** | WCAG 2.1 AA compliance, mobile responsive |

### 2.4 Functional Specification

#### Use Case Diagram

```
                    ┌─────────────────────────────────────┐
                    │           MyTeacher System          │
                    │                                     │
    ┌───────┐       │  ┌──────────────────────────────┐  │
    │       │       │  │     User Authentication      │  │
    │       │───────┼─>│  - Register                  │  │
    │       │       │  │  - Login                     │  │
    │       │       │  │  - Manage Profile            │  │
    │       │       │  └──────────────────────────────┘  │
    │       │       │                                     │
    │ User  │       │  ┌──────────────────────────────┐  │
    │       │───────┼─>│     Learning Management      │  │
    │       │       │  │  - Browse Learning Paths     │  │
    │       │       │  │  - Study Modules             │  │
    │       │       │  │  - Complete Exercises        │  │
    │       │       │  └──────────────────────────────┘  │
    │       │       │                                     │
    │       │       │  ┌──────────────────────────────┐  │
    │       │───────┼─>│       AI Interaction         │  │
    │       │       │  │  - Ask Questions             │  │
    │       │       │  │  - Get Hints                 │  │
    │       │       │  │  - Create Learning Plans     │  │
    └───────┘       │  └──────────────────────────────┘  │
                    │                                     │
                    │  ┌──────────────────────────────┐  │
    ┌───────┐       │  │      AI Agent System         │  │
    │Claude │<──────┼──│  - Tutor Agent               │  │
    │  API  │       │  │  - Learning Orchestrator     │  │
    └───────┘       │  │  - Hint Agent                │  │
                    │  └──────────────────────────────┘  │
                    └─────────────────────────────────────┘
```

### 2.5 Technical Specification

#### Technology Requirements:

| Component | Technology | Justification |
|-----------|------------|---------------|
| **Frontend Framework** | Next.js 14 | Server-side rendering, React ecosystem, excellent DX |
| **Backend Framework** | FastAPI | Async support, automatic OpenAPI docs, Python ecosystem |
| **Database** | MongoDB | Flexible schema for varied content types |
| **Cache** | Redis | Session management, API response caching |
| **AI Integration** | Claude API | Advanced reasoning, tool calling, safety features |
| **Styling** | TailwindCSS | Utility-first, rapid development, customizable |
| **State Management** | Zustand | Lightweight, TypeScript support, simple API |

---

## 3. System Design

### 3.1 Technology Selection

#### Frontend Technologies

```
┌────────────────────────────────────────────────────────┐
│                    FRONTEND STACK                       │
├────────────────────────────────────────────────────────┤
│  Framework:     Next.js 14.1.0                         │
│  Runtime:       React 18.2.0                           │
│  Language:      TypeScript 5                           │
│  Styling:       TailwindCSS 3.4.1                      │
│  State:         Zustand 4.5.0                          │
│  UI Library:    Radix UI (Accessible components)       │
│  Code Editor:   Monaco Editor 4.6.0                    │
│  Animations:    Framer Motion 12.23.26                 │
│  HTTP Client:   Axios 1.6.5                            │
│  Icons:         Lucide React 0.556.0                   │
│  Markdown:      React Markdown 9.0.1                   │
└────────────────────────────────────────────────────────┘
```

#### Backend Technologies

```
┌────────────────────────────────────────────────────────┐
│                    BACKEND STACK                        │
├────────────────────────────────────────────────────────┤
│  Framework:     FastAPI 0.109.0                        │
│  Server:        Uvicorn 0.27.0 (ASGI)                  │
│  Database:      MongoDB 7.0 (Motor 3.3.2 async driver) │
│  Cache:         Redis 7 (redis-py 5.0.1)              │
│  AI:            Anthropic Claude API 0.39.0            │
│  Auth:          python-jose 3.3.0 (JWT)               │
│  Validation:    Pydantic 2.5.3                         │
│  Testing:       Pytest 7.4.3                           │
└────────────────────────────────────────────────────────┘
```

### 3.2 System Architecture

#### High-Level Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────────┐
│                              CLIENT LAYER                                │
│  ┌─────────────────────────────────────────────────────────────────┐    │
│  │                     Next.js Frontend (Port 3000)                │    │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────────┐ │    │
│  │  │   Pages     │  │ Components  │  │     State (Zustand)     │ │    │
│  │  │ - Dashboard │  │ - Chat UI   │  │ - authStore             │ │    │
│  │  │ - Learning  │  │ - Exercise  │  │ - chatStore             │ │    │
│  │  │ - Exercises │  │ - Progress  │  │ - exerciseStore         │ │    │
│  │  │ - Profile   │  │ - Layout    │  │ - nodeStore             │ │    │
│  │  └─────────────┘  └─────────────┘  └─────────────────────────┘ │    │
│  └─────────────────────────────────────────────────────────────────┘    │
└───────────────────────────────────┬─────────────────────────────────────┘
                                    │ HTTPS/REST API
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                              API LAYER                                   │
│  ┌─────────────────────────────────────────────────────────────────┐    │
│  │                  FastAPI Backend (Port 8000)                    │    │
│  │  ┌────────────────────────────────────────────────────────────┐ │    │
│  │  │                    API Endpoints (/v1)                     │ │    │
│  │  │  /auth    /chat    /nodes    /exercises    /progress       │ │    │
│  │  │  /learning-paths   /course-content   /onboarding           │ │    │
│  │  └────────────────────────────────────────────────────────────┘ │    │
│  │  ┌────────────────────────────────────────────────────────────┐ │    │
│  │  │                    Business Logic                          │ │    │
│  │  │  - Authentication Service   - Progress Tracking            │ │    │
│  │  │  - Chat Service             - Content Generation           │ │    │
│  │  │  - Exercise Grading         - Learning Path Management     │ │    │
│  │  └────────────────────────────────────────────────────────────┘ │    │
│  │  ┌────────────────────────────────────────────────────────────┐ │    │
│  │  │                      AI Agent Layer                        │ │    │
│  │  │  ┌──────────────┐ ┌──────────────┐ ┌────────────────────┐ │ │    │
│  │  │  │ Tutor Agent  │ │  Hint Agent  │ │Learning Orchestrator│ │ │    │
│  │  │  └──────┬───────┘ └──────┬───────┘ └─────────┬──────────┘ │ │    │
│  │  │         └────────────────┴───────────────────┘            │ │    │
│  │  │                          │                                 │ │    │
│  │  │         ┌────────────────▼───────────────────┐            │ │    │
│  │  │         │       Tool Registry & Handlers     │            │ │    │
│  │  │         └────────────────────────────────────┘            │ │    │
│  │  └────────────────────────────────────────────────────────────┘ │    │
│  └─────────────────────────────────────────────────────────────────┘    │
└───────────────────────────────────┬─────────────────────────────────────┘
                                    │
        ┌───────────────────────────┼───────────────────────────┐
        │                           │                           │
        ▼                           ▼                           ▼
┌───────────────┐          ┌───────────────┐          ┌───────────────┐
│   MongoDB     │          │    Redis      │          │  Claude API   │
│  (Port 27017) │          │  (Port 6379)  │          │  (External)   │
│               │          │               │          │               │
│ - users       │          │ - sessions    │          │ - chat        │
│ - nodes       │          │ - cache       │          │ - tools       │
│ - exercises   │          │ - rate limit  │          │ - generation  │
│ - progress    │          │               │          │               │
│ - chat_msgs   │          │               │          │               │
└───────────────┘          └───────────────┘          └───────────────┘
```

#### Component Interaction Flow

```
User Action: "I want to learn Docker"
                    │
                    ▼
┌──────────────────────────────────┐
│       Frontend (Next.js)         │
│  ChatPanel captures message      │
│  Sends POST /v1/chat/message     │
└────────────────┬─────────────────┘
                 │
                 ▼
┌──────────────────────────────────┐
│       Backend (FastAPI)          │
│  1. Validate JWT token           │
│  2. Route to chat service        │
│  3. Determine context (planning) │
└────────────────┬─────────────────┘
                 │
                 ▼
┌──────────────────────────────────┐
│       AI Agent System            │
│  1. Select LearningOrchestrator  │
│  2. Build system prompt          │
│  3. Include user context         │
└────────────────┬─────────────────┘
                 │
                 ▼
┌──────────────────────────────────┐
│        Claude API Call           │
│  - System prompt + tools         │
│  - User message                  │
│  - Conversation history          │
└────────────────┬─────────────────┘
                 │
                 ▼
┌──────────────────────────────────┐
│       Tool Execution Loop        │
│  Claude returns: tool_use        │
│  Execute: create_learning_path   │
│  Return results to Claude        │
│  Claude returns: end_turn        │
└────────────────┬─────────────────┘
                 │
                 ▼
┌──────────────────────────────────┐
│       Response Processing        │
│  1. Extract text response        │
│  2. Save to chat_messages        │
│  3. Return to frontend           │
└────────────────┬─────────────────┘
                 │
                 ▼
┌──────────────────────────────────┐
│       Frontend Update            │
│  1. Update Zustand store         │
│  2. Render AI response           │
│  3. Display new learning path    │
└──────────────────────────────────┘
```

### 3.3 Database Design

#### Entity Relationship Diagram

```
┌─────────────────┐       ┌─────────────────┐       ┌─────────────────┐
│     users       │       │  user_profiles  │       │  user_context   │
├─────────────────┤       ├─────────────────┤       ├─────────────────┤
│ _id (PK)        │──1:1──│ user_id (FK)    │──1:1──│ user_id (FK)    │
│ email (unique)  │       │ experience_level│       │ education       │
│ full_name       │       │ learning_goals  │       │ work            │
│ password_hash   │       │ weak_points     │       │ learning        │
│ settings        │       │ strengths       │       │ career_goals    │
│ created_at      │       │ recent_struggles│       │ personal        │
└────────┬────────┘       └─────────────────┘       └─────────────────┘
         │
         │ 1:N
         ▼
┌─────────────────┐       ┌─────────────────┐       ┌─────────────────┐
│ learning_paths  │       │  user_progress  │       │  chat_sessions  │
├─────────────────┤       ├─────────────────┤       ├─────────────────┤
│ _id (PK)        │       │ _id (PK)        │       │ _id (PK)        │
│ user_id (FK)    │       │ user_id (FK)    │       │ user_id (FK)    │
│ path_id (unique)│       │ current_node_id │       │ context_type    │
│ title           │       │ completed_nodes │       │ context_id      │
│ description     │       │ node_progress   │       │ is_active       │
│ nodes[]         │       │ overall_stats   │       │ created_at      │
└────────┬────────┘       └─────────────────┘       └────────┬────────┘
         │                                                    │
         │ N:M                                               │ 1:N
         ▼                                                    ▼
┌─────────────────┐       ┌─────────────────┐       ┌─────────────────┐
│ learning_nodes  │───1:N─│    exercises    │       │  chat_messages  │
├─────────────────┤       ├─────────────────┤       ├─────────────────┤
│ _id (PK)        │       │ _id (PK)        │       │ _id (PK)        │
│ node_id (unique)│       │ exercise_id     │       │ session_id (FK) │
│ title           │       │ node_id (FK)    │       │ role            │
│ description     │       │ title           │       │ content         │
│ category        │       │ type            │       │ created_at      │
│ difficulty      │       │ prompt          │       └─────────────────┘
│ prerequisites[] │       │ test_cases[]    │
│ content         │       │ hints[]         │
└─────────────────┘       └────────┬────────┘
                                   │
                                   │ 1:N
                                   ▼
                          ┌─────────────────┐
                          │exercise_attempts│
                          ├─────────────────┤
                          │ _id (PK)        │
                          │ user_id (FK)    │
                          │ exercise_id (FK)│
                          │ submitted_code  │
                          │ test_results[]  │
                          │ score           │
                          │ feedback        │
                          └─────────────────┘
```

#### Collection Schemas

**users Collection:**
```javascript
{
  _id: ObjectId,
  email: String (indexed, unique),
  full_name: String,
  password_hash: String,
  created_at: DateTime,
  last_login: DateTime,
  onboarding_completed: Boolean,
  settings: {
    focus_mode: Boolean,
    break_reminders: Boolean,
    pace_preference: "slow" | "medium" | "fast",
    adhd_mode: Boolean
  }
}
```

**learning_nodes Collection:**
```javascript
{
  _id: ObjectId,
  node_id: String (indexed, unique),
  title: String,
  description: String,
  category: String,
  difficulty: "beginner" | "intermediate" | "advanced",
  estimated_duration: Number,
  prerequisites: [String],
  skills_taught: [String],
  content: {
    introduction: String,
    concepts: [String],
    practical_applications: [String]
  }
}
```

**exercises Collection:**
```javascript
{
  _id: ObjectId,
  exercise_id: String (indexed, unique),
  node_id: String (indexed),
  title: String,
  type: "python" | "bash" | "terraform" | "pulumi" | "ansible",
  prompt: String,
  starter_code: String,
  solution: String,
  hints: [{
    hint_number: Number,
    text: String,
    reveal_after_attempts: Number
  }],
  test_cases: [{
    test_id: String,
    input: Object,
    expected_output: Object
  }]
}
```

### 3.4 API Design

#### RESTful API Endpoints

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| **Authentication** ||||
| POST | `/v1/auth/register` | Register new user | No |
| POST | `/v1/auth/login` | Login and get JWT | No |
| GET | `/v1/auth/me` | Get current user | Yes |
| PUT | `/v1/auth/profile` | Update profile | Yes |
| **Chat** ||||
| POST | `/v1/chat/message` | Send message to AI | Yes |
| GET | `/v1/chat/history/{session_id}` | Get chat history | Yes |
| GET | `/v1/chat/sessions` | Get all sessions | Yes |
| **Learning** ||||
| GET | `/v1/nodes` | Get all nodes | Yes |
| GET | `/v1/nodes/{node_id}` | Get node details | Yes |
| GET | `/v1/learning-paths` | Get learning paths | Yes |
| GET | `/v1/learning-paths/{path_id}` | Get path details | Yes |
| **Exercises** ||||
| GET | `/v1/exercises/{exercise_id}` | Get exercise | Yes |
| POST | `/v1/exercises/{exercise_id}/submit` | Submit solution | Yes |
| **Progress** ||||
| GET | `/v1/progress` | Get user progress | Yes |
| GET | `/v1/progress/stats` | Get detailed stats | Yes |

#### API Request/Response Examples

**Login Request:**
```json
POST /v1/auth/login
Content-Type: application/x-www-form-urlencoded

username=user@example.com&password=securepassword
```

**Login Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

**Chat Message Request:**
```json
POST /v1/chat/message
Authorization: Bearer <token>
Content-Type: application/json

{
  "message": "I want to learn Docker",
  "context_type": "planning",
  "context_id": "dashboard"
}
```

**Chat Message Response:**
```json
{
  "content": "Great choice! Docker is essential for modern DevOps...",
  "actions": [
    {
      "type": "navigate",
      "path_id": "docker-learning-path"
    }
  ],
  "session_id": "sess_abc123"
}
```

### 3.5 User Interface Design

#### Design Principles

1. **Clean & Minimal:** Reduce cognitive load with whitespace and clear hierarchy
2. **Consistent Theming:** CSS variables for seamless light/dark mode
3. **Responsive:** Mobile-first design with breakpoints at 640px, 768px, 1024px
4. **Accessible:** WCAG 2.1 AA compliance with Radix UI primitives
5. **ADHD-Friendly:** Focus mode, progress indicators, celebration animations

#### Key UI Components

```
┌─────────────────────────────────────────────────────────────────────────┐
│  ┌──────┐  MyTeacher AI                                    [Theme] [User]│
│  │ Logo │  ─────────────────────────────────────────────────────────────│
├──┴──────┴───────────────────────────────────────────────────────────────┤
│ ┌─────────┐                                                              │
│ │Dashboard│                                                              │
│ ├─────────┤  ┌─────────────────────────────────────────────────────────┐│
│ │Learning │  │                    MAIN CONTENT AREA                     ││
│ │         │  │                                                          ││
│ │ > Paths │  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐      ││
│ │ > Nodes │  │  │ Active      │  │ Progress    │  │ Completed   │      ││
│ ├─────────┤  │  │ Courses: 3  │  │ 45%         │  │ 12          │      ││
│ │Exercises│  │  └─────────────┘  └─────────────┘  └─────────────┘      ││
│ ├─────────┤  │                                                          ││
│ │Progress │  │  ┌─────────────────────────────────────────────────────┐││
│ ├─────────┤  │  │            AI Learning Assistant                    │││
│ │Settings │  │  │  Tell me what you want to learn...                  │││
│ └─────────┘  │  └─────────────────────────────────────────────────────┘││
│              └─────────────────────────────────────────────────────────┘│
└─────────────────────────────────────────────────────────────────────────┘
```

#### Learning View (Dual Panel)

```
┌─────────────────────────────────────────────────────────────────────────┐
│                              LEARNING VIEW                               │
├───────────────────────────────────┬─────────────────────────────────────┤
│         CONTENT PANEL (60%)       │         CHAT PANEL (40%)            │
│  ┌─────────────────────────────┐  │  ┌─────────────────────────────┐   │
│  │ Docker Fundamentals         │  │  │ AI Tutor                    │   │
│  │ ─────────────────────────── │  │  ├─────────────────────────────┤   │
│  │ Introduction                │  │  │ How can I help you today?   │   │
│  │                             │  │  │                             │   │
│  │ Docker is a platform for    │  │  │ User: What is a container?  │   │
│  │ developing, shipping, and   │  │  │                             │   │
│  │ running applications in     │  │  │ AI: A container is a        │   │
│  │ containers...               │  │  │ lightweight, standalone     │   │
│  │                             │  │  │ package that includes...    │   │
│  │ ```bash                     │  │  │                             │   │
│  │ docker run hello-world      │  │  │                             │   │
│  │ ```                         │  │  ├─────────────────────────────┤   │
│  │                             │  │  │ [Type your question...]  [>]│   │
│  └─────────────────────────────┘  │  └─────────────────────────────┘   │
│  [< Previous]     [3/10]  [Next >]│                                     │
└───────────────────────────────────┴─────────────────────────────────────┘
```

---

## 4. Implementation

### 4.1 Backend Development

#### Project Structure

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI application entry
│   ├── config.py            # Environment configuration
│   ├── dependencies.py      # Dependency injection
│   ├── api/
│   │   └── v1/
│   │       ├── auth.py      # Authentication endpoints
│   │       ├── chat.py      # Chat/AI endpoints
│   │       ├── exercises.py # Exercise management
│   │       ├── nodes.py     # Learning nodes
│   │       ├── progress.py  # Progress tracking
│   │       └── ...
│   ├── models/              # Pydantic models
│   ├── ai/                  # AI agent system
│   │   ├── chat_service.py
│   │   ├── tool_registry.py
│   │   ├── agents/
│   │   └── prompts/
│   ├── db/                  # Database layer
│   │   ├── mongodb.py
│   │   ├── redis.py
│   │   └── repositories/
│   └── utils/               # Utilities
├── tests/                   # Test files
├── requirements.txt
└── Dockerfile
```

#### Key Implementation: Chat Service

```python
# app/ai/chat_service.py
class ChatService:
    def __init__(self):
        self.client = anthropic.Anthropic(api_key=settings.ANTHROPIC_API_KEY)
        self.tool_registry = ToolRegistry()

    async def process_message(
        self,
        message: str,
        context_type: str,
        user_id: str,
        session_id: str
    ) -> ChatResponse:
        # 1. Get user profile for personalization
        user_profile = await self.get_user_profile(user_id)

        # 2. Build system prompt based on context
        system_prompt = self.build_system_prompt(context_type, user_profile)

        # 3. Get conversation history
        history = await self.get_chat_history(session_id)

        # 4. Call Claude API with tools
        response = self.client.messages.create(
            model="claude-3-haiku-20240307",
            max_tokens=4096,
            system=system_prompt,
            tools=self.tool_registry.get_tools(),
            messages=history + [{"role": "user", "content": message}]
        )

        # 5. Handle tool calls if any
        while response.stop_reason == "tool_use":
            tool_results = await self.execute_tools(response.content)
            response = self.client.messages.create(
                model="claude-3-haiku-20240307",
                max_tokens=4096,
                system=system_prompt,
                tools=self.tool_registry.get_tools(),
                messages=history + tool_results
            )

        # 6. Save and return response
        await self.save_message(session_id, "assistant", response.content)
        return ChatResponse(content=response.content[0].text)
```

#### Key Implementation: Authentication

```python
# app/api/v1/auth.py
@router.post("/login")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    # Verify credentials
    user = await users_collection.find_one({"email": form_data.username})
    if not user or not verify_password(form_data.password, user["password_hash"]):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    # Generate JWT token
    access_token = create_access_token(
        data={"user_id": str(user["_id"]), "email": user["email"]}
    )

    return {"access_token": access_token, "token_type": "bearer"}

# app/utils/security.py
def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
```

### 4.2 Frontend Development

#### Project Structure

```
frontend/src/
├── app/                      # Next.js 14 App Router
│   ├── layout.tsx           # Root layout with providers
│   ├── page.tsx             # Landing page
│   ├── dashboard/
│   │   └── page.tsx         # Dashboard page
│   ├── login/
│   │   └── page.tsx         # Login page
│   ├── learn/
│   │   └── [nodeId]/
│   │       └── page.tsx     # Learning view
│   └── ...
├── components/
│   ├── ui/                  # Reusable UI components
│   │   ├── button.tsx
│   │   ├── card.tsx
│   │   ├── input.tsx
│   │   └── ...
│   ├── chat/                # Chat components
│   │   ├── ChatPanel.tsx
│   │   └── FloatingChat.tsx
│   ├── layout/              # Layout components
│   │   ├── AppLayout.tsx
│   │   └── AppSidebar.tsx
│   └── ...
├── stores/                  # Zustand state stores
│   ├── authStore.ts
│   ├── chatStore.ts
│   └── ...
├── lib/
│   ├── api.ts              # API client
│   └── utils.ts            # Utility functions
└── styles/
    └── globals.css         # Global styles with CSS variables
```

#### Key Implementation: State Management

```typescript
// stores/chatStore.ts
import { create } from 'zustand';

interface ChatState {
  messages: ChatMessage[];
  isLoading: boolean;
  error: string | null;
  sendMessage: (message: string, contextType: string, contextId: string) => Promise<void>;
  clearChat: () => void;
}

export const useChatStore = create<ChatState>((set, get) => ({
  messages: [],
  isLoading: false,
  error: null,

  sendMessage: async (message, contextType, contextId) => {
    set({ isLoading: true, error: null });

    // Add user message immediately
    const userMessage: ChatMessage = {
      role: 'user',
      content: message,
      timestamp: new Date().toISOString()
    };
    set(state => ({ messages: [...state.messages, userMessage] }));

    try {
      const response = await api.sendChatMessage(message, contextType, contextId);

      // Add AI response
      const aiMessage: ChatMessage = {
        role: 'assistant',
        content: response.content,
        timestamp: new Date().toISOString()
      };
      set(state => ({ messages: [...state.messages, aiMessage], isLoading: false }));
    } catch (error) {
      set({ error: 'Failed to send message', isLoading: false });
    }
  },

  clearChat: () => set({ messages: [], error: null })
}));
```

#### Key Implementation: Theme System

```css
/* styles/globals.css */
:root {
  /* Light Mode Colors */
  --background: 0 0% 99%;
  --foreground: 224 71% 4%;
  --card: 0 0% 100%;
  --card-foreground: 224 71% 4%;
  --primary: 221 83% 53%;
  --primary-foreground: 210 40% 98%;
  --muted: 220 14% 96%;
  --muted-foreground: 220 9% 46%;
  --border: 220 13% 91%;
  --radius: 0.625rem;
}

.dark {
  /* Dark Mode Colors */
  --background: 224 71% 4%;
  --foreground: 213 31% 91%;
  --card: 224 71% 6%;
  --card-foreground: 213 31% 91%;
  --primary: 217 91% 60%;
  --primary-foreground: 222 47% 11%;
  --muted: 215 28% 17%;
  --muted-foreground: 215 20% 65%;
  --border: 215 28% 17%;
}
```

### 4.3 AI Integration

#### Tool Calling System

```python
# app/ai/tool_registry.py
class ToolRegistry:
    def get_tools(self) -> list:
        return [
            {
                "name": "create_learning_path",
                "description": "Create a new learning path for the user",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "title": {"type": "string"},
                        "description": {"type": "string"},
                        "category": {"type": "string"},
                        "nodes": {
                            "type": "array",
                            "items": {"type": "string"}
                        }
                    },
                    "required": ["title", "description", "category", "nodes"]
                }
            },
            {
                "name": "generate_exercise",
                "description": "Generate a practice exercise",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "topic": {"type": "string"},
                        "difficulty": {"type": "string"},
                        "type": {"type": "string"}
                    },
                    "required": ["topic", "difficulty", "type"]
                }
            },
            # ... more tools
        ]

# app/ai/tool_handlers.py
class ToolHandlers:
    async def execute_tool(self, tool_name: str, tool_input: dict, user_id: str):
        if tool_name == "create_learning_path":
            return await self.create_learning_path(tool_input, user_id)
        elif tool_name == "generate_exercise":
            return await self.generate_exercise(tool_input, user_id)
        # ... more handlers
```

### 4.4 Database Implementation

#### MongoDB Connection

```python
# app/db/mongodb.py
from motor.motor_asyncio import AsyncIOMotorClient

class MongoDB:
    client: AsyncIOMotorClient = None
    db = None

    @classmethod
    async def connect(cls):
        cls.client = AsyncIOMotorClient(settings.MONGODB_URL)
        cls.db = cls.client[settings.MONGODB_DB_NAME]

        # Create indexes
        await cls.db.users.create_index("email", unique=True)
        await cls.db.learning_nodes.create_index("node_id", unique=True)
        await cls.db.chat_sessions.create_index([("user_id", 1), ("is_active", 1)])

    @classmethod
    async def disconnect(cls):
        if cls.client:
            cls.client.close()

# Collections
users_collection = MongoDB.db.users
nodes_collection = MongoDB.db.learning_nodes
exercises_collection = MongoDB.db.exercises
```

### 4.5 Authentication & Security

#### Security Implementation

| Feature | Implementation |
|---------|----------------|
| Password Hashing | bcrypt with auto-generated salt |
| JWT Tokens | HS256 algorithm, 24-hour expiry |
| CORS | Restricted to localhost:3000, 3001 |
| Input Validation | Pydantic models with constraints |
| Rate Limiting | Redis-based per-user limits |

```python
# Security Configuration
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)
```

---

## 5. Testing

### 5.1 Unit Testing

#### Test Coverage

| Module | Tests | Coverage |
|--------|-------|----------|
| Authentication | 8 | 95% |
| Chat Service | 12 | 88% |
| Exercise Grading | 10 | 92% |
| Progress Tracking | 6 | 85% |

#### Example Unit Tests

```python
# tests/test_auth.py
import pytest
from app.utils.security import create_access_token, verify_password, get_password_hash

class TestAuthentication:
    def test_password_hashing(self):
        password = "securepassword123"
        hashed = get_password_hash(password)

        assert hashed != password
        assert verify_password(password, hashed)
        assert not verify_password("wrongpassword", hashed)

    def test_jwt_token_creation(self):
        data = {"user_id": "123", "email": "test@example.com"}
        token = create_access_token(data)

        assert token is not None
        assert len(token) > 0

# tests/test_exercises.py
class TestExerciseGrading:
    @pytest.mark.asyncio
    async def test_correct_solution_scores_100(self):
        exercise = await get_exercise("python-hello-world")
        result = await grade_submission(
            exercise_id=exercise.id,
            code="print('Hello, World!')"
        )

        assert result.score == 100
        assert all(tc.passed for tc in result.test_results)
```

### 5.2 Integration Testing

#### API Integration Tests

```python
# tests/test_api_integration.py
import pytest
from httpx import AsyncClient
from app.main import app

@pytest.mark.asyncio
async def test_full_learning_flow():
    async with AsyncClient(app=app, base_url="http://test") as client:
        # 1. Register user
        response = await client.post("/v1/auth/register", json={
            "email": "test@example.com",
            "password": "testpass123",
            "full_name": "Test User"
        })
        assert response.status_code == 201

        # 2. Login
        response = await client.post("/v1/auth/login", data={
            "username": "test@example.com",
            "password": "testpass123"
        })
        assert response.status_code == 200
        token = response.json()["access_token"]

        # 3. Start learning session
        headers = {"Authorization": f"Bearer {token}"}
        response = await client.post("/v1/chat/message",
            headers=headers,
            json={
                "message": "I want to learn Python",
                "context_type": "planning"
            }
        )
        assert response.status_code == 200
        assert "Python" in response.json()["content"]
```

### 5.3 System Testing

#### Performance Testing Results

| Test Scenario | Metric | Result | Target |
|---------------|--------|--------|--------|
| Page Load (Dashboard) | Time to First Byte | 180ms | <500ms |
| API Response (Chat) | Response Time | 320ms | <1000ms |
| Concurrent Users | Max Supported | 150 | 100 |
| Database Query | Average Time | 45ms | <100ms |

### 5.4 User Acceptance Testing

#### Test Scenarios

| Scenario | Steps | Expected Result | Status |
|----------|-------|-----------------|--------|
| New User Registration | 1. Visit /register<br>2. Fill form<br>3. Submit | Account created, redirected to onboarding | PASS |
| Learning Path Creation | 1. Open chat<br>2. Request Docker path<br>3. View path | AI creates path, displays modules | PASS |
| Exercise Completion | 1. Open exercise<br>2. Write code<br>3. Submit | Code graded, feedback provided | PASS |
| Dark Mode Toggle | 1. Click theme toggle | UI switches theme smoothly | PASS |

---

## 6. Technical Documentation

### 6.1 Source Code Documentation

#### Code Documentation Standards

All source code follows these documentation standards:

**Python (Backend):**
```python
def create_learning_path(
    title: str,
    description: str,
    nodes: List[str],
    user_id: str
) -> LearningPath:
    """
    Create a new learning path for a user.

    Args:
        title: Display name for the learning path
        description: Brief description of what the path covers
        nodes: List of node IDs to include in the path
        user_id: ID of the user creating the path

    Returns:
        LearningPath: The created learning path object

    Raises:
        ValueError: If title is empty or nodes list is empty
        NotFoundError: If any node_id doesn't exist
    """
```

**TypeScript (Frontend):**
```typescript
/**
 * Custom hook for managing chat state and interactions
 *
 * @returns Object containing chat state and actions
 * @example
 * const { messages, sendMessage, isLoading } = useChatStore();
 */
```

### 6.2 User Manual

#### Getting Started

1. **Registration**
   - Navigate to the registration page
   - Enter your email, full name, and password
   - Complete the onboarding questionnaire

2. **Dashboard Overview**
   - View your active courses and progress
   - Access the AI assistant for learning guidance
   - Track your achievements and streaks

3. **Learning a Topic**
   - Browse available learning paths or ask AI for recommendations
   - Click on a learning path to view modules
   - Complete lectures and exercises in sequence

4. **Using the AI Tutor**
   - Click the chat icon to open the AI assistant
   - Ask questions about concepts you're learning
   - Request hints when stuck on exercises

5. **Completing Exercises**
   - Read the exercise prompt carefully
   - Write your code in the editor
   - Click "Submit" to grade your solution
   - Review feedback and try again if needed

### 6.3 Administrator Manual

#### System Requirements

| Component | Minimum | Recommended |
|-----------|---------|-------------|
| CPU | 2 cores | 4 cores |
| RAM | 4 GB | 8 GB |
| Storage | 20 GB | 50 GB |
| Node.js | 18.x | 20.x |
| Python | 3.11 | 3.12 |

#### Environment Setup

```bash
# Backend Environment Variables
APP_NAME=MyTeacher API
SECRET_KEY=<generate-secure-key>
MONGODB_URL=mongodb://localhost:27017
MONGODB_DB_NAME=myteacher
REDIS_URL=redis://localhost:6379
ANTHROPIC_API_KEY=<your-api-key>
```

#### Monitoring & Logs

- Application logs: `/var/log/myteacher/app.log`
- Access logs: `/var/log/myteacher/access.log`
- Error alerts: Configure in `settings.py`

### 6.4 Deployment Guide

#### Docker Deployment

```yaml
# docker-compose.yml
version: '3.8'

services:
  mongodb:
    image: mongo:7.0
    ports:
      - "27017:27017"
    volumes:
      - mongodb_data:/data/db

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"

  backend:
    build: ./backend
    ports:
      - "8000:8000"
    environment:
      - MONGODB_URL=mongodb://mongodb:27017
      - REDIS_URL=redis://redis:6379
    depends_on:
      - mongodb
      - redis

  frontend:
    build: ./frontend
    ports:
      - "3000:3000"
    depends_on:
      - backend

volumes:
  mongodb_data:
```

#### Deployment Commands

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down

# Rebuild after changes
docker-compose build --no-cache
docker-compose up -d
```

---

## 7. Conclusion

### Project Achievements

The MyTeacher project successfully delivers an AI-powered adaptive learning platform that addresses the identified business problems:

1. **Personalization:** The platform adapts to individual learning styles through comprehensive user profiling and AI-driven content customization.

2. **Interactivity:** Real-time AI tutoring, interactive exercises, and immediate feedback create an engaging learning experience.

3. **Accessibility:** ADHD-friendly features including focus mode, break reminders, and step-by-step guidance make learning accessible to diverse users.

4. **Scalability:** The microservices architecture with MongoDB and Redis supports horizontal scaling for growing user bases.

5. **Modern Technology Stack:** Implementation using Next.js 14, FastAPI, and Claude API demonstrates proficiency in current industry-standard technologies.

### Future Enhancements

1. **Mobile Application:** Native iOS/Android apps using React Native
2. **Collaborative Learning:** Group study sessions and peer programming
3. **Advanced Analytics:** Learning analytics dashboard for instructors
4. **Content Marketplace:** User-generated learning paths and exercises
5. **Certification System:** Verified completion certificates

### Lessons Learned

- **AI Integration Complexity:** Tool calling with Claude API requires careful prompt engineering
- **State Management:** Zustand provides simpler state management than Redux for this use case
- **Type Safety:** TypeScript significantly reduces runtime errors in complex applications
- **Dark Mode:** CSS variables enable seamless theme switching without JavaScript overhead

---

## 8. References

1. Anthropic. (2024). Claude API Documentation. https://docs.anthropic.com
2. Next.js Documentation. (2024). https://nextjs.org/docs
3. FastAPI Documentation. (2024). https://fastapi.tiangolo.com
4. MongoDB Manual. (2024). https://docs.mongodb.com/manual
5. Tailwind CSS Documentation. (2024). https://tailwindcss.com/docs
6. Radix UI Primitives. (2024). https://radix-ui.com/primitives
7. Zustand State Management. (2024). https://github.com/pmndrs/zustand

---

## 9. Appendices

### Appendix A: API Endpoint Reference

Complete list of all 25+ API endpoints with request/response schemas.

### Appendix B: Database Schema Details

Full MongoDB collection schemas with indexes and constraints.

### Appendix C: Component Library

Catalog of 66+ React components with usage examples.

### Appendix D: Test Reports

Detailed test execution reports and coverage analysis.

---

**Document Version:** 1.0
**Last Updated:** January 2025
**Author:** Yohans Bekele

---

*This document was prepared as part of the Engineering Project course requirements.*
