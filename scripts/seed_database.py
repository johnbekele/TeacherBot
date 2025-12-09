"""
Seed database with initial learning nodes and exercises
"""
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime

# MongoDB connection
MONGODB_URL = "mongodb://localhost:27017"
DB_NAME = "myteacher"


async def seed_database():
    """Seed the database with initial data"""
    client = AsyncIOMotorClient(MONGODB_URL)
    db = client[DB_NAME]

    print("🌱 Seeding database...")

    # Clear existing data
    await db.learning_nodes.delete_many({})
    await db.exercises.delete_many({})

    # Seed learning nodes
    nodes = [
        {
            "node_id": "python-basics",
            "title": "Python Basics",
            "description": "Learn fundamental Python programming concepts",
            "category": "python",
            "difficulty": "beginner",
            "estimated_duration": 120,
            "prerequisites": [],
            "skills_taught": ["variables", "loops", "functions", "data types"],
            "status": "available",
            "content": {
                "introduction": "Python is a versatile programming language used in DevOps automation.",
                "concepts": [
                    "Variables and data types",
                    "Control flow (if/else)",
                    "Loops (for, while)",
                    "Functions and modules"
                ],
                "practical_applications": [
                    "Writing automation scripts",
                    "Processing configuration files",
                    "Building CLI tools"
                ]
            },
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        },
        {
            "node_id": "bash-scripting",
            "title": "Bash Scripting Fundamentals",
            "description": "Master shell scripting for Linux automation",
            "category": "bash",
            "difficulty": "beginner",
            "estimated_duration": 90,
            "prerequisites": [],
            "skills_taught": ["shell commands", "variables", "conditionals", "loops"],
            "status": "available",
            "content": {
                "introduction": "Bash scripting is essential for Linux automation and DevOps workflows.",
                "concepts": [
                    "Shell commands",
                    "Variables and environment",
                    "Conditionals and loops",
                    "Functions and scripts"
                ],
                "practical_applications": [
                    "Server provisioning",
                    "Deployment automation",
                    "System monitoring"
                ]
            },
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        },
        {
            "node_id": "terraform-basics",
            "title": "Terraform Basics",
            "description": "Infrastructure as Code with Terraform",
            "category": "terraform",
            "difficulty": "intermediate",
            "estimated_duration": 180,
            "prerequisites": ["bash-scripting"],
            "skills_taught": ["HCL", "resources", "providers", "state management"],
            "status": "available",
            "content": {
                "introduction": "Terraform enables infrastructure as code for cloud platforms.",
                "concepts": [
                    "Terraform configuration language (HCL)",
                    "Resources and providers",
                    "Variables and outputs",
                    "State management"
                ],
                "practical_applications": [
                    "Provisioning cloud infrastructure",
                    "Managing AWS/Azure/GCP resources",
                    "Infrastructure versioning"
                ]
            },
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
    ]

    result = await db.learning_nodes.insert_many(nodes)
    print(f"✅ Inserted {len(result.inserted_ids)} learning nodes")

    # Seed exercises
    exercises = [
        {
            "exercise_id": "python-hello-world",
            "node_id": "python-basics",
            "title": "Hello World in Python",
            "description": "Write your first Python program",
            "type": "python",
            "difficulty": "beginner",
            "prompt": "Write a Python function called `greet()` that prints 'Hello, World!' to the console.",
            "starter_code": "def greet():\n    # Your code here\n    pass",
            "solution": "def greet():\n    print('Hello, World!')",
            "hints": [
                {
                    "hint_number": 1,
                    "text": "Use the print() function to output text",
                    "reveal_after_attempts": 1
                },
                {
                    "hint_number": 2,
                    "text": "The string should be enclosed in quotes",
                    "reveal_after_attempts": 2
                }
            ],
            "test_cases": [
                {
                    "test_id": "test_1",
                    "description": "Function prints 'Hello, World!'",
                    "input": {},
                    "expected_output": {"stdout": "Hello, World!\n"},
                    "validation_script": "greet()"
                }
            ],
            "grading_rubric": {
                "correctness_weight": 0.8,
                "style_weight": 0.1,
                "efficiency_weight": 0.1
            },
            "created_at": datetime.utcnow()
        },
        {
            "exercise_id": "bash-echo",
            "node_id": "bash-scripting",
            "title": "Echo Command",
            "description": "Use the echo command to print text",
            "type": "bash",
            "difficulty": "beginner",
            "prompt": "Write a bash script that prints 'DevOps is awesome!' using the echo command.",
            "starter_code": "#!/bin/bash\n# Your code here",
            "solution": "#!/bin/bash\necho 'DevOps is awesome!'",
            "hints": [
                {
                    "hint_number": 1,
                    "text": "Use the echo command followed by the text in quotes",
                    "reveal_after_attempts": 1
                }
            ],
            "test_cases": [
                {
                    "test_id": "test_1",
                    "description": "Script prints correct text",
                    "input": {},
                    "expected_output": {"stdout": "DevOps is awesome!\n"},
                    "validation_script": "bash script.sh"
                }
            ],
            "grading_rubric": {
                "correctness_weight": 1.0,
                "style_weight": 0.0,
                "efficiency_weight": 0.0
            },
            "created_at": datetime.utcnow()
        }
    ]

    result = await db.exercises.insert_many(exercises)
    print(f"✅ Inserted {len(result.inserted_ids)} exercises")

    print("🎉 Database seeded successfully!")
    client.close()


if __name__ == "__main__":
    asyncio.run(seed_database())
