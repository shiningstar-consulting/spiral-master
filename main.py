import streamlit as st
import json
import time
from code_generator import generate_spiral_code
from spiral_api import execute_code, SPIRALAPIExecutor
from utils import format_response, initialize_session_state

st.set_page_config(
    page_title="SPIRAL API Assistant",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded",
)

def add_message(role, content, code=None, response=None, is_final=False):
    """メッセージをセッションステートに追加するヘルパー関数"""
    msg = {"role": role, "content": content}
    if code:
        msg["code"] = code
    if response:
        msg["response"] = response
    if is_final:
        msg["is_final"] = True
    st.session_state.messages.append(msg)

def remove_final_messages():
    """最終メッセージを削除する（is_final=Trueのメッセージ）"""
    st.session_state.messages = [m for m in st.session_state.messages if not m.get("is_final")]

def display_messages():
    """セッション内のメッセージを表示"""
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.write(message["content"])
            if "code" in message:
                st.code(message["code"], language="python")
                if message.get("is_final"):
                    # 実行ボタンを表示
                    button_key = f"execute_{len(st.session_state.messages)}_{int(time.time())}"
                    execute_button = st.button("このコードを実行する", key=button_key, use_container_width=True)
                    
                    if execute_button:
                        with st.spinner("APIを実行中..."):
                            try:
                                # 実行前にセッション状態をクリア
                                executor = SPIRALAPIExecutor(st.session_state.api_endpoint, st.session_state.api_key)
                                st.session_state["executing"] = True
                                
                                # コードを実行
                                local_vars = {"st": st}
                                exec(message["code"], {"executor": executor, "st": st, "result": None}, local_vars)
                                response = local_vars.get("result")
                                
                                # セッション状態を更新
                                st.session_state.current_code = None
                                st.session_state.required_params = {}
                                st.session_state["executing"] = False
                                
                                # レスポンスを整形
                                formatted_response = format_response(response)
                                
                                # メッセージを更新
                                remove_final_messages()
                                add_message("assistant", "実行結果:", response=formatted_response)
                                
                                # 強制的にページを再読み込み
                                st.rerun()
                            except Exception as e:
                                st.error(f"実行エラー: {str(e)}")
            if "response" in message:
                st.json(message["response"])

def handle_new_prompt(prompt):
    """新しいプロンプトを処理"""
    with st.spinner("コードを生成中..."):
        try:
            generated_code = generate_spiral_code(prompt)
            st.session_state.current_code = generated_code
            
            # パラメータ入力が必要かどうかの静的チェック
            if "app_id" in generated_code or "db_name" in generated_code:
                if not st.session_state.get("app_id") and "app_id" in generated_code:
                    message = "アプリIDを入力してください。"
                    st.session_state.required_params = {"app_id": None}
                    add_message("assistant", message)
                    return
                if not st.session_state.get("db_name") and "db_name" in generated_code:
                    message = "データベース名を入力してください。自動生成する場合は「自動生成」と入力してください。"
                    st.session_state.required_params = {"db_name": None}
                    add_message("assistant", message)
                    return
            
            # すべてのパラメータが揃っている場合は実行確認
            add_message("assistant", "このコードを実行してよろしいですか？", code=generated_code, is_final=True)
            
        except Exception as e:
            st.error(f"コード生成エラー: {str(e)}")
            add_message("assistant", f"エラーが発生しました: {str(e)}")

def handle_param_input(prompt):
    """パラメータ入力を処理"""
    param_value = prompt.strip()
    
    if st.session_state.required_params:
        param_name = list(st.session_state.required_params.keys())[0]
        st.session_state[param_name] = param_value
        st.session_state.required_params = {}
        
        # パラメータ入力後の処理
        current_code = st.session_state.current_code
        if "app_id" in current_code and not st.session_state.get("db_name"):
            message = "データベース名を入力してください。自動生成する場合は「自動生成」と入力してください。"
            st.session_state.required_params = {"db_name": None}
            add_message("assistant", message)
        else:
            # すべてのパラメータが揃った場合は実行確認
            add_message("assistant", "このコードを実行してよろしいですか？", code=current_code, is_final=True)
        
        st.rerun()

def main():
    # 初期化
    if 'initialized' not in st.session_state:
        initialize_session_state()
        st.session_state.current_code = None
        st.session_state.required_params = {}
        st.session_state.messages = []
        st.session_state.initialized = True

    st.title("SPIRAL API アシスタント 🤖")

    # サイドバーにAPI設定
    with st.sidebar:
        st.header("API 設定")
        st.text_input("API エンドポイント", value=st.session_state.api_endpoint, key="api_endpoint")
        st.text_input("API キー", value=st.session_state.api_key, key="api_key", type="password")

    # チャット表示
    display_messages()

    # ユーザー入力
    prompt = st.chat_input("SPIRALで実行したい操作を入力してください")
    if prompt:
        add_message("user", prompt)
        
        if st.session_state.required_params:
            handle_param_input(prompt)
        else:
            handle_new_prompt(prompt)

if __name__ == "__main__":
    main()