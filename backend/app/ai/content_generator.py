"""
Content Generator for Pre-Generated Course Content
Generates complete course content (lectures + exercises) upfront to reduce costs
"""
from typing import List, Dict, Optional
from anthropic import AsyncAnthropic
from motor.motor_asyncio import AsyncIOMotorDatabase
from bson import ObjectId
from datetime import datetime
import json
import re

from app.config import get_settings

settings = get_settings()


def safe_json_parse(text: str) -> Dict:
    """
    Safely parse JSON with repair for common AI generation issues
    """
    # Try direct parse first
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass

    # Try to repair common issues
    repaired = text

    # Fix unterminated strings by ensuring balanced quotes
    # Remove any trailing incomplete content after last complete object/array
    try:
        # Find the last complete JSON structure
        brace_count = 0
        bracket_count = 0
        last_valid_pos = 0

        for i, char in enumerate(repaired):
            if char == '{':
                brace_count += 1
            elif char == '}':
                brace_count -= 1
                if brace_count == 0 and bracket_count == 0:
                    last_valid_pos = i + 1
            elif char == '[':
                bracket_count += 1
            elif char == ']':
                bracket_count -= 1
                if brace_count == 0 and bracket_count == 0:
                    last_valid_pos = i + 1

        if last_valid_pos > 0:
            repaired = repaired[:last_valid_pos]
            return json.loads(repaired)
    except:
        pass

    # Last resort: return a minimal valid structure
    print(f"⚠️ JSON repair failed, returning fallback structure")
    return {
        "title": "Content Generation Error",
        "introduction": "Content is being generated. Please try again.",
        "sections": [],
        "summary": "Content generation encountered an issue."
    }


LECTURE_STRUCTURE_PROMPT = """
Generate a comprehensive lecture with these mandatory sections:

1. **Introduction** (2-3 paragraphs)
   - What is this concept?
   - Why is it important?
   - Real-world analogy

2. **Core Concepts** (3-5 subsections)
   - Break down into smallest teachable units
   - Each concept: definition → example → code demo
   - Build progressively (simple → complex)

3. **Hands-On Examples** (3-4 examples)
   - Interactive code snippets user can run
   - Show input/output
   - Explain line-by-line

4. **Common Mistakes** (2-3 mistakes)
   - Show incorrect code
   - Explain why it's wrong
   - Show correction

5. **Summary & Next Steps**
   - Recap key points (bulleted)
   - "Ready to practice? Let's start with beginner exercises."

CRITICAL: Ensure concepts are taught BEFORE any exercise is introduced.
"""


EXERCISE_GENERATION_PROMPT = """
Generate {num_exercises} progressive exercises for this topic:

Requirements:
- Exercise 1: Beginner - Basic concept application
- Exercise 2: Intermediate - Combine multiple concepts
- Exercise 3: Advanced - Real-world scenario (if needed)

For each exercise, provide:
1. Title (concise, descriptive)
2. Description (what skill is being taught)
3. Prompt (clear instructions for student)
4. **Starter code**: SCAFFOLDING ONLY - function signatures, TODO comments, structure. DO NOT include solution logic!
   Example:
   ```
   def calculate_sum(a, b):
       # TODO: Implement the sum calculation
       pass
   ```
5. **Solution**: Complete working code with full implementation
   Example:
   ```
   def calculate_sum(a, b):
       return a + b
   ```
6. Test cases (at least 2-3 validation tests)
7. Hints (3 levels: conceptual → specific → pseudocode)

CRITICAL: starter_code and solution MUST BE DIFFERENT. Starter code provides structure, solution provides implementation.

Format as JSON array with this exact structure:
[
  {{
    "title": "Exercise Title",
    "description": "What skill this teaches",
    "prompt": "Clear instructions",
    "starter_code": "// Scaffolding only, NO solution",
    "solution": "// Complete working code",
    "test_cases": [
      {{
        "test_id": "test_1",
        "description": "Test description",
        "input": {{}},
        "expected_output": {{"stdout": "expected"}},
        "validation_script": "validation code"
      }}
    ],
    "hints": [
      {{"level": 1, "hint": "Conceptual hint"}},
      {{"level": 2, "hint": "Specific hint"}},
      {{"level": 3, "hint": "Pseudocode hint"}}
    ]
  }}
]
"""


