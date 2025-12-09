# MyTeacher - AI DevOps Mentor Implementation Plan

## Executive Summary
This document provides a complete engineering plan for building a hyper-personalized AI-powered DevOps learning platform designed for ADHD-friendly, step-by-step learning with persistent memory and adaptive teaching strategies.

---

## 1. High-Level System Architecture

### System Components Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                         CLIENT LAYER                             │
│  ┌────────────────────┐              ┌─────────────────────┐   │
│  │   Learning Pad     │              │   AI Chat Panel     │   │
│  │  (Left Panel)      │              │   (Right Panel)     │   │
│  │  - Content         │              │   - Conversation    │   │
│  │  - Code Editor     │              │   - Instructions    │   │
│  │  - Exercise        │              │   - Hints           │   │
│  │  - Results         │              │   - Feedback        │   │
│  └────────────────────┘              └─────────────────────┘   │
│           Next.js + React + TailwindCSS + Monaco                │
└─────────────────────────────────────────────────────────────────┘
                                 │
                            HTTPS/REST API
                                 │
┌─────────────────────────────────────────────────────────────────┐
│                        BACKEND LAYER (FastAPI)                   │
│  ┌──────────────┬──────────────┬──────────────┬─────────────┐  │
│  │ Auth Service │ Node/Curric  │Exercise Svc  │ Chat Router │  │
│  │              │ Service      │              │             │  │
│  └──────────────┴──────────────┴──────────────┴─────────────┘  │
│  ┌──────────────┬──────────────┬──────────────┬─────────────┐  │
│  │Memory Service│Grading Svc   │Progress Svc  │ Sandbox Mgr │  │
│  │              │              │              │             │  │
│  └──────────────┴──────────────┴──────────────┴─────────────┘  │
└─────────────────────────────────────────────────────────────────┘
                    │                           │
        ┌───────────┴────────┐         ┌───────┴────────┐
        │                    │         │                │
┌───────▼────────┐  ┌────────▼──────┐ │  ┌─────────────▼────────┐
│   MongoDB      │  │  Redis Queue  │ │  │   Docker Sandbox     │
│   - Users      │  │  - Jobs       │ │  │   - Python Runner    │
│   - Nodes      │  │  - Sessions   │ │  │   - Bash Runner      │
│   - Exercises  │  │               │ │  │   - Terraform Runner │
│   - Memory     │  └───────────────┘ │  │   - Pulumi Runner    │
│   - Progress   │                    │  └──────────────────────┘
└────────────────┘                    │
                                      │
┌─────────────────────────────────────▼────────────────────────┐
│                     AI ORCHESTRATION LAYER                    │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │              Claude API (Anthropic)                      │ │
│  │  ┌─────────────┬─────────────┬──────────────────────┐  │ │
│  │  │ Teaching    │ Exercise    │  Memory & Dialogue   │  │ │
│  │  │ Strategy    │ Generation  │  Agents              │  │ │
│  │  │ Agent       │ & Grading   │                      │  │ │
│  │  └─────────────┴─────────────┴──────────────────────┘  │ │
│  └─────────────────────────────────────────────────────────┘ │
│                                                               │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │           Vector Memory Store (Pinecone/Weaviate)       │ │
│  │  - User confusion patterns                               │ │
│  │  - Learning history embeddings                           │ │
│  │  - Strength/weakness vectors                             │ │
│  └─────────────────────────────────────────────────────────┘ │
└───────────────────────────────────────────────────────────────┘
```

### Layer Responsibilities

#### Frontend Layer
- Rendering dual-pane interface
- Managing client-side state (editor content, UI modals, focus mode)
- API communication with backend
- No business logic - purely presentational

#### Backend Layer
- REST API endpoints
- Authentication & session management
- Database operations
- Job queue management (Redis)
- Sandbox orchestration
- AI agent communication proxy

#### AI Orchestration Layer
- Teaching strategy decisions
- Exercise generation
- Auto-grading logic
- Memory retrieval and storage
- Adaptive curriculum planning
- Emotional context processing (ADHD patterns, frustration detection)

#### Infrastructure Layer
- MongoDB: Long-term storage
- Redis: Job queues, caching, session store
- Docker Sandboxes: Isolated code execution
- Vector DB: Semantic memory storage

---

## 2. Database Schema (MongoDB)

### Collection: `users`
```javascript
{
  _id: ObjectId,
  email: String (unique, indexed),
  password_hash: String,
  full_name: String,
  created_at: DateTime,
  last_login: DateTime,
  onboarding_completed: Boolean,
  settings: {
    focus_mode: Boolean,
    break_reminders: Boolean,
    pace_preference: String, // "slow", "medium", "fast"
    adhd_mode: Boolean
  }
}
```

### Collection: `onboarding_profiles`
```javascript
{
  _id: ObjectId,
  user_id: ObjectId (indexed),
  learning_style: {
    overthinking: Number (1-5),
    adhd: Boolean,
    detail_preference: String, // "simple", "detailed", "expert"
    rabbit_hole_tendency: Number (1-5)
  },
  goals: {
    primary: String, // "DevOps", "SRE", "Cloud", "Certification"
    certifications: [String],
    time_availability: String, // "1-2h/day", "3-5h/day", etc.
    motivation: String
  },
  weaknesses: [String],
  strengths: [String],
  created_at: DateTime
}
```

### Collection: `learning_nodes`
```javascript
{
  _id: ObjectId,
  node_id: String (unique, indexed), // e.g., "terraform-basics"
  title: String, // "Terraform Basics"
  description: String,
  category: String, // "terraform", "pulumi", "python", "bash", "ansible"
  difficulty: String, // "beginner", "intermediate", "advanced"
  estimated_duration: Number, // minutes
  prerequisites: [String], // array of node_ids
  skills_taught: [String],
  status: String, // "available", "locked", "deprecated"
  content: {
    introduction: String,
    concepts: [String],
    practical_applications: [String]
  },
  created_at: DateTime,
  updated_at: DateTime
}
```

### Collection: `exercises`
```javascript
{
  _id: ObjectId,
  exercise_id: String (unique, indexed),
  node_id: String (indexed),
  title: String,
  description: String,
  type: String, // "python", "bash", "terraform", "pulumi", "ansible"
  difficulty: String,
  prompt: String,
  starter_code: String,
  solution: String,
  hints: [
    {
      hint_number: Number,
      text: String,
      reveal_after_attempts: Number
    }
  ],
  test_cases: [
    {
      test_id: String,
      description: String,
      input: Object,
      expected_output: Object,
      validation_script: String
    }
  ],
  grading_rubric: {
    correctness_weight: Number,
    style_weight: Number,
    efficiency_weight: Number
  },
  created_at: DateTime
}
```

### Collection: `exercise_attempts`
```javascript
{
  _id: ObjectId,
  user_id: ObjectId (indexed),
  exercise_id: String (indexed),
  attempt_number: Number,
  submitted_code: String,
  execution_result: {
    stdout: String,
    stderr: String,
    exit_code: Number,
    execution_time: Number
  },
  test_results: [
    {
      test_id: String,
      passed: Boolean,
      actual_output: Object,
      error_message: String
    }
  ],
  score: Number, // 0-100
  feedback: String,
  ai_comments: String,
  submitted_at: DateTime,
  graded_at: DateTime
}
```

### Collection: `progress_state`
```javascript
{
  _id: ObjectId,
  user_id: ObjectId (unique, indexed),
  current_node_id: String,
  completed_nodes: [String], // array of node_ids
  unlocked_nodes: [String],
  node_progress: {
    "<node_id>": {
      status: String, // "not_started", "in_progress", "completed"
      completion_percentage: Number,
      exercises_completed: Number,
      exercises_total: Number,
      time_spent: Number, // minutes
      last_accessed: DateTime
    }
  },
  overall_stats: {
    total_exercises_completed: Number,
    total_time_spent: Number,
    success_rate: Number,
    streak_days: Number,
    last_activity: DateTime
  },
  updated_at: DateTime
}
```

### Collection: `chat_logs`
```javascript
{
  _id: ObjectId,
  user_id: ObjectId (indexed),
  session_id: String (indexed),
  node_id: String,
  messages: [
    {
      role: String, // "user", "assistant"
      content: String,
      timestamp: DateTime,
      context: {
        current_exercise: String,
        mode: String // "teaching", "grading", "hint", "onboarding"
      }
    }
  ],
  started_at: DateTime,
  ended_at: DateTime
}
```

### Collection: `user_memory`
```javascript
{
  _id: ObjectId,
  user_id: ObjectId (indexed),
  memory_type: String, // "confusion", "strength", "weakness", "pattern"
  concept: String, // e.g., "terraform-variables"
  description: String,
  context: String,
  frequency: Number, // how many times this came up
  severity: Number, // 1-5 for weaknesses/confusion
  first_observed: DateTime,
  last_observed: DateTime,
  resolved: Boolean,
  vector_embedding_id: String, // reference to vector DB
  related_nodes: [String]
}
```

### Collection: `diagnostic_tests`
```javascript
{
  _id: ObjectId,
  node_id: String (indexed),
  test_id: String (unique),
  title: String,
  description: String,
  passing_score: Number,
  exercises: [String], // exercise_ids
  created_at: DateTime
}
```

---

## 3. API Specification

### Base URL
`https://api.myteacher.app/v1`

