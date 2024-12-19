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
        if isinstance(response, str):
            response = json.loads(response)
        
        # エラーレスポンスの場合
        if isinstance(response, dict) and "error" in response:
            return {
                "status": "error",
                "error": response["error"],
                "details": response.get("details", "No additional details")
            }
        
        # 成功レスポンスの場合
        return {
            "status": "success",
            "data": response
        }
        
    except json.JSONDecodeError:
        return {
            "status": "error",
            "error": "Invalid JSON response",
            "raw_response": response
        }
    except Exception as e:
        return {
            "status": "error",
            "error": f"Response formatting error: {str(e)}",
            "raw_response": response
        }
