import json
import os
from openai import OpenAI
from typing import Dict, Any

# the newest OpenAI model is "gpt-4o" which was released May 13, 2024.
# do not change this unless explicitly requested by the user
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

def generate_spiral_code(prompt: str) -> str:
    """
    Generate Python code to execute SPIRAL API based on user prompt
    """
    try:
        system_prompt = '''You are a SPIRAL API expert who generates Python code based on user requests to call the SPIRAL API.

Follow these rules:
1. Use executor.execute_request() method to call the API
2. Always start with result = None
3. Include proper error handling with try-except
4. When parameters are needed, provide two options:
   - If user wants to specify parameters: Ask for specific parameters with clear Japanese descriptions
   - If user wants automatic generation: Generate sample parameters with realistic values
5. All user messages should be in Japanese
6. Generate complete, executable code without special characters
7. Use only ASCII characters in code (Japanese is only allowed in messages)
8. Keep indentation simple and consistent

Example format for parameter requests:

result = None
if 'db_name' not in globals():
    result = {
        "status": "waiting_input",
        "message": "データベース名を入力してください。自動生成する場合は「自動生成」と入力してください。",
        "required_params": ["db_name"]
    }
else:
    try:
        response = executor.execute_request(
            method="METHOD",
            path="path/to/api",
            data={"key": "value"}
        )
        result = {"status": "success", "data": response}
    except Exception as e:
        result = {"status": "error", "error": str(e)}

Example code for handling parameters with auto-generation option:

# For database creation
result = None
if 'db_name' not in globals():
    result = {
        "status": "waiting_input",
        "message": "データベース名を入力してください。自動生成する場合は「自動生成」と入力してください。",
        "required_params": ["db_name"]
    }
    return

try:
    # Handle auto-generation case
    if db_name == "自動生成":
        data = {
            "name": "members_db",
            "displayName": "会員データベース",
            "description": "会員情報を管理するデータベース"
        }
    else:
        data = {
            "name": db_name,
            "displayName": f"{db_name}データベース",
            "description": f"{db_name}のデータを管理するデータベース"
        }
    
    response = executor.execute_request(
        method="POST",
        path="apps/dbs",
        data=data
    )
    result = {"status": "success", "data": response}
except Exception as e:
    result = {"status": "error", "error": str(e)}'''
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt}
        ]

        response = client.chat.completions.create(
            model="gpt-4o",
            messages=messages,
            temperature=0.7,
            max_tokens=1500
        )

        return response.choices[0].message.content

    except Exception as e:
        raise Exception(f"Code generation failed: {str(e)}")