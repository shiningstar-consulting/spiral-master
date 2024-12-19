import json
import os
from openai import OpenAI
from typing import Dict, Any

# the newest OpenAI model is "gpt-4o" which was released May 13, 2024.
# do not change this unless explicitly requested by the user
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

def generate_spiral_code(prompt: str) -> str:
    """
    ユーザーのプロンプトからSPIRAL APIを実行するPythonコードを生成
    """
    try:
        system_prompt = """You are a SPIRAL API expert. Generate Python code based on user requests to call the SPIRAL API.

Follow these rules:
1. Use executor.execute_request() method to call the API
2. Always assign results to the 'result' variable
3. Include proper error handling
4. If parameters are missing, return a message in the result variable
5. Code must be complete and executable
6. Format responses appropriately
7. Use only ASCII characters in the generated code

Example code for handling missing parameters:
```python
# Example 1: Single parameter check
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
    result = {
        "status": "success",
        "data": response
    }
except Exception as e:
    result = {
        "status": "error",
        "error": str(e)
    }
```

Example code for multiple parameters:
```python
# Example 2: Multiple parameter check
if 'app_id' not in globals():
    result = {
        "status": "waiting_input",
        "message": "Please enter the App ID",
        "required_params": ["app_id"]
    }
    return

if 'db_id' not in globals():
    result = {
        "status": "waiting_input",
        "message": "Please enter the Database ID",
        "required_params": ["db_id"]
    }
    return

try:
    response = executor.execute_request(
        method="GET",
        path=f"apps/{app_id}/dbs/{db_id}",
        data=None
    )
    result = {
        "status": "success",
        "data": response
    }
except Exception as e:
    result = {
        "status": "error",
        "error": str(e)
    }
```"""
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
        raise Exception(f"コード生成に失敗しました: {str(e)}")