### Authentication
All authenticated endpoints require:
```
Authorization: Bearer <jwt_token>
```

### Endpoints

#### Authentication

**POST** `/auth/register`
```json
Request:
{
  "email": "user@example.com",
  "password": "string",
  "full_name": "string"
}

Response: 201 Created
{
  "user_id": "string",
  "message": "User created successfully"
}
```

**POST** `/auth/login`
```json
Request:
{
  "email": "user@example.com",
  "password": "string"
}

Response: 200 OK
{
  "access_token": "jwt_token",
  "token_type": "bearer",
  "user": {
    "user_id": "string",
    "email": "string",
    "full_name": "string",
    "onboarding_completed": false
  }
}
```

**POST** `/auth/logout`
```json
Response: 200 OK
{
  "message": "Logged out successfully"
}
```

#### Onboarding

**POST** `/onboarding/start`
```json
Response: 200 OK
{
  "session_id": "string",
  "message": "Welcome message from AI",
  "questions": [
    {
      "question_id": "learning_style",
      "text": "How do you typically approach learning new technologies?"
    }
  ]
}
```

**POST** `/onboarding/answer`
```json
Request:
{
  "session_id": "string",
  "question_id": "string",
  "answer": "string or object"
}

Response: 200 OK
{
  "next_question": {...},
  "completed": false
}
```

**POST** `/onboarding/complete`
```json
Response: 200 OK
{
  "profile": {...},
  "recommended_start_node": "string",
  "message": "Onboarding complete message"
}
```

#### Curriculum / Nodes

**GET** `/nodes`
```json
Query Params:
- category: string (optional)
- difficulty: string (optional)

Response: 200 OK
{
  "nodes": [
    {
      "node_id": "terraform-basics",
      "title": "Terraform Basics",
      "description": "string",
      "difficulty": "beginner",
      "estimated_duration": 180,
      "prerequisites": [],
      "locked": false,
      "completion_status": "not_started",
      "completion_percentage": 0
    }
  ]
}
```

**GET** `/nodes/:node_id`
```json
Response: 200 OK
{
  "node": {
    "node_id": "string",
    "title": "string",
    "description": "string",
    "difficulty": "string",
    "prerequisites": [],
    "skills_taught": [],
    "content": {
      "introduction": "string",
      "concepts": [],
      "practical_applications": []
    },
    "exercises": [
      {
        "exercise_id": "string",
        "title": "string",
        "difficulty": "string",
        "completed": false
      }
    ]
  },
  "progress": {
    "status": "in_progress",
    "completion_percentage": 25,
    "exercises_completed": 2,
    "exercises_total": 8
  }
}
```

**POST** `/nodes/:node_id/start`
```json
Response: 200 OK
{
  "message": "Node started",
  "ai_introduction": "string",
  "first_exercise": "string"
}
```

**POST** `/nodes/:node_id/unlock`
```json
Request:
{
  "diagnostic_test_id": "string"
}

Response: 200 OK or 403 Forbidden
{
  "unlocked": true,
  "message": "string"
}
```

#### Exercises

**GET** `/exercises/:exercise_id`
```json
Response: 200 OK
{
  "exercise": {
    "exercise_id": "string",
    "title": "string",
    "description": "string",
    "prompt": "string",
    "starter_code": "string",
    "type": "python",
    "difficulty": "beginner"
  },
  "user_progress": {
    "attempts": 2,
    "best_score": 75,
    "completed": false
  }
}
```

**POST** `/exercises/:exercise_id/submit`
```json
Request:
{
  "code": "string",
  "language": "python"
}

Response: 200 OK
{
  "submission_id": "string",
  "status": "grading",
  "message": "Code submitted for grading"
}
```

**GET** `/exercises/:exercise_id/result/:submission_id`
```json
Response: 200 OK
{
  "status": "completed",
  "score": 85,
  "passed": true,
  "test_results": [
    {
      "test_id": "string",
      "passed": true,
      "message": "string"
    }
  ],
  "feedback": "AI-generated feedback",
  "next_step": "Continue to next exercise",
  "hints_available": 2
}
```

**POST** `/exercises/:exercise_id/hint`
```json
Request:
{
  "hint_number": 1
}

Response: 200 OK
{
  "hint": "string",
  "hints_remaining": 2
}
```

