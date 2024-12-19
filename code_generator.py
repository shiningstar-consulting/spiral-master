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
        system_prompt = '''You are a SPIRAL API expert. Generate Python code based on user requests to call the SPIRAL API.

Follow these rules:
1. Use executor.execute_request() method to call the API
2. Always start with result = None
3. Include proper error handling with try-except
4. If parameters are missing, return a message in the result variable
5. Generate complete, executable code without any special characters or comments
6. Use only ASCII characters
7. No fancy formatting or docstrings
8. Keep indentation simple and consistent

Here is the exact format to follow:

result = None
if 'parameter' not in globals():
    result = {
        "status": "waiting_input",
        "message": "Enter parameter",
        "required_params": ["parameter"]
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

Example code for handling missing parameters:
result = None
if 'app_id' not in globals():
    result = {
        "status": "waiting_input",
        "message": "Please enter the App ID",
        "required_params": ["app_id"]
    }
    return

try:
    response = executor.execute_request(
        method="GET",
        path=f"apps/{app_id}",
        data=None
    )
    result = {"status": "success", "data": response}
except Exception as e:
    result = {"status": "error", "error": str(e)}
'''
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