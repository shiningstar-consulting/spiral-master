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

def main():
    # セッション状態の初期化
    if 'initialized' not in st.session_state:
        initialize_session_state()
        st.session_state.current_code = None
        st.session_state.required_params = {}
        st.session_state.messages = []
        st.session_state.show_execute_button = False
        st.session_state.final_code = None
        st.session_state.initialized = True
    
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
    
    # チャットインターフェースの設定
    st.header("チャット")
    
    # メッセージを分類
    regular_messages = []
    final_message = None
    
    for message in st.session_state.messages:
        if message.get("is_final"):
            final_message = message
        else:
            regular_messages.append(message)
    
    # 通常のメッセージを表示
    for message in regular_messages:
        with st.chat_message(message["role"]):
            st.write(message["content"])
            if "code" in message:
                st.code(message["code"], language="python")
            if "response" in message:
                st.json(message["response"])
    
    # 最終メッセージを表示（実行ボタン付き）
    if final_message:
        with st.chat_message(final_message["role"]):
            st.write(final_message["content"])
            if "code" in final_message:
                st.code(final_message["code"], language="python")
                button_key = f"execute_{len(st.session_state.messages)}_{int(time.time())}"
                if st.button("このコードを実行する", key=button_key):
                    with st.spinner("APIを実行中..."):
                        try:
                            executor = SPIRALAPIExecutor(st.session_state.api_endpoint, st.session_state.api_key)
                            local_vars = {"st": st}
                            exec(final_message["code"], {"executor": executor, "st": st, "result": None}, local_vars)
                            response = local_vars.get("result")
                            
                            # レスポンスを整形
                            formatted_response = format_response(response)
                            
                            # 最終メッセージを削除して新しいメッセージを追加
                            st.session_state.messages = [m for m in st.session_state.messages if not m.get("is_final")]
                            st.session_state.messages.append({
                                "role": "assistant",
                                "content": "実行が完了しました。",
                                "response": formatted_response
                            })
                            
                            st.experimental_rerun()
                        except Exception as e:
                            st.error(f"実行エラー: {str(e)}")
    
    # ユーザー入力
    if prompt := st.chat_input("SPIRALに実行したい操作を入力してください"):
        # ユーザーのメッセージを表示
        with st.chat_message("user"):
            st.markdown(prompt)
            st.session_state.messages.append({"role": "user", "content": prompt})

        # パラメータ入力または修正要求の場合
        if st.session_state.current_code and prompt.strip():
            # アシスタントの応答を生成
            with st.chat_message("assistant"):
                try:
                    if 'params' not in st.session_state:
                        st.session_state.params = {}
                    
                    # パラメータの保存
                    if st.session_state.required_params:
                        param_name = list(st.session_state.required_params.keys())[0]
                        param_value = prompt.strip()
                        st.session_state[param_name] = param_value
                        st.session_state.params[param_name] = param_value
                    
                    # 変数の初期化
                    updated_code = st.session_state.current_code
                    modified_code = None

                    if st.session_state.required_params:
                        # パラメータ入力の処理
                        param_name = list(st.session_state.required_params.keys())[0]
                        st.session_state.params[param_name] = prompt.strip()
                        
                        # コード内のプレースホルダーを実際の値で置換
                        for param, value in st.session_state.params.items():
                            updated_code = updated_code.replace(f'"{param}"', f'"{value}"')
                        
                        # まだ必要なパラメータが残っているか確認
                        st.session_state.required_params.pop(param_name)
                        if st.session_state.required_params:
                            next_param = list(st.session_state.required_params.keys())[0]
                            st.session_state.messages = [m for m in st.session_state.messages if not m.get("is_final")]
                            st.session_state.messages.append({
                                "role": "assistant",
                                "content": f"{next_param}を入力してください。"
                            })
                        else:
                            st.session_state.messages = [m for m in st.session_state.messages if not m.get("is_final")]
                            st.session_state.messages.append({
                                "role": "assistant",
                                "content": "全てのパラメータが入力されました。このコードを実行してよろしいですか？",
                                "code": updated_code,
                                "is_final": True
                            })
                    else:
                        # 修正要求の処理
                        modified_code = generate_spiral_code(prompt)
                        st.session_state.messages.append({
                            "role": "assistant",
                            "content": "コードを修正しました。このコードを実行してよろしいですか？",
                            "code": modified_code,
                            "is_final": True
                        })
                    
                    # 現在のコードを更新
                    st.session_state.current_code = modified_code if modified_code is not None else updated_code
                    
                    # コードの生成と表示のみを行う
                    try:
                        current_code = st.session_state.current_code
                        
                        # 既存の最終メッセージを削除
                        st.session_state.messages = [m for m in st.session_state.messages if not m.get("is_final")]
                        
                        # パラメータ入力が必要かどうかの静的チェック
                        if "app_id" in current_code and not st.session_state.get("app_id"):
                            message = "アプリIDを入力してください。"
                            st.info(message)
                            st.session_state.required_params = {"app_id": None}
                            st.session_state.messages.append({
                                "role": "assistant",
                                "content": message
                            })
                        elif "db_name" in current_code and not st.session_state.get("db_name"):
                            message = "データベース名を入力してください。"
                            st.info(message)
                            st.session_state.required_params = {"db_name": None}
                            st.session_state.messages.append({
                                "role": "assistant",
                                "content": message
                            })
                        else:
                            # すべてのパラメータが揃っている場合、実行準備完了
                            st.session_state.messages.append({
                                "role": "assistant",
                                "content": "全てのパラメータが入力されました。このコードを実行してよろしいですか？",
                                "code": current_code,
                                "is_final": True
                            })
                            
                    except Exception as e:
                        st.error(f"コードの検証中にエラーが発生しました: {str(e)}")
                        st.session_state.messages.append({
                            "role": "assistant",
                            "content": f"エラーが発生しました: {str(e)}"
                        })
                except Exception as e:
                    st.error(f"エラーが発生しました: {str(e)}")
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": f"エラーが発生しました: {str(e)}"
                    })
        
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
                    
                    # コードの検証
                    executor = SPIRALAPIExecutor(st.session_state.api_endpoint, st.session_state.api_key)
                    test_vars = {}
                    exec(generated_code, {"executor": executor, "result": None}, test_vars)
                    response = test_vars.get("result")
                    
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
                        # コードの準備完了
                        st.session_state.show_execute_button = True
                        st.session_state.final_code = generated_code
                        st.session_state.messages.append({
                            "role": "assistant",
                            "content": "コードの準備ができました。実行してよろしいですか？",
                            "code": generated_code,
                            "is_final": True
                        })
                    
                except Exception as e:
                    st.error(f"エラーが発生しました: {str(e)}")
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": f"エラーが発生しました: {str(e)}"
                    })

if __name__ == "__main__":
    main()