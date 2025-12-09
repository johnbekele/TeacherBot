# 🤖 Context-Aware AI Chat System

## 🎯 The Problem (Before):
- Chat box was duplicated
- AI behaved the same everywhere
- No planning/path creation capability
- Chat didn't reset when changing contexts

## ✅ The Solution (After):
- Single, synced chat panel
- **Two AI Modes**:
  1. **Planning Mode** (Dashboard) - Creates learning paths
  2. **Teaching Mode** (Inside nodes) - Focused topic teaching

---

## 🗺️ Complete User Journey:

### **1. Dashboard (Planning Mode)**
```
User arrives at /dashboard

AI Context: Planning & Path Creation
AI Personality: Advisor & Planner

User: "I want to learn Docker"

AI:
- Analyzes user's experience level
- Asks clarifying questions
- Creates personalized learning path
- Generates nodes dynamically

Result: Custom Docker learning path with nodes:
- Docker Basics
- Containers & Images
- Docker Compose
- Docker Networking
- etc.
```

### **2. Inside Node (Teaching Mode)**
```
User clicks "Docker Basics" node

AI Context: Docker Basics ONLY
AI Personality: Teacher & Guide

Chat resets automatically
AI focuses on Docker basics only

User: "How do containers work?"

AI:
- Explains containers
- Shows code examples
- Gives exercises
- Provides feedback
- Navigates to next topic when ready
```

### **3. Exit Node (Back to Planning)**
```
User goes back to dashboard

AI Context: Planning
Chat resets again

User: "What should I learn after Docker?"

AI: "Great progress! Let's add Kubernetes to your path..."
```

---

## 🔧 Technical Implementation:

### **Context Types**:

1. **"planning"** - Dashboard, general advice
2. **"learning_session"** - Inside a node
3. **"exercise"** - Doing an exercise
4. **"general"** - Fallback

### **Chat Reset Triggers**:
- ✅ When entering dashboard (`clearChat()`)
- ✅ When entering a node (new session)
- ✅ When changing nodes
- ✅ Manual reset available

### **AI Behavior Per Context**:

**Planning Mode (`contextType="planning"`)**:
```python
System Prompt:
"You are a learning path advisor. Help users:
- Discover what they want to learn
- Assess their current level
- Create personalized learning paths
- Recommend tools and topics
- Generate custom nodes

Available Tools:
- create_learning_path
- assess_user_level
- generate_custom_node
- recommend_next_topic"
```

**Teaching Mode (`contextType="learning_session"`)**:
```python
System Prompt:
"You are teaching {node_title}.
Focus ONLY on this topic.
Help user master this specific skill.

Available Tools:
- display_learning_content
- generate_exercise
- execute_code
- show_interactive_component
- navigate_to_next_step"
```

---

## 📂 File Structure:

```
frontend/src/
├── app/
│   ├── dashboard/
│   │   └── page.tsx          ✅ NEW - Planning Mode UI
│   ├── nodes/[nodeId]/
│   │   └── page.tsx          ✏️  MODIFIED - Teaching Mode
│   └── learn/[nodeId]/
│       └── page.tsx          ✏️  MODIFIED - Learning Session
├── components/
│   ├── chat/
│   │   ├── ChatPanel.tsx     ✏️  MODIFIED - Context-aware
│   │   └── InteractiveComponent.tsx ✅ NEW
│   └── layout/
│       ├── AppLayout.tsx     ✏️  MODIFIED - Passes context
│       └── RightPanel.tsx    ✏️  MODIFIED - Single chat
└── stores/
    └── chatStore.ts          ✏️  MODIFIED - Has clearChat()
```

---

## 🎮 How to Use:

### **For Users**:

**Step 1: Start at Dashboard**
```
http://localhost:3000/dashboard
```

**Step 2: Tell AI What You Want to Learn**
```
Chat: "I want to become a DevOps engineer"

AI will:
1. Ask about your background
2. Assess your level
3. Create a learning path
4. Show you the first steps
```

**Step 3: Start Learning**
```
Click on first node → AI switches to teaching mode
AI focuses on that one topic
Complete exercises with AI help
```

**Step 4: Progress**
```
After mastering a topic:
- AI suggests next topic
- Creates new nodes if needed
- Tracks your progress
```

