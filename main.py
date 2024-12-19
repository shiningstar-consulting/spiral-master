import streamlit as st
import json
from code_generator import generate_spiral_code
from spiral_api import execute_code, SPIRALAPIExecutor
from utils import format_response, initialize_session_state

st.set_page_config(
    page_title="SPIRAL API Assistant",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded",
)

def main():
    initialize_session_state()
    
    if 'current_code' not in st.session_state:
        st.session_state.current_code = None
    if 'required_params' not in st.session_state:
        st.session_state.required_params = {}
    
    st.title("SPIRAL API アシスタント 🤖")
    
    # サイドバーにAPI設定を表示
    with st.sidebar:
        st.header("API 設定")
        st.text_input("API エンドポイント", 
                     value=st.session_state.api_endpoint,
                     key="api_endpoint",
                     help="SPIRAL APIのエンドポイントを入力してください")
        st.text_input("API キー", 
                     value=st.session_state.api_key,
                     key="api_key", 
                     type="password",
                     help="SPIRAL APIキーを入力してください")
    
    # メインエリアにチャットインターフェースを表示
    st.header("チャット")
    
    # チャット履歴の表示
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            if "code" in message:
                st.code(message["code"], language="python")
            if "response" in message:
                if isinstance(message["response"], dict):
                    st.json(message["response"])
                else:
                    st.text(message["response"])

    # ユーザー入力
    if prompt := st.chat_input("SPIRALに実行したい操作を入力してください"):
        # ユーザーのメッセージを表示
        with st.chat_message("user"):
            st.markdown(prompt)
            st.session_state.messages.append({"role": "user", "content": prompt})

        # パラメータ入力の場合
        if st.session_state.current_code and prompt.strip():
            param_name = list(st.session_state.required_params.keys())[0]
            st.session_state.required_params[param_name] = prompt.strip()
            
            # アシスタントの応答を生成
            with st.chat_message("assistant"):
                try:
                    # SPIRALAPIExecutorのインスタンスを作成
                    executor = SPIRALAPIExecutor(st.session_state.api_endpoint, st.session_state.api_key)
                    # コードを実行
                    exec(f"{param_name} = '{prompt.strip()}'", globals())
                    local_vars = {}
                    exec(st.session_state.current_code, {"executor": executor, "result": None}, local_vars)
                    response = local_vars.get("result")
                    
                    # レスポンスの処理
                    if isinstance(response, dict) and response.get("status") == "waiting_input":
                        # まだ追加のパラメータが必要な場合
                        message = response.get("message", "追加の入力が必要です")
                        st.info(message)
                        st.session_state.required_params = {p: None for p in response.get("required_params", [])}
                        st.session_state.messages.append({
                            "role": "assistant",
                            "content": message
                        })
                    else:
                        # 実行完了
                        formatted_response = format_response(response)
                        st.markdown("### 実行結果:")
                        st.json(formatted_response)
                        st.session_state.current_code = None
                        st.session_state.required_params = {}
                        st.session_state.messages.append({
                            "role": "assistant",
                            "content": "処理が完了しました。",
                            "response": formatted_response
                        })
                        
                except Exception as e:
                    st.error(f"エラーが発生しました: {str(e)}")
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": f"エラーが発生しました: {str(e)}"
                    })
                    st.session_state.current_code = None
                    st.session_state.required_params = {}
        
        # 新しいコマンドの場合
        else:
            # アシスタントの応答を生成
            with st.chat_message("assistant"):
                try:
                    # コード生成中のスピナー表示
                    with st.spinner("コードを生成中..."):
                        generated_code = generate_spiral_code(prompt)
                    
                    st.markdown("生成されたコードです:")
                    st.code(generated_code, language="python")
                    
                    # コード実行
                    with st.spinner("APIを実行中..."):
                        # SPIRALAPIExecutorのインスタンスを作成
                        executor = SPIRALAPIExecutor(st.session_state.api_endpoint, st.session_state.api_key)
                        # 生成されたコードをローカル変数として実行
                        local_vars = {}
                        exec(generated_code, {"executor": executor, "result": None}, local_vars)
                        response = local_vars.get("result")
                    
                    # レスポンスの処理
                    if isinstance(response, dict) and response.get("status") == "waiting_input":
                        # パラメータ入力が必要な場合
                        message = response.get("message", "追加の入力が必要です")
                        st.info(message)
                        st.session_state.current_code = generated_code
                        st.session_state.required_params = {p: None for p in response.get("required_params", [])}
                        st.session_state.messages.append({
                            "role": "assistant",
                            "content": message,
                            "code": generated_code
                        })
                    else:
                        # 実行完了
                        formatted_response = format_response(response)
                        st.markdown("### 実行結果:")
                        st.json(formatted_response)
                        st.session_state.messages.append({
                            "role": "assistant",
                            "content": "処理が完了しました。",
                            "code": generated_code,
                            "response": formatted_response
                        })
                    
                except Exception as e:
                    st.error(f"エラーが発生しました: {str(e)}")
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": f"エラーが発生しました: {str(e)}"
                    })

if __name__ == "__main__":
    main()