**POST** `/exercises/generate`
```json
Request:
{
  "node_id": "string",
  "difficulty": "string",
  "concept": "string",
  "user_weakness": "string (optional)"
}

Response: 200 OK
{
  "exercise": {
    "exercise_id": "string",
    "title": "string",
    "prompt": "string",
    "starter_code": "string"
  }
}
```

#### Chat / AI Interaction

**POST** `/chat/message`
```json
Request:
{
  "message": "string",
  "context": {
    "node_id": "string",
    "exercise_id": "string (optional)"
  }
}

Response: 200 OK
{
  "response": "AI response text",
  "mode": "explanation",
  "actions": [
    {
      "type": "show_content",
      "data": {...}
    }
  ],
  "next_step": "string"
}
```

**GET** `/chat/history`
```json
Query Params:
- session_id: string (optional)
- limit: number

Response: 200 OK
{
  "messages": [
    {
      "role": "user",
      "content": "string",
      "timestamp": "ISO 8601"
    }
  ]
}
```

#### Progress

**GET** `/progress`
```json
Response: 200 OK
{
  "current_node": "string",
  "completed_nodes": [],
  "unlocked_nodes": [],
  "overall_stats": {
    "total_exercises_completed": 15,
    "total_time_spent": 420,
    "success_rate": 78,
    "streak_days": 5
  },
  "node_progress": {...}
}
```

**GET** `/progress/stats`
```json
Response: 200 OK
{
  "strengths": [
    {
      "concept": "bash-loops",
      "proficiency": 85
    }
  ],
  "weaknesses": [
    {
      "concept": "terraform-state",
      "confusion_count": 5
    }
  ],
  "learning_patterns": {
    "best_time_of_day": "morning",
    "average_session_length": 45,
    "preferred_pace": "slow"
  }
}
```

#### Memory / Personalization

**GET** `/memory/weaknesses`
```json
Response: 200 OK
{
  "weaknesses": [
    {
      "concept": "string",
      "description": "string",
      "frequency": 5,
      "severity": 3,
      "related_nodes": []
    }
  ]
}
```

**GET** `/memory/patterns`
```json
Response: 200 OK
{
  "patterns": [
    {
      "pattern_type": "adhd_distraction",
      "description": "User tends to get distracted after 20 minutes",
      "recommendation": "Enable break reminders"
    }
  ]
}
```

#### Admin / Management

**POST** `/admin/nodes/create`
```json
Request:
{
  "title": "string",
  "description": "string",
  "category": "string",
  "difficulty": "string",
  "prerequisites": [],
  "content": {...}
}

Response: 201 Created
```

**POST** `/admin/exercises/create`
```json
Request:
{
  "node_id": "string",
  "exercise": {...}
}

Response: 201 Created
```

---

## 4. Frontend UI Plan

### Component Architecture

#### Core Layout Components

**`AppLayout.tsx`**
- Root layout component
- Manages dual-pane structure
- Handles responsive breakpoints
- Focus mode toggle

**`LeftPanel.tsx`** (Learning Pad)
- Container for learning content
- Switches between:
  - Node introduction
  - Exercise view
  - Results view
  - Explanation content

**`RightPanel.tsx`** (AI Chat)
- Persistent chat interface
- Message history
- Input field
- Quick action buttons (Simplify, Hint, Next)

#### Navigation Components

**`Sidebar.tsx`**
- Dashboard link
- Node map link
- Progress tracker link
- Settings

**`Header.tsx`**
- App title
- User menu
- Focus mode toggle
- Panic button

#### Onboarding Components

**`OnboardingFlow.tsx`**
- Multi-step wizard
- Progress indicator
- AI-driven questions
- Profile summary

**`OnboardingQuestion.tsx`**
- Single question display
- Input variants (text, multiple choice, slider)
- Validation

#### Node/Curriculum Components

**`NodeMap.tsx`**
- Interactive graph visualization
- Node connections (prerequisites)
- Status indicators (locked, in-progress, completed)
- Click to navigate

**`NodeCard.tsx`**
```jsx
Props:
- nodeId
- title
- description
- difficulty
- estimatedDuration
- prerequisites
- locked
- completionPercentage
- skills
```

**`NodeDetail.tsx`**
- Full node information
- Exercise list
- Start button
- Prerequisites check

**`PrerequisiteGate.tsx`**
- Displays locked state
- Shows missing prerequisites
- Diagnostic test option

#### Exercise Components

**`ExerciseView.tsx`**
- Exercise prompt
- Code editor
- Submit button
- Hint button

**`CodeEditor.tsx`**
- Monaco Editor integration
- Syntax highlighting per language
- Auto-save to local state
- Run/Submit controls

**`ExerciseResults.tsx`**
- Score display
- Test case results (pass/fail)
- AI feedback
- Next action buttons

**`TestCaseResult.tsx`**
- Individual test display
- Expected vs actual output
- Error messages

#### Progress & Stats Components

**`ProgressDashboard.tsx`**
- Overview stats
- Completed nodes
- Current streak
- Strengths/weaknesses

**`ProgressTracker.tsx`**
- Visual progress bar
- Node completion status
- Time spent

**`StrengthsWeaknesses.tsx`**
- List of concepts with proficiency
- Weakness recommendations
- Link to review exercises

#### ADHD-Friendly Components

**`FocusModeToggle.tsx`**
- Minimizes distractions
- Hides unnecessary UI elements
- Larger fonts, simpler layout

**`PanicButton.tsx`**
- Simplifies current content
- Breaks down into micro-steps
- Calming message from AI

**`BreakReminder.tsx`**
- Timer-based notifications
- Gentle prompts
- Session stats

**`StepByStepGuide.tsx`**
- Micro-task checklist
- One step at a time
- Progress indicator

#### Chat Components

**`ChatPanel.tsx`**
- Message list
- User input
- Typing indicator

**`ChatMessage.tsx`**
- User vs AI styling
- Markdown rendering
- Code blocks
- Action buttons

**`QuickActions.tsx`**
- Simplify button
- Hint button
- Explain Why button
- Next Step button

#### Utility Components

**`LoadingSpinner.tsx`**
**`ErrorBoundary.tsx`**
**`Modal.tsx`**
**`Toast.tsx`**
**`Tooltip.tsx`**

### State Management (Zustand)

**`authStore.ts`**
```typescript
interface AuthState {
  user: User | null;
  token: string | null;
  isAuthenticated: boolean;
  login: (email: string, password: string) => Promise<void>;
  logout: () => void;
}
```

**`nodeStore.ts`**
```typescript
interface NodeState {
  nodes: Node[];
  currentNode: Node | null;
  loadNodes: () => Promise<void>;
  selectNode: (nodeId: string) => void;
}
```