---

## 🎨 UI/UX Flow:

### **Dashboard View**:
```
┌──────────────────────────────────────────┐
│ Good morning, John! 👋                  │
│ What would you like to learn today?     │
├──────────────────────────────────────────┤
│ 🤖 AI Learning Path Creator              │
│                                          │
│ Tell me what you want to learn...       │
│                                          │
│ Try asking:                              │
│ • "I want to learn Docker"               │
│ • "Help me plan a DevOps path"           │
└──────────────────────────────────────────┘

[Right Panel: Planning AI Chat]
```

### **Inside Node View**:
```
┌──────────────────────────────────────────┐
│ Docker Basics                            │
│ [Learning Content]                       │
│ [Code Examples]                          │
│ [Continue to Practice →]                 │
└──────────────────────────────────────────┘

[Right Panel: Teaching AI Chat]
(Focused on Docker only)
```

---

## 🚀 New Features Enabled:

### **1. Dynamic Path Creation**
```
User: "I want to learn CI/CD"

AI creates nodes:
- [NEW] Git Fundamentals
- [NEW] GitHub Actions
- [NEW] Jenkins Basics
- [NEW] Pipeline Design
- [NEW] Deployment Strategies
```

### **2. Personalized Pacing**
```
Dashboard AI: "I see you completed Docker fast!
Let's add advanced topics to your path."

[Generates advanced Docker nodes]
```

### **3. Adaptive Learning**
```
Teaching AI tracks:
- Struggling topics → More practice
- Easy topics → Move faster
- Preferred learning style → Adjust content
```

---

## 🔥 Key Improvements:

### **Before**:
❌ AI was same everywhere
❌ No planning capability
❌ Chat didn't reset
❌ Duplicate chat boxes
❌ No path creation

### **After**:
✅ Context-aware AI behavior
✅ Planning mode on dashboard
✅ Chat resets per context
✅ Single, synced chat
✅ Dynamic path creation

---

## 📊 Context Switching Logic:

```typescript
// Dashboard
<AppLayout
  contextType="planning"    // AI in planning mode
  contextId="dashboard"
  onActionReceived={handleDashboardActions}
/>

// Node Detail
<AppLayout
  contextType="learning_session"  // AI in teaching mode
  contextId={nodeId}              // Focused on this node
  sessionId={sessionId}           // Maintains session
  onActionReceived={handleLearningActions}
/>

// Exercise
<AppLayout
  contextType="exercise"    // AI helps with exercise
  contextId={exerciseId}
  sessionId={sessionId}
  onActionReceived={handleExerciseActions}
/>
```

---

## 🎯 Testing the New System:

### **Test 1: Planning Mode**
```bash
1. Go to http://localhost:3000/dashboard
2. Chat should be empty (reset)
3. Ask: "I want to learn Docker"
4. AI should act as planner/advisor
```

### **Test 2: Teaching Mode**
```bash
1. Click on any node
2. Chat resets again
3. Ask: "Explain this topic"
4. AI focuses on that topic only
```

### **Test 3: Context Switch**
```bash
1. In node → Ask about Docker
2. Go back to dashboard
3. Chat resets
4. Ask about Docker again
5. AI responds differently (planning vs teaching)
```

---

## 💡 Future Enhancements:

1. **Persistent Learning Paths**
   - Save AI-generated paths to database
   - Share paths with other users

2. **Progress Tracking**
   - Visual path completion
   - Skill badges
   - Certificates

3. **Collaborative Learning**
   - AI creates group study paths
   - Team learning recommendations

---

## 🎓 Summary:

The AI now has **two personalities**:

1. **Planning AI** (Dashboard)
   - Advisor
   - Path creator
   - Goal-oriented

2. **Teaching AI** (Nodes)
   - Instructor
   - Exercise creator
   - Topic-focused

Chat **resets** when switching contexts, ensuring:
- ✅ No confusion
- ✅ Relevant conversations
- ✅ Clean slate per context

This creates a **natural learning flow**:
Plan → Learn → Practice → Progress → Plan Next

---

**Status**: ✅ Implementation Complete
**Next Step**: Test dashboard at `/dashboard` and experience the new flow!