async def generate_full_course_content(
    db: AsyncIOMotorDatabase,
    user_id: str,
    path_id: str,
    path_description: str,
    target_nodes: List[Dict],
    user_profile: Dict
) -> Dict:
    """
    Generate all content for a learning path in one batch operation

    Flow:
    1. Use Claude Opus (high quality) to design course outline
    2. For each node in path:
       - Generate lecture content (sections with theory, examples, code demos)
       - Generate 3-5 progressive exercises (beginner → intermediate → advanced)
       - Generate hints for each exercise
    3. Store all in MongoDB with path_id reference
    4. Return summary of generated content

    Cost: ~$2-3 for complete path (10-15 nodes)
    Saves: ~$0.17 * (number of sessions) = $8.50 savings after 50 sessions

    Args:
        db: MongoDB database connection
        user_id: User ID for personalization
        path_id: Learning path identifier
        path_description: Description of the learning path
        target_nodes: List of node documents to generate content for
        user_profile: User profile for personalization

    Returns:
        Dict with summary: {success, nodes_generated, total_exercises, message}
    """
    client = AsyncAnthropic(api_key=settings.ANTHROPIC_API_KEY)

    # If no nodes provided, fetch from database
    if not target_nodes:
        cursor = db.learning_nodes.find({"node_id": {"$regex": f"^{path_id}"}})
        target_nodes = await cursor.to_list(length=100)

    if not target_nodes:
        return {
            "success": False,
            "message": f"No nodes found for path: {path_id}"
        }

    print(f"🎓 Starting bulk content generation for path: {path_id}")
    print(f"   Target: {len(target_nodes)} nodes")
    print(f"   User: {user_id}")

    generated_count = 0
    total_exercises = 0
    errors = []

    # Process nodes in batches of 3 to avoid token limits
    batch_size = 3
    for i in range(0, len(target_nodes), batch_size):
        batch = target_nodes[i:i + batch_size]
        print(f"\n📦 Processing batch {i//batch_size + 1}/{(len(target_nodes)-1)//batch_size + 1}")

        for node in batch:
            try:
                node_id = node["node_id"]
                print(f"   🔨 Generating content for: {node_id}")

                # Generate lecture content
                lecture = await generate_lecture_content(
                    client=client,
                    node=node,
                    user_profile=user_profile
                )

                # Generate exercises for this node
                exercises = await generate_exercises_for_node(
                    client=client,
                    node=node,
                    user_profile=user_profile,
                    num_exercises=3
                )

                # Store in course_content collection
                content_doc = {
                    "path_id": path_id,
                    "node_id": node_id,
                    "user_id": user_id,
                    "content_version": 1,
                    "lecture": lecture,
                    "exercises": exercises,
                    "generated_at": datetime.utcnow(),
                    "last_accessed": None,
                    "access_count": 0
                }

                # Upsert to allow regeneration
                await db.course_content.update_one(
                    {"node_id": node_id, "user_id": user_id},
                    {"$set": content_doc},
                    upsert=True
                )

                generated_count += 1
                total_exercises += len(exercises)
                print(f"   ✅ Generated {len(exercises)} exercises for {node_id}")

            except Exception as e:
                error_msg = f"Failed to generate content for {node.get('node_id', 'unknown')}: {str(e)}"
                print(f"   ❌ {error_msg}")
                errors.append(error_msg)

    # Summary
    success = generated_count > 0
    message = f"✅ Generated content for {generated_count}/{len(target_nodes)} nodes ({total_exercises} exercises total)"

    if errors:
        message += f"\n⚠️ {len(errors)} errors encountered"

    print(f"\n🎉 Bulk generation complete!")
    print(f"   {message}")

    return {
        "success": success,
        "nodes_generated": generated_count,
        "total_exercises": total_exercises,
        "errors": errors,
        "message": message
    }