**`exerciseStore.ts`**
```typescript
interface ExerciseState {
  currentExercise: Exercise | null;
  editorCode: string;
  submissionStatus: 'idle' | 'submitting' | 'grading' | 'completed';
  results: ExerciseResult | null;
  submitCode: (code: string) => Promise<void>;
  requestHint: (hintNumber: number) => Promise<string>;
}
```

**`chatStore.ts`**
```typescript
interface ChatState {
  messages: Message[];
  isTyping: boolean;
  sendMessage: (content: string) => Promise<void>;
  loadHistory: () => Promise<void>;
}
```

**`uiStore.ts`**
```typescript
interface UIState {
  focusMode: boolean;
  modalOpen: boolean;
  currentModal: string | null;
  toggleFocusMode: () => void;
  openModal: (modalName: string) => void;
  closeModal: () => void;
}
```

### Styling Approach

**TailwindCSS Configuration**
- Custom color palette (learning-friendly colors)
- ADHD-optimized spacing scale
- Custom focus states
- Dark mode support

**Design Principles**
- Minimal cognitive load
- Clear visual hierarchy
- Consistent spacing
- Calming color scheme
- Large touch targets
- High contrast for readability

### Responsive Design

**Breakpoints**
- Mobile: < 768px (stacked panels)
- Tablet: 768px - 1024px (collapsible panels)
- Desktop: > 1024px (dual-pane side-by-side)

**Mobile Adaptations**
- Bottom tab navigation
- Swipe between panels
- Simplified node map
- Full-screen code editor

---

## 5. AI Agent Design

### Agent Architecture

The AI layer is organized as a multi-agent system where specialized sub-agents handle specific concerns, orchestrated by a main coordinator agent.

#### Agent Hierarchy

```
┌─────────────────────────────────────────────┐
│         Master Coordinator Agent             │
│  - Receives user input                       │
│  - Determines intent                         │
│  - Routes to appropriate sub-agent           │
│  - Aggregates responses                      │
│  - Maintains conversation context            │
└─────────────────────────────────────────────┘
                     │
     ┌───────────────┼───────────────┬────────────────┐
     │               │               │                │
┌────▼─────┐  ┌──────▼──────┐  ┌────▼─────┐  ┌──────▼──────┐
│Teaching  │  │ Exercise    │  │ Memory   │  │  Dialogue   │
│Strategy  │  │ Gen/Grading │  │ Agent    │  │  Agent      │
│Agent     │  │ Agent       │  │          │  │             │
└──────────┘  └─────────────┘  └──────────┘  └─────────────┘
     │               │               │                │
     └───────────────┴───────────────┴────────────────┘
                     │
            ┌────────▼─────────┐
            │ Explanation &    │
            │ Simplification   │
            │ Agent            │
            └──────────────────┘
```

### Sub-Agent Specifications

#### 1. Teaching Strategy Agent

**Purpose**: Determines what to teach next, how to structure curriculum, and when to unlock new content.

**Inputs**:
- User progress state
- Completed nodes
- Exercise performance history
- User profile (learning style, ADHD, goals)
- Current context (what user is asking)

**Outputs**:
```json
{
  "next_node_recommendation": "string",
  "reasoning": "string",
  "difficulty_adjustment": "increase|maintain|decrease",
  "prerequisite_review_needed": ["node_id"],
  "estimated_readiness": "ready|needs_practice|not_ready"
}
```

**Logic**:
- Analyzes success rate on recent exercises
- Checks for repeated failures on specific concepts
- Considers prerequisite mastery
- Adapts pacing based on ADHD markers
- Suggests review when patterns show weakness

**Prompting Strategy**:
```
You are a teaching strategy agent for a DevOps learning platform.

Context:
- User profile: {user_profile}
- Current progress: {progress}
- Recent performance: {recent_scores}

Your task:
1. Analyze the user's readiness for advancement
2. Recommend the next node or review session
3. Adjust difficulty if needed
4. Explain your reasoning

Consider:
- ADHD-friendly pacing (small steps)
- Confidence building (success before challenge)
- Prerequisite gaps
```

#### 2. Exercise Generation Agent

**Purpose**: Creates custom exercises tailored to user weaknesses, current node, and learning goals.

**Inputs**:
- Node ID and concepts
- Difficulty level
- User weaknesses (from memory)
- Exercise type (python, bash, terraform, etc.)

**Outputs**:
```json
{
  "exercise": {
    "title": "string",
    "description": "string",
    "prompt": "string",
    "starter_code": "string",
    "solution": "string",
    "test_cases": [
      {
        "input": {},
        "expected_output": {},
        "validation_script": "string"
      }
    ],
    "hints": [
      {
        "hint_number": 1,
        "text": "string",
        "reveal_after_attempts": 1
      }
    ],
    "learning_objectives": ["string"]
  }
}
```

**Logic**:
- Retrieves relevant concepts from node
- Considers user's past confusion points
- Generates realistic, practical scenarios
- Creates test cases with varying complexity
- Provides progressive hints

**Prompting Strategy**:
```
You are an exercise generation agent specializing in DevOps education.

Generate a {difficulty} level exercise for the concept: {concept}
Node: {node_title}
User's known weaknesses: {weaknesses}

Requirements:
1. Practical, real-world scenario
2. Clear instructions (ADHD-friendly)
3. Testable outputs
4. 3-5 test cases (edge cases included)
5. 3 progressive hints
6. Example solution

Output format: JSON
```

#### 3. Exercise Grading Agent

**Purpose**: Evaluates submitted code, provides detailed feedback, identifies mistakes, and suggests improvements.

**Inputs**:
- Submitted code
- Exercise definition
- Test execution results (from sandbox)
- User's past attempts

**Outputs**:
```json
{
  "score": 85,
  "passed": true,
  "test_results": [
    {
      "test_id": "string",
      "passed": true,
      "feedback": "string"
    }
  ],
  "overall_feedback": "string",
  "mistakes": [
    {
      "line": 12,
      "issue": "string",
      "suggestion": "string"
    }
  ],
  "strengths": ["string"],
  "next_step": "string",
  "encouragement": "string"
}
```

**Logic**:
- Analyzes test pass/fail results
- Identifies code quality issues
- Compares to solution
- Detects common anti-patterns
- Provides constructive feedback
- Encourages without false praise

**Prompting Strategy**:
```
You are a grading agent for a DevOps learning platform.

Exercise: {exercise_prompt}
User's code: {submitted_code}
Test results: {test_results}

Task:
1. Evaluate correctness (tests passed/failed)
2. Identify specific mistakes
3. Provide line-by-line feedback
4. Suggest improvements
5. Recognize strengths
6. Encourage next step

Tone: Compassionate, constructive, motivating (user has ADHD and overthinks)
```

