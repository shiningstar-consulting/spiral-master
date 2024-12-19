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
        # Noneの場合
        if response is None:
            return {
                "status": "success",
                "data": None
            }
            
        # 文字列の場合
        if isinstance(response, str):
            return {
                "status": "success",
                "data": response
            }
            
        # 辞書以外の場合
        if not isinstance(response, dict):
            return {
                "status": "success",
                "data": response
            }
        
        # エラーレスポンスの場合
        if "error" in response:
            return {
                "status": "error",
                "error": str(response["error"])
            }
        
        # 待機レスポンスの場合
        if response.get("status") == "waiting_input":
            return {
                "status": "waiting_input",
                "message": response.get("message", "入力待ち"),
                "required_params": response.get("required_params", [])
            }
        
        # 通常のレスポンスの場合
        return {
            "status": "success",
            "data": response
        }
        
    except Exception as e:
        return {
            "status": "error",
            "error": str(e)
        }