async def generate_lecture_content(
    client: AsyncAnthropic,
    node: Dict,
    user_profile: Dict
) -> Dict:
    """
    Generate structured lecture content for a single node

    Args:
        client: Anthropic API client
        node: Node document with title, description, concepts
        user_profile: User learning style and preferences

    Returns:
        Dict with lecture structure: {title, introduction, sections, summary}
    """
    # Build context from node metadata
    node_title = node.get("title", "")
    node_description = node.get("description", "")
    concepts = node.get("skills_taught", node.get("content", {}).get("concepts", []))
    learning_objectives = node.get("content", {}).get("learning_objectives", [])

    # Personalization based on user profile
    learning_style = user_profile.get("learning_style", "mixed")
    experience_level = user_profile.get("experience_level", "beginner")

    style_guidance = {
        "hands_on": "Focus heavily on code examples and interactive demos. Minimal theory.",
        "read_first": "Provide thorough explanations before examples. More conceptual depth.",
        "mixed": "Balance theory and practice. Interleave explanations with examples."
    }.get(learning_style, "Balance theory and practice.")

    # Generate lecture using Claude Opus (high quality)
    prompt = f"""You are an expert programming instructor creating a comprehensive lecture.

Topic: {node_title}
Description: {node_description}
Concepts to cover: {', '.join(concepts) if concepts else 'Core fundamentals'}
Learning Objectives: {', '.join(learning_objectives) if learning_objectives else 'Master the basics'}

Student Profile:
- Experience Level: {experience_level}
- Learning Style: {learning_style}
- Style Guidance: {style_guidance}

{LECTURE_STRUCTURE_PROMPT}

Return your response as a JSON object with this structure:
{{
  "title": "Lecture title",
  "introduction": "2-3 paragraph introduction as markdown",
  "sections": [
    {{
      "heading": "Section title",
      "body": "Detailed explanation as markdown",
      "code_examples": [
        {{
          "language": "python|javascript|bash",
          "code": "actual code here",
          "explanation": "what this code does"
        }}
      ]
    }}
  ],
  "summary": "Key takeaways as bulleted markdown"
}}

IMPORTANT: Generate COMPLETE, DETAILED content. This will be saved and reused.
"""

    response = await client.messages.create(
        model="claude-opus-4-20250514",  # Use Opus for highest quality
        max_tokens=4096,
        messages=[{"role": "user", "content": prompt}]
    )

    # Parse JSON response
    content_text = response.content[0].text

    # Extract JSON from response (may be wrapped in markdown code blocks)
    if "```json" in content_text:
        content_text = content_text.split("```json")[1].split("```")[0].strip()
    elif "```" in content_text:
        content_text = content_text.split("```")[1].split("```")[0].strip()

    lecture = safe_json_parse(content_text)

    # Add next_steps
    lecture["next_steps"] = "Ready to practice? Let's apply what you've learned with some exercises!"

    return lecture


async def generate_exercises_for_node(
    client: AsyncAnthropic,
    node: Dict,
    user_profile: Dict,
    num_exercises: int = 3
) -> List[Dict]:
    """
    Generate progressive exercises for a node

    Args:
        client: Anthropic API client
        node: Node document
        user_profile: User preferences
        num_exercises: Number of exercises to generate (default 3)

    Returns:
        List of exercise documents
    """
    node_title = node.get("title", "")
    node_description = node.get("description", "")
    node_id = node.get("node_id", "")

    # Determine exercise type from node_id prefix
    exercise_type = "python"  # default
    if "js-" in node_id or "javascript-" in node_id:
        exercise_type = "javascript"
    elif "bash-" in node_id:
        exercise_type = "bash"
    elif "go-" in node_id:
        exercise_type = "go"
    elif "terraform-" in node_id:
        exercise_type = "terraform"

    prompt = f"""Generate {num_exercises} progressive exercises for this topic.

Topic: {node_title}
Description: {node_description}
Exercise Type: {exercise_type}

{EXERCISE_GENERATION_PROMPT}

Return as a JSON array of exercises.
"""

    response = await client.messages.create(
        model="claude-opus-4-20250514",
        max_tokens=4096,
        messages=[{"role": "user", "content": prompt}]
    )

    content_text = response.content[0].text

    # Extract JSON
    if "```json" in content_text:
        content_text = content_text.split("```json")[1].split("```")[0].strip()
    elif "```" in content_text:
        content_text = content_text.split("```")[1].split("```")[0].strip()

    exercises_data = safe_json_parse(content_text)
    # Ensure it's a list
    if isinstance(exercises_data, dict):
        exercises_data = [exercises_data]

    # Format exercises with proper IDs
    exercises = []
    for idx, ex_data in enumerate(exercises_data):
        exercise_id = f"{node_id}-ex{idx+1}"

        # Ensure test_cases format
        test_cases = ex_data.get("test_cases", [])
        formatted_tests = []
        for test in test_cases:
            formatted_tests.append({
                "test_id": test.get("test_id", f"test_{idx+1}"),
                "description": test.get("description", "Test case"),
                "input": test.get("input", {}),
                "expected_output": test.get("expected_output", {"stdout": ""}),
                "validation_script": test.get("validation_script", "# Validation")
            })

        exercises.append({
            "exercise_id": exercise_id,
            "title": ex_data["title"],
            "description": ex_data.get("description", ""),
            "prompt": ex_data["prompt"],
            "difficulty": ex_data.get("difficulty", ["beginner", "intermediate", "advanced"][idx]),
            "starter_code": ex_data.get("starter_code", "# Your code here"),
            "solution": ex_data["solution"],
            "test_cases": formatted_tests,
            "hints": ex_data.get("hints", [])
        })

    return exercises