#### 4. Memory Agent

**Purpose**: Stores and retrieves user-specific learning patterns, weaknesses, strengths, and emotional states.

**Responsibilities**:
- Detect confusion patterns
- Track repeated mistakes
- Identify ADHD triggers (distraction, overwhelm)
- Store emotional context (frustration, confidence)
- Retrieve relevant history during teaching

**Operations**:

**Write Memory**:
```json
{
  "user_id": "string",
  "memory_type": "weakness",
  "concept": "terraform-variables",
  "description": "User confused variable syntax 3 times",
  "severity": 4,
  "context": "Always forgets var. prefix"
}
```

**Query Memory**:
```
Input: "What are the user's weaknesses in Terraform?"
Output: [
  {
    "concept": "terraform-variables",
    "frequency": 5,
    "severity": 4
  }
]
```

**Vector Storage**:
- Embeds user's struggles and questions
- Semantic search for similar past confusions
- Uses Pinecone or Weaviate

**Memory Triggers**:
- After each exercise (detect new patterns)
- When user asks for help (search similar past issues)
- Before generating exercises (target weaknesses)
- During teaching (recall past explanations)

#### 5. Explanation & Simplification Agent

**Purpose**: Explains concepts in 3 levels of detail and simplifies on demand.

**Inputs**:
- Concept to explain
- User's current understanding level
- Detail preference (simple, medium, expert)
- User confusion history

**Outputs**:
```json
{
  "explanation_simple": "string",
  "explanation_detailed": "string",
  "explanation_expert": "string",
  "why_it_matters": "string",
  "real_world_example": "string",
  "common_pitfalls": ["string"]
}
```

**3 Levels of Explanation**:

1. **Simple** (ADHD-friendly, minimal jargon)
   - 2-3 sentences
   - Analogy-based
   - Direct, practical

2. **Medium** (Technical but clear)
   - 1-2 paragraphs
   - Technical terms with definitions
   - Examples included

3. **Expert** (Deep dive)
   - Full technical detail
   - Architecture implications
   - Best practices

**Panic/Simplify Button Behavior**:
- Triggered when user feels overwhelmed
- Agent breaks down current task into micro-steps
- Uses only "simple" explanations
- Reduces cognitive load
- Provides single next action

**Prompting Strategy**:
```
You are an explanation agent for DevOps learners (ADHD-optimized).

Concept: {concept}
User's level: {level}
User confusion history: {confusion}

Provide 3 explanations:
1. Simple (3 sentences, no jargon)
2. Medium (1 paragraph, some technical detail)
3. Expert (full detail)

Also:
- Why this matters (practical value)
- Real-world example
- Common mistakes
```

#### 6. Dialogue Agent

**Purpose**: Manages conversational flow, maintains motivating tone, and keeps messages concise and actionable.

**Responsibilities**:
- Format AI responses
- Maintain compassionate tone
- Keep messages short
- Always provide next action
- Detect and respond to emotional states

**Tone Guidelines**:
- Compassionate but not patronizing
- Encouraging but realistic
- Simple language (Dr. Angela Yu style)
- Action-oriented
- Patient

**Message Structure**:
```
1. Acknowledge user input
2. Provide core response (1-2 sentences)
3. Next actionable step
```

**Emotional Response Patterns**:

- **User frustrated**: "I see this is tricky. Let's break it down into smaller pieces."
- **User confused**: "Let me explain this differently..."
- **User succeeding**: "Great work! You're building strong habits."
- **User distracted**: "No worries. Let's refocus on the next small step."

### AI Workflow: Teach-Loop

The core teaching interaction follows this loop:

```
1. User Input
   │
   ├─> Parse intent (question, exercise submission, request)
   │
2. Memory Retrieval
   │
   ├─> Query vector DB for relevant past struggles
   ├─> Load user profile and preferences
   │
3. Context Analysis
   │
   ├─> Determine mode (teaching, grading, explaining, onboarding)
   │
4. Route to Sub-Agent
   │
   ├─> Teaching Strategy → next node recommendation
   ├─> Exercise Generation → new exercise
   ├─> Grading → evaluate submission
   ├─> Explanation → simplify concept
   │
5. Generate Response
   │
   ├─> Dialogue Agent formats output
   ├─> Include next action
   │
6. Memory Write
   │
   ├─> Store new patterns, weaknesses, strengths
   │
7. Deliver to User
```

### AI System Prompts

**Master Coordinator Prompt**:
```
You are the master AI coordinator for MyTeacher, a hyper-personalized DevOps learning platform.

Your responsibilities:
1. Receive all user inputs
2. Analyze intent (teaching, exercise, question, confusion, etc.)
3. Route to appropriate sub-agent
4. Maintain conversation context
5. Ensure responses are ADHD-friendly (concise, actionable, compassionate)

User profile: {user_profile}
Current node: {current_node}
Recent progress: {progress}

Always:
- Keep messages short
- Provide next action
- Be encouraging but realistic
- Detect overwhelm and simplify
```

**Example Agent Invocation**:
```python
# Backend orchestration pseudo-code
async def handle_user_message(user_id, message, context):
    # 1. Retrieve memory
    memory = await memory_service.retrieve(user_id, context)

    # 2. Determine intent
    intent = await coordinator_agent.parse_intent(message, context)

    # 3. Route to sub-agent
    if intent == "exercise_submission":
        result = await grading_agent.grade(message, context, memory)
    elif intent == "request_hint":
        result = await explanation_agent.provide_hint(context, memory)
    elif intent == "confusion":
        result = await explanation_agent.simplify(context, memory)

    # 4. Format response
    response = await dialogue_agent.format(result)

    # 5. Store memory
    await memory_service.write(user_id, result.memory_updates)

    return response
```

### Vector Memory Implementation

**Embedding Strategy**:
- Embed user questions, confusions, mistakes
- Embed exercise feedback and comments
- Embed chat messages with context

**Storage**:
- Use Pinecone or Weaviate
- Namespace by user_id
- Metadata: timestamp, node_id, concept, sentiment

**Retrieval**:
- Semantic search for similar past issues
- Top-k retrieval (k=5)
- Re-rank by recency and severity

**Example Query**:
```
User struggling with: "I don't understand why Pulumi uses .get()"

Vector search returns:
1. "User confused about Pulumi Outputs (3 days ago)"
2. "User asked why Terraform uses count (1 week ago)"
3. "User struggled with async concepts (2 weeks ago)"

→ Teaching Strategy Agent uses this to tailor explanation
```

---

## 6. Project Folder Structure

