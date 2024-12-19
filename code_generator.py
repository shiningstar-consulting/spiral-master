import json
import os
import streamlit as st
from openai import OpenAI
from typing import Dict, Any

# the newest OpenAI model is "gpt-4o" which was released May 13, 2024.
# do not change this unless explicitly requested by the user
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

def generate_spiral_code(prompt: str, existing_code: str = None) -> str:
    """
    Generate Python code to execute SPIRAL API based on user prompt
    If existing_code is provided, modify it according to the prompt
    """
    try:
        system_prompt = '''You are a SPIRAL API expert who generates Python code based on user requests to call the SPIRAL API.

フィールドタイプリファレンスは以下の通り
| フィールドタイプ名   | フィールドタイプ (API上での名称) | ストレージ計算容量 (bytes) |
|---------------------|--------------------------------|--------------------------|
| テキスト            | text                          | 128                      |
| テキストエリア      | textarea                      | 1024                     |
| メールアドレス      | email                         | 256                      |
| 電話番号            | phone                         | 19                       |
| 整数                | integer                       | 8                        |
| 数値                | double                        | 8                        |
| 日付                | date                          | 4                        |
| 月日                | monthDay                      | 4                        |
| 時刻                | time                          | 8                        |
| 日時                | dateTime                      | 8                        |
| セレクト            | select                        | 8                        |
| マルチセレクト      | multiselect                   | 125                      |
| 参照フィールド      | reference                     | 8                        |
| パスワード          | password                      | 128                      |
| ユーザフィールド    | user                          | 320                      |


Rules for code generation:
1. Generate pure Python code without any Markdown syntax or code block markers
2. Always start with "result = None"
3. Use executor.execute_request() for API calls
4. Include proper error handling with try-except
5. Generate complete, executable code
6. Use only ASCII characters in code
7. All messages to users must be in Japanese
8. Keep indentation consistent

Basic code structure for database operations:
result = None

if not st.session_state.get('app_id'):
    result = {
        "status": "waiting_input",
        "message": "アプリIDを入力してください。",
        "required_params": ["app_id"]
    }
elif not st.session_state.get('db_name'):
    result = {
        "status": "waiting_input",
        "message": "データベース名を入力してください。自動生成する場合は「自動生成」と入力してください。",
        "required_params": ["db_name"]
    }
else:
    try:
        db_name = st.session_state['db_name']
        app_id = st.session_state['app_id']
        if db_name == "自動生成":
            data = {
                "name": "members_db",
                "displayName": "会員データベース",
                "description": "会員情報を管理するデータベース",
                "fields": [
                    {"name": "member_id", "type": "text", "displayName": "会員ID", "required": True},
                    {"name": "name", "type": "text", "displayName": "名前", "required": True},
                    {"name": "email", "type": "email", "displayName": "メールアドレス", "required": True},
                    {"name": "phone", "type": "phone", "displayName": "電話番号", "required": False},
                    {"name": "address", "type": "textarea", "displayName": "住所", "required": False},
                    {"name": "join_date", "type": "date", "displayName": "入会日", "required": True}
                ]
            }
        else:
            data = {
                "name": db_name,
                "displayName": f"{db_name}",
                "description": f"{db_name}のデータを管理するデータベース"
            }
        
        response = executor.execute_request(
            method="POST",
            path=f"apps/{app_id}/dbs",
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