async def generate_single_node_content(
    db: AsyncIOMotorDatabase,
    user_id: str,
    node_id: str
) -> Dict:
    """
    Fallback: Generate content for a single node on-demand
    Used when pre-generated content doesn't exist

    Args:
        db: MongoDB database
        user_id: User ID
        node_id: Node to generate content for

    Returns:
        Course content document
    """
    # Fetch node
    node = await db.learning_nodes.find_one({"node_id": node_id})
    if not node:
        raise ValueError(f"Node not found: {node_id}")

    # Fetch user profile
    user_profile = await db.user_profiles.find_one({"user_id": user_id}) or {}

    # Extract path_id from node_id (e.g., "python-variables" -> "python")
    path_id = node_id.split("-")[0] if "-" in node_id else node_id

    client = AsyncAnthropic(api_key=settings.ANTHROPIC_API_KEY)

    print(f"⚠️ Fallback: Generating on-demand content for {node_id}")

    # Generate lecture
    lecture = await generate_lecture_content(client, node, user_profile)

    # Generate exercises
    exercises = await generate_exercises_for_node(client, node, user_profile, num_exercises=2)

    # Store for future use
    content_doc = {
        "path_id": path_id,
        "node_id": node_id,
        "user_id": user_id,
        "content_version": 1,
        "lecture": lecture,
        "exercises": exercises,
        "generated_at": datetime.utcnow(),
        "last_accessed": datetime.utcnow(),
        "access_count": 1
    }

    await db.course_content.insert_one(content_doc)

    return content_doc


async def generate_targeted_exercise(
    db: AsyncIOMotorDatabase,
    user_id: str,
    node_id: str,
    focus_topics: List[str],
    difficulty: str = "intermediate",
    context: str = "remedial"
) -> Dict:
    """
    Generate a single targeted exercise focused on specific weak points

    Args:
        db: MongoDB database
        user_id: User ID
        node_id: Associated node
        focus_topics: Topics to focus on (weak points)
        difficulty: Exercise difficulty
        context: "remedial" or "practice"

    Returns:
        Exercise document
    """
    client = AsyncAnthropic(api_key=settings.ANTHROPIC_API_KEY)

    # Fetch node for context
    node = await db.learning_nodes.find_one({"node_id": node_id})
    node_title = node.get("title", "") if node else node_id

    prompt = f"""Generate a single focused exercise to address these weak points:

Topic: {node_title}
Weak Points to Address: {', '.join(focus_topics)}
Difficulty: {difficulty}
Context: {context}

Requirements:
- Focus specifically on the weak point topics
- Simpler than regular exercises
- Provide more scaffolding in starter code
- Include helpful comments and TODO markers
- Generate 3 progressive hints

Return as JSON object (not array).
"""

    response = await client.messages.create(
        model="claude-3-5-sonnet-20241022",  # Use Sonnet for speed
        max_tokens=2048,
        messages=[{"role": "user", "content": prompt}]
    )

    content_text = response.content[0].text
    if "```json" in content_text:
        content_text = content_text.split("```json")[1].split("```")[0].strip()

    exercise_data = safe_json_parse(content_text)

    # Format with proper ID
    exercise_id = f"{node_id}-remedial-{str(ObjectId())}"

    return {
        "exercise_id": exercise_id,
        "node_id": node_id,
        "title": exercise_data["title"],
        "description": exercise_data.get("description", ""),
        "prompt": exercise_data["prompt"],
        "type": "python",  # TODO: infer from node
        "difficulty": difficulty,
        "starter_code": exercise_data.get("starter_code", ""),
        "solution": exercise_data["solution"],
        "test_cases": exercise_data.get("test_cases", []),
        "hints": exercise_data.get("hints", []),
        "grading_rubric": {
            "correctness_weight": 1.0,
            "style_weight": 0.0,
            "efficiency_weight": 0.0
        },
        "generated_by_ai": True,
        "created_for_user": user_id,
        "created_at": datetime.utcnow(),
        "context": context,
        "focus_topics": focus_topics
    }