```
myteacher/
│
├── frontend/                     # Next.js React Application
│   ├── public/
│   │   ├── images/
│   │   └── icons/
│   ├── src/
│   │   ├── app/                  # Next.js 13+ app directory
│   │   │   ├── (auth)/
│   │   │   │   ├── login/
│   │   │   │   └── register/
│   │   │   ├── (dashboard)/
│   │   │   │   ├── layout.tsx
│   │   │   │   ├── page.tsx
│   │   │   │   ├── nodes/
│   │   │   │   │   ├── [nodeId]/
│   │   │   │   │   └── page.tsx
│   │   │   │   ├── exercise/
│   │   │   │   │   └── [exerciseId]/
│   │   │   │   └── progress/
│   │   │   ├── onboarding/
│   │   │   └── layout.tsx
│   │   ├── components/
│   │   │   ├── layout/
│   │   │   │   ├── AppLayout.tsx
│   │   │   │   ├── LeftPanel.tsx
│   │   │   │   ├── RightPanel.tsx
│   │   │   │   ├── Sidebar.tsx
│   │   │   │   └── Header.tsx
│   │   │   ├── onboarding/
│   │   │   │   ├── OnboardingFlow.tsx
│   │   │   │   └── OnboardingQuestion.tsx
│   │   │   ├── nodes/
│   │   │   │   ├── NodeMap.tsx
│   │   │   │   ├── NodeCard.tsx
│   │   │   │   ├── NodeDetail.tsx
│   │   │   │   └── PrerequisiteGate.tsx
│   │   │   ├── exercise/
│   │   │   │   ├── ExerciseView.tsx
│   │   │   │   ├── CodeEditor.tsx
│   │   │   │   ├── ExerciseResults.tsx
│   │   │   │   └── TestCaseResult.tsx
│   │   │   ├── progress/
│   │   │   │   ├── ProgressDashboard.tsx
│   │   │   │   ├── ProgressTracker.tsx
│   │   │   │   └── StrengthsWeaknesses.tsx
│   │   │   ├── chat/
│   │   │   │   ├── ChatPanel.tsx
│   │   │   │   ├── ChatMessage.tsx
│   │   │   │   └── QuickActions.tsx
│   │   │   ├── adhd/
│   │   │   │   ├── FocusModeToggle.tsx
│   │   │   │   ├── PanicButton.tsx
│   │   │   │   ├── BreakReminder.tsx
│   │   │   │   └── StepByStepGuide.tsx
│   │   │   └── common/
│   │   │       ├── Button.tsx
│   │   │       ├── Modal.tsx
│   │   │       ├── Toast.tsx
│   │   │       └── LoadingSpinner.tsx
│   │   ├── stores/
│   │   │   ├── authStore.ts
│   │   │   ├── nodeStore.ts
│   │   │   ├── exerciseStore.ts
│   │   │   ├── chatStore.ts
│   │   │   └── uiStore.ts
│   │   ├── lib/
│   │   │   ├── api.ts              # API client
│   │   │   ├── auth.ts
│   │   │   └── constants.ts
│   │   ├── hooks/
│   │   │   ├── useAuth.ts
│   │   │   ├── useNodes.ts
│   │   │   ├── useExercise.ts
│   │   │   └── useChat.ts
│   │   ├── types/
│   │   │   ├── user.ts
│   │   │   ├── node.ts
│   │   │   ├── exercise.ts
│   │   │   └── chat.ts
│   │   └── styles/
│   │       └── globals.css
│   ├── tailwind.config.js
│   ├── next.config.js
│   ├── tsconfig.json
│   └── package.json
│
├── backend/                      # FastAPI Python Application
│   ├── app/
│   │   ├── main.py               # FastAPI app entry
│   │   ├── config.py             # Environment config
│   │   ├── dependencies.py       # Shared dependencies
│   │   │
│   │   ├── api/                  # API Routes
│   │   │   ├── v1/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── auth.py
│   │   │   │   ├── onboarding.py
│   │   │   │   ├── nodes.py
│   │   │   │   ├── exercises.py
│   │   │   │   ├── chat.py
│   │   │   │   ├── progress.py
│   │   │   │   └── memory.py
│   │   │   └── __init__.py
│   │   │
│   │   ├── models/               # Pydantic models & DB schemas
│   │   │   ├── user.py
│   │   │   ├── node.py
│   │   │   ├── exercise.py
│   │   │   ├── progress.py
│   │   │   ├── memory.py
│   │   │   └── chat.py
│   │   │
│   │   ├── services/             # Business logic layer
│   │   │   ├── auth_service.py
│   │   │   ├── node_service.py
│   │   │   ├── exercise_service.py
│   │   │   ├── grading_service.py
│   │   │   ├── memory_service.py
│   │   │   ├── progress_service.py
│   │   │   ├── chat_service.py
│   │   │   └── sandbox_service.py
│   │   │
│   │   ├── ai/                   # AI orchestration layer
│   │   │   ├── __init__.py
│   │   │   ├── coordinator.py    # Master coordinator
│   │   │   ├── agents/
│   │   │   │   ├── teaching_strategy.py
│   │   │   │   ├── exercise_generator.py
│   │   │   │   ├── grading_agent.py
│   │   │   │   ├── memory_agent.py
│   │   │   │   ├── explanation_agent.py
│   │   │   │   └── dialogue_agent.py
│   │   │   ├── prompts/          # System prompts
│   │   │   │   ├── coordinator_prompt.txt
│   │   │   │   ├── teaching_prompt.txt
│   │   │   │   ├── exercise_gen_prompt.txt
│   │   │   │   └── grading_prompt.txt
│   │   │   └── utils.py
│   │   │
│   │   ├── db/                   # Database layer
│   │   │   ├── mongodb.py        # MongoDB connection
│   │   │   ├── redis.py          # Redis connection
│   │   │   ├── vector_db.py      # Pinecone/Weaviate
│   │   │   └── repositories/
│   │   │       ├── user_repository.py
│   │   │       ├── node_repository.py
│   │   │       ├── exercise_repository.py
│   │   │       ├── progress_repository.py
│   │   │       └── memory_repository.py
│   │   │
│   │   ├── sandbox/              # Code execution sandbox
│   │   │   ├── __init__.py
│   │   │   ├── docker_runner.py  # Docker orchestration
│   │   │   ├── runners/
│   │   │   │   ├── python_runner.py
│   │   │   │   ├── bash_runner.py
│   │   │   │   ├── terraform_runner.py
│   │   │   │   └── pulumi_runner.py
│   │   │   └── validators/
│   │   │       ├── test_validator.py
│   │   │       └── output_validator.py
│   │   │
│   │   ├── workers/              # Background job workers
│   │   │   ├── grading_worker.py
│   │   │   └── memory_worker.py
│   │   │
│   │   ├── middleware/
│   │   │   ├── auth_middleware.py
│   │   │   └── error_handler.py
│   │   │
│   │   └── utils/
│   │       ├── security.py
│   │       ├── validators.py
│   │       └── helpers.py
│   │
│   ├── tests/
│   │   ├── test_api/
│   │   ├── test_services/
│   │   └── test_agents/
│   │
│   ├── alembic/                  # (if using SQL in future)
│   ├── requirements.txt
│   ├── Dockerfile
│   └── pyproject.toml
│
├── sandbox/                      # Sandbox Docker images
│   ├── python/
│   │   ├── Dockerfile
│   │   └── requirements.txt
│   ├── bash/
│   │   └── Dockerfile
│   ├── terraform/
│   │   └── Dockerfile
│   └── pulumi/
│       └── Dockerfile
│
├── infrastructure/               # Infrastructure as Code
│   ├── docker-compose.yml       # Local development
│   ├── kubernetes/              # K8s manifests (production)
│   └── terraform/               # Cloud infrastructure
│
├── scripts/                      # Utility scripts
│   ├── seed_database.py         # Seed initial nodes/exercises
│   ├── create_admin.py
│   └── migrate.py
│
├── docs/                         # Documentation
│   ├── api-spec.md
│   ├── architecture.md
│   ├── deployment.md
│   └── agent-design.md
│
├── .github/
│   └── workflows/
│       ├── ci.yml
│       └── deploy.yml
│
├── .env.example
├── .gitignore
├── README.md
└── LICENSE
```

