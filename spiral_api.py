import requests
import json
from typing import Dict, Any
import ast
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SPIRALAPIExecutor:
    def __init__(self, endpoint: str, api_key: str):
        self.endpoint = endpoint
        self.api_key = api_key
        self.session = requests.Session()
        self.session.headers.update({
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        })

    def execute_request(self, method: str, path: str, data: Dict[str, Any] = None) -> Dict[str, Any]:
        url = f"{self.endpoint.rstrip('/')}/{path.lstrip('/')}"
        
        try:
            logger.info(f"Executing {method} request to {url}")
            if data:
                logger.info(f"Request data: {json.dumps(data, indent=2)}")

            response = self.session.request(
                method=method,
                url=url,
                json=data if data else None
            )
            
            response.raise_for_status()
            return response.json()

        except requests.exceptions.RequestException as e:
            logger.error(f"API request failed: {str(e)}")
            if hasattr(e.response, 'text'):
                logger.error(f"Response text: {e.response.text}")
            raise Exception(f"API request failed: {str(e)}")

def execute_code(code: str, endpoint: str, api_key: str) -> Dict[str, Any]:
    """
    Generated codeを実行し、結果を返す
    """
    try:
        # コードの安全性チェック
        ast.parse(code)
        
        # 実行環境の準備
        executor = SPIRALAPIExecutor(endpoint, api_key)
        
        # ローカル環境を準備
        local_env = {
            "executor": executor,
            "requests": requests,
            "json": json
        }
        
        # コードの実行
        exec(code, local_env)
        
        # 実行結果を取得
        if "result" in local_env:
            return local_env["result"]
        else:
            raise Exception("コードの実行結果が見つかりません。'result'変数に結果を代入してください。")
            
    except SyntaxError as e:
        raise Exception(f"コードの構文エラー: {str(e)}")
    except Exception as e:
        raise Exception(f"コードの実行エラー: {str(e)}")
