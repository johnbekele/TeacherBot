You are an expert full-stack architect, AI systems designer, DevOps engineer, and educational-technology designer.  
Your task: **plan and generate the complete architecture, code structure, API spec, DB schema, agent reasoning flow, and UI/UX design** for a web application that serves as a hyper-personal DevOps mentor for a single learner.

This application acts like a private “AI DevOps Instructor” that teaches Terraform, Pulumi, Python scripting, Bash, Ansible, CI/CD, cloud, etc., using micro-steps, ADHD-friendly pacing, hands-on exercises, and persistent memory.

===========================
### 🧠 USER STORY (KEY REQUIREMENTS)
The user is:
- an overthinker, slow learner at first, but becomes obsessed once understanding the logic
- easily overwhelmed, ADHD, gets distracted researching docs and going down rabbit holes
- learns best with step-by-step instruction and “do this now” micro guidance
- likes simple, practical explanations (like Dr Angela Yu’s teaching style)
- gets frustrated when they don’t understand *why* a function or API is used (ex: why Pulumi uses `.get()`)
- prefers practical exercises connected to real-world tasks
- needs the system to save all progress and personal struggles so the AI mentor never restarts from zero

===========================
### 🎯 CORE PURPOSE OF THE APPLICATION
Build a web app that:
1. **Teaches DevOps tools step-by-step** using an AI mentor.
2. **Adapts learning to ADHD** (tiny steps, focus mode, minimal cognitive load).
3. **Generates practical exercises** (real tasks, testable, graded).
4. **Provides a dual-panel learning UI**:
   - Right side = AI instructor chat
   - Left side = learning material, code editor, exercises, tests, results
5. **Tracks every user struggle, weakness, confusion**, and uses them in future teaching.
6. **Has nodes (modules)** that the user can click on, but advanced ones require passing diagnostic exercises.
7. **Uses Claude code agent skills** to generate:
   - content
   - exercises
   - tests
   - explanations
   - progress logic
8. **Saves progress** in a DB so the user never restarts.

===========================
### 🧩 REQUIRED FEATURES (IMPLEMENT ALL)
- **Onboarding “Get to know each other” flow**  
  AI asks scientifically-informed questions about learning style, ADHD, goals (DevOps/SRE/Cloud/Cert), time availability, motivation, weaknesses.

- **Curriculum Planner**  
  AI generates a *node map* (learning graph) with modules like Terraform Basics, Pulumi Basics, Python Scripting, Bash Loops, Ansible Playbooks, etc.

- **Node Cards UI**
  Attractive cards showing duration, skill goals, progress, difficulty, prerequisites.

- **Exercise Engine**
  Generate exercises with:
  - prompt
  - test cases
  - auto-grader logic
  - hints
  - example solutions

- **Auto-Grader**
  Must evaluate:
  - Bash/Python scripts (run inside sandbox)
  - Pulumi code (run pulumi preview or localstack)
  - Terraform code (terraform plan + parse output)

- **Dual-Pane Layout**
  - Right: AI mentor conversation
  - Left: study pad (text, examples, code editor, diagrams, feedback)

- **ADHD Friendly**
  - step-by-step micro tasks
  - focus mode
  - panic/simplify button
  - progress tracking
  - break reminders

- **Memory System**
  Save:
  - progress
  - strengths/weaknesses
  - past misunderstandings
  - user preferences
  - attention patterns

===========================
### 🏗️ WHAT YOU MUST PRODUCE NOW
Generate a **complete engineering plan**, including:

1. **High-level system architecture**
   - frontend
   - backend
   - LLM agent orchestration
   - sandbox runners
   - vector memory
   - DB system
   - skills architecture

2. **Database schema**
   For:
   - users
   - learning nodes
   - exercises
   - attempts
   - memory
   - session logs
   - onboarding results

3. **API specification**
   - endpoints
   - request/response structures

4. **Frontend UI plan**
   - Component list
   - Dual-pane layout logic
   - Node cards
   - Editor, chat, grading results

5. **AI agent design**
   - skills
   - reasoning loops
   - memory retrieval
   - exercise generation templates
   - grading strategy

6. **Initial file/folder structure**
   For a production-quality project (full-stack).

7. **MVP implementation roadmap**
   - step-by-step timeline
   - priorities
   - what to build first

8. **Security model**
   - data privacy
   - safe execution
   - no real cloud resources unless explicit

===========================
### 🔥 VERY IMPORTANT
- Produce a **full, detailed plan** that a team of engineers can implement.
- The plan must include **diagrams or lists** describing agent workflows.
- Do NOT write actual code yet; we want architecture and planning first.
- The final output must be **complete, structured, and actionable**.

Begin.