---

## 7. MVP Implementation Roadmap

### Phase 1: Foundation & Infrastructure (Week 1-2)

**Goals**: Set up project structure, databases, authentication, basic API

**Tasks**:
1. Initialize project repositories (frontend, backend)
2. Set up MongoDB, Redis, Docker
3. Create database collections and schemas
4. Implement authentication (register, login, JWT)
5. Set up FastAPI with basic health check endpoint
6. Set up Next.js with basic routing
7. Implement API client in frontend
8. Create basic layout (AppLayout, LeftPanel, RightPanel)

**Deliverables**:
- Working auth flow (register → login → dashboard)
- Database connected and seeded with test data
- Dual-pane UI skeleton

### Phase 2: Curriculum & Nodes (Week 3)

**Goals**: Implement node system, curriculum visualization

**Tasks**:
1. Create node CRUD endpoints (backend)
2. Implement node service and repository
3. Build NodeMap component (frontend)
4. Build NodeCard and NodeDetail components
5. Implement node navigation
6. Add prerequisite logic (unlock mechanism)
7. Seed database with 5-10 sample nodes (Terraform, Python, Bash)

**Deliverables**:
- Node map visualization
- Clickable node cards
- Locked/unlocked states
- Basic progress tracking

### Phase 3: Exercise System (Week 4-5)

**Goals**: Build exercise engine, code editor, submission flow

**Tasks**:
1. Create exercise CRUD endpoints
2. Build CodeEditor component (Monaco)
3. Implement exercise submission endpoint
4. Build sandbox Docker images (Python, Bash)
5. Implement sandbox execution service
6. Create test case validation logic
7. Build ExerciseResults component
8. Seed database with 10-15 exercises across nodes

**Deliverables**:
- Working code editor
- Submit → execute → display results flow
- Basic test case validation
- Exercise completion tracking

### Phase 4: AI Agent Integration (Week 6-7)

**Goals**: Integrate Claude API, build basic teaching flow

**Tasks**:
1. Set up Claude API integration
2. Implement Master Coordinator Agent
3. Implement Dialogue Agent (basic chat)
4. Build ChatPanel component (frontend)
5. Connect chat to backend AI service
6. Implement basic memory storage (MongoDB)
7. Create simple teaching prompts
8. Build explanation flow (user asks → AI explains)

**Deliverables**:
- Working AI chat in right panel
- AI responds to user questions
- Basic teaching conversation flow

### Phase 5: Grading & Feedback (Week 8)

**Goals**: AI-powered exercise grading

**Tasks**:
1. Implement Grading Agent
2. Create grading prompt templates
3. Integrate grading with sandbox results
4. Display AI feedback in ExerciseResults
5. Implement hint system
6. Add grading rubric logic
7. Store attempt history

**Deliverables**:
- AI grades submitted exercises
- Detailed feedback on mistakes
- Hints available on demand

### Phase 6: Onboarding Flow (Week 9)

**Goals**: Build onboarding questionnaire and profile creation

**Tasks**:
1. Create onboarding endpoints
2. Build OnboardingFlow component
3. Implement AI-driven question generation
4. Store onboarding profile
5. Generate initial curriculum recommendations
6. Redirect to dashboard after onboarding

**Deliverables**:
- Multi-step onboarding wizard
- AI asks personalized questions
- Profile stored and used for teaching

### Phase 7: Memory & Personalization (Week 10)

**Goals**: Implement vector memory, track weaknesses/strengths

**Tasks**:
1. Set up vector database (Pinecone/Weaviate)
2. Implement Memory Agent
3. Create memory write/query logic
4. Embed user struggles and feedback
5. Retrieve memory during teaching
6. Display strengths/weaknesses on dashboard
7. Implement Teaching Strategy Agent (uses memory)

**Deliverables**:
- AI remembers past struggles
- Personalized teaching based on history
- Dashboard shows strengths/weaknesses

### Phase 8: ADHD Features (Week 11)

**Goals**: Implement focus mode, panic button, break reminders

**Tasks**:
1. Build FocusModeToggle component
2. Implement focus mode styling (minimal UI)
3. Build PanicButton component
4. Implement simplification logic (AI agent)
5. Add BreakReminder component (timer-based)
6. Add StepByStepGuide component
7. Implement micro-task breakdown

**Deliverables**:
- Focus mode hides distractions
- Panic button simplifies content
- Break reminders trigger after 25 minutes
- Step-by-step micro-tasks displayed

### Phase 9: Advanced Grading (Week 12)

**Goals**: Support Terraform, Pulumi, Ansible exercises

**Tasks**:
1. Build Terraform sandbox Docker image
2. Build Pulumi sandbox Docker image
3. Implement Terraform runner and validator
4. Implement Pulumi runner and validator
5. Create Terraform/Pulumi exercises
6. Test grading for IaC code

**Deliverables**:
- Terraform exercises with `terraform plan` validation
- Pulumi exercises with `pulumi preview` validation

### Phase 10: Polish & Testing (Week 13-14)

**Goals**: Bug fixes, performance optimization, UX improvements

**Tasks**:
1. End-to-end testing (Playwright)
2. API integration tests
3. UI/UX refinements based on testing
4. Performance optimization (caching, lazy loading)
5. Error handling improvements
6. Security audit (sandbox, API, auth)
7. Accessibility improvements
8. Documentation (API, architecture, deployment)

**Deliverables**:
- Stable, tested application
- Comprehensive test coverage
- Deployment-ready codebase

