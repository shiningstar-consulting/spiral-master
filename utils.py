import streamlit as st
import json
from typing import Dict, Any

def initialize_session_state():
    """
    セッション状態の初期化
    """
    if "messages" not in st.session_state:
        st.session_state.messages = []
    
    if "api_endpoint" not in st.session_state:
        st.session_state.api_endpoint = "https://api.spiral-platform.com/v1"
    
    if "api_key" not in st.session_state:
        st.session_state.api_key = ""
    
    if "app_id" not in st.session_state:
        st.session_state.app_id = ""
    
    if "db_name" not in st.session_state:
        st.session_state.db_name = ""

def format_response(response: Dict[str, Any]) -> Dict[str, Any]:
    """
    APIレスポンスを見やすく整形
    """
    try:
        # 文字列の場合はJSONとしてパース
        if isinstance(response, str):
            try:
                response = json.loads(response)
            except json.JSONDecodeError:
                # JSON解析に失敗した場合は文字列としてそのまま扱う
                response = {"message": response}
        
        # 辞書でない場合は辞書に変換
        if not isinstance(response, dict):
            response = {"data": response}
        
        # エラーレスポンスの場合
        if "error" in response:
            return {
                "status": "error",
                "error": str(response["error"]),
                "details": str(response.get("details", "No additional details"))
            }
        
        # 待機レスポンスの場合
        if "status" in response and response["status"] == "waiting_input":
            return response
        
        # 成功レスポンスの場合
        return {
            "status": "success",
            "data": response.get("data", response)
        }
        
    except Exception as e:
        return {
            "status": "error",
            "error": f"Response formatting error: {str(e)}",
            "data": str(response)
        }
