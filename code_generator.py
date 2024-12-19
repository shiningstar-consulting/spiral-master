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
        system_prompt = """
あなたはSPIRAL APIの専門家です。ユーザーの要望に基づいて、SPIRAL APIを呼び出すPythonコードを生成してください。

以下の規則に従ってください：
1. executor.execute_request() メソッドを使用してAPIを呼び出す
2. 結果は必ず'result'変数に代入する
3. エラーハンドリングを適切に行う
4. パラメータが不足している場合は、st.text_input()やst.selectbox()を使用してユーザーに入力を求める
5. コードは完全な形で、実行可能である必要がある
6. レスポンスは適切に整形する

# 必要なパラメータをユーザーに確認するコード例：
app_id = st.text_input("アプリIDを入力してください")
if not app_id:
    result = {
        "status": "waiting_input",
        "message": "アプリIDが必要です"
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

# 複数のパラメータが必要な場合のコード例：
db_id = st.text_input("データベースIDを入力してください")
record_id = st.text_input("レコードIDを入力してください")

if not db_id or not record_id:
    result = {
        "status": "waiting_input",
        "message": "データベースIDとレコードIDが必要です"
    }
    return

try:
    response = executor.execute_request(
        method="GET",
        path=f"apps/{app_id}/dbs/{db_id}/records/{record_id}",
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
"""
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