### Phase 11: Deployment (Week 15)

**Goals**: Deploy to production

**Tasks**:
1. Set up production environment (AWS/GCP/Azure)
2. Configure MongoDB Atlas
3. Configure Redis Cloud
4. Deploy backend (containerized)
5. Deploy frontend (Vercel/Netlify)
6. Set up CI/CD pipeline (GitHub Actions)
7. Configure monitoring (Sentry, DataDog)
8. Set up backups

**Deliverables**:
- Live production application
- Monitoring and logging in place
- Automated deployments

---

## 8. Security Model

### Authentication & Authorization

**User Authentication**:
- JWT-based authentication
- Tokens expire after 24 hours
- Refresh token mechanism
- Password hashing: bcrypt (cost factor 12)
- Rate limiting on login endpoint (5 attempts per 15 minutes)

**Authorization**:
- Role-based access control (user, admin)
- Users can only access their own data
- Admin endpoints protected with admin role check

### Data Privacy

**Personal Data Storage**:
- User profile data encrypted at rest (MongoDB encryption)
- No storage of sensitive data beyond email/password
- User can request data export (GDPR compliance)
- User can request account deletion

**AI Memory Privacy**:
- Memory data tied only to user_id
- No cross-user data leakage
- Vector embeddings anonymized
- No personal identifiers in embeddings

**Chat Logs**:
- Stored for personalization only
- Not shared with third parties
- User can delete chat history

### Sandbox Security

**Docker Isolation**:
- Each execution in isolated container
- No network access (--network=none)
- Limited CPU (--cpus="0.5")
- Limited memory (--memory="256m")
- Read-only root filesystem
- Temporary writable /workspace directory

**Resource Limits**:
- Execution timeout: 30 seconds
- Max output size: 10 KB
- Max processes: 10
- No root privileges

**Whitelisted Commands**:
- Python: Standard library only (no pip install)
- Bash: Core utils only (no curl, wget, nc)
- Terraform: terraform init/plan only (no apply)
- Pulumi: pulumi preview only (no up)

**Filesystem Isolation**:
- Each execution gets fresh ephemeral filesystem
- No persistent storage between runs
- No access to host filesystem

### API Security

**Input Validation**:
- Pydantic models for all request bodies
- Strict type checking
- Max code length: 10,000 characters
- Sanitize user input before storage

**Rate Limiting**:
- 100 requests per minute per user
- 10 exercise submissions per minute per user
- 5 chat messages per minute per user

**CORS**:
- Whitelist frontend domain only
- No wildcard origins

**HTTPS**:
- Enforce HTTPS in production
- HSTS headers

### Cloud Resource Protection

**No Real Cloud Deployments**:
- Terraform/Pulumi run in plan/preview mode only
- No AWS/GCP/Azure credentials provided to sandbox
- No real infrastructure created

**LocalStack for Testing**:
- Use LocalStack for simulated AWS environment
- Fully local, no real cloud costs

### Sensitive Data Handling

**Environment Variables**:
- API keys stored in environment variables (not code)
- `.env` file excluded from git
- Secrets managed via secure vault (AWS Secrets Manager, HashiCorp Vault)

**API Keys**:
- Claude API key: Backend only (never exposed to frontend)
- Database credentials: Backend only
- JWT secret: Rotated monthly

### Monitoring & Logging

**Security Monitoring**:
- Log all authentication attempts
- Log all sandbox executions
- Alert on suspicious activity (rate limit violations, injection attempts)

**Telemetry**:
- OpenTelemetry for distributed tracing
- Logs stored securely (AWS CloudWatch, Datadog)
- No sensitive data in logs (mask passwords, tokens)

### Compliance

**GDPR**:
- Data export endpoint
- Data deletion endpoint
- Privacy policy displayed during registration

**Children's Privacy**:
- No collection of age data
- Assume users are 18+
- COPPA compliance if under 13

---

## Additional Considerations

### Scalability Plan

**Database**:
- MongoDB sharding for horizontal scaling
- Indexes on frequently queried fields (user_id, node_id, exercise_id)
- TTL indexes for temporary data (session logs)

**Caching**:
- Redis cache for:
  - Node metadata
  - Exercise definitions
  - User progress state
- Cache invalidation on updates

**Background Jobs**:
- Redis queue for grading jobs
- Celery workers for async processing
- Separate worker pool for sandbox execution

**CDN**:
- Frontend assets served via CDN (Cloudflare, AWS CloudFront)
- Static content caching

### Cost Optimization

**Claude API Usage**:
- Use Claude Haiku for simple tasks (grading, hints)
- Use Claude Sonnet for complex tasks (exercise generation, teaching)
- Cache common explanations
- Implement response caching

**Sandbox Execution**:
- Pool Docker containers (warm start)
- Limit concurrent executions (queue overflow)
- Time-based scaling

**Database**:
- MongoDB free tier sufficient for MVP (512 MB)
- Upgrade to paid tier for production

### Observability

**Metrics**:
- User engagement metrics (sessions, exercises completed)
- AI metrics (response time, token usage)
- Sandbox metrics (execution time, failure rate)
- Error rates per endpoint

**Dashboards**:
- Grafana dashboards for real-time monitoring
- Alerts for system health

### Future Enhancements (Post-MVP)

1. **Collaborative Learning**:
   - Peer review exercises
   - Discussion forums

2. **Gamification**:
   - Badges, achievements
   - Leaderboards (opt-in)

3. **Advanced Personalization**:
   - Learning style detection (visual, kinesthetic)
   - Time-of-day recommendations

4. **Mobile App**:
   - React Native app
   - Offline mode

5. **Live Coding Sessions**:
   - WebRTC-based pair programming with AI
   - Screen sharing

6. **Certification Prep**:
   - AWS, Azure, GCP cert-specific tracks
   - Mock exams

7. **Real Project Portfolio**:
   - Connect to user's real GitHub
   - Deploy to real cloud (with cost limits)

8. **Community Content**:
   - User-generated exercises
   - Community-vetted curriculum

---

## Conclusion

This implementation plan provides a complete blueprint for building MyTeacher, a hyper-personalized AI DevOps mentor. The architecture balances technical sophistication with user-centric design, prioritizing ADHD-friendly features, secure sandboxing, and intelligent AI-driven teaching.

**Key Strengths**:
- Clear separation of concerns (frontend, backend, AI, infrastructure)
- Robust security model (sandboxing, authentication, privacy)
- Scalable architecture (MongoDB, Redis, Docker, vector DB)
- Comprehensive AI agent design (multi-agent specialization)
- Detailed MVP roadmap (15-week timeline)

**Next Steps**:
1. Review and approve this plan
2. Set up development environment
3. Begin Phase 1 implementation
4. Iterate based on user feedback

---

**End of Implementation Plan**
