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
        """
        SPIRAL APIリクエストを実行
        
        Args:
            method: HTTPメソッド
            path: APIパス
            data: リクエストデータ（オプション）
            
        Returns:
            Dict[str, Any]: APIレスポンス
            
        Raises:
            Exception: APIリクエストが失敗した場合
        """
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
            
            # レスポンスの詳細なログ
            logger.info(f"Response status code: {response.status_code}")
            logger.info(f"Response headers: {dict(response.headers)}")
            
            try:
                response_data = response.json()
                logger.info(f"Response data: {json.dumps(response_data, indent=2)}")
            except json.JSONDecodeError:
                logger.warning(f"Non-JSON response: {response.text}")
                raise Exception("Invalid JSON response from API")
            
            response.raise_for_status()
            return response_data

        except requests.exceptions.RequestException as e:
            error_message = f"API request failed: {str(e)}"
            if hasattr(e, 'response') and e.response is not None:
                try:
                    error_detail = e.response.json()
                    error_message = f"{error_message}\nAPI Error: {json.dumps(error_detail, indent=2)}"
                except json.JSONDecodeError:
                    error_message = f"{error_message}\nResponse text: {e.response.text}"
            
            logger.error(error_message)
            raise Exception(error_message)
        except Exception as e:
            logger.error(f"Unexpected error: {str(e)}")
            raise

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
        local_vars = {}
        
        # コードを実行
        exec(code, {"executor": executor, "result": None}, local_vars)
        
        # 実行結果を取得
        if "result" in local_vars:
            return local_vars["result"]
        else:
            raise Exception("実行結果が見つかりません。コードに問題がある可能性があります。")
            
    except SyntaxError as e:
        raise Exception(f"コードの構文エラー: {str(e)}")
    except Exception as e:
        raise Exception(f"コードの実行エラー: {str(e)}")
