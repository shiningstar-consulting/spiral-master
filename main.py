import streamlit as st
import json
from code_generator import generate_spiral_code
from spiral_api import execute_code
from utils import format_response, initialize_session_state

st.set_page_config(
    page_title="SPIRAL API Assistant",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded",
)

def main():
    initialize_session_state()
    
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
                st.json(message["response"])

    # ユーザー入力
    if prompt := st.chat_input("SPIRALに実行したい操作を入力してください"):
        # ユーザーのメッセージを表示
        with st.chat_message("user"):
            st.markdown(prompt)
            st.session_state.messages.append({"role": "user", "content": prompt})

        # アシスタントの応答を生成
        with st.chat_message("assistant"):
            # コード生成中のスピナー表示
            with st.spinner("コードを生成中..."):
                generated_code = generate_spiral_code(prompt)
            
            st.markdown("生成されたコードです:")
            st.code(generated_code, language="python")

            # 実行ボタン
            if st.button("コードを実行", key="execute"):
                try:
                    with st.spinner("APIを実行中..."):
                        response = execute_code(
                            generated_code,
                            st.session_state.api_endpoint,
                            st.session_state.api_key
                        )
                    
                    # レスポンスの整形と表示
                    formatted_response = format_response(response)
                    st.markdown("### 実行結果:")
                    st.json(formatted_response)
                    
                    # チャット履歴に保存
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": "コードを生成し実行しました。",
                        "code": generated_code,
                        "response": formatted_response
                    })
                    
                except Exception as e:
                    st.error(f"エラーが発生しました: {str(e)}")
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": f"エラーが発生しました: {str(e)}",
                        "code": generated_code
                    })

if __name__ == "__main__":
    main()
