import streamlit as st
import base64
import sys
from pathlib import Path

# 프로젝트 루트 경로를 sys.path에 추가 (ui/ 상위가 루트)
ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.append(str(ROOT_DIR))

from rag.chatbot import JobisChatbot

# ---------------------------
# Title with Logo
# ---------------------------
def load_image_base64(path):
    with open(path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode()

STATIC_DIR = Path(__file__).resolve().parents[1] / "static" / "logo.png"
logo_base64 = load_image_base64(STATIC_DIR)

st.markdown(
    f"""
    <div style="display: flex; align-items: center; gap: 10px; margin-bottom:20px;">
        <img src="data:image/png;base64,{logo_base64}" width="45">
        <h2 style="margin: 0;">Jobis</h2>
    </div>
    """,
    unsafe_allow_html=True
)

# ---------------------------
# Chat Styling
# ---------------------------
bubble_style = """
<style>
.user-bubble {
    background-color: #33DA6E;
    color: #000;
    padding: 10px 15px;
    border-radius: 12px;
    max-width: 70%;
    margin-bottom: 10px;
    display: inline-block;
}
.bot-bubble {
    background-color: #E8E8E8;
    color: black;
    padding: 10px 15px;
    border-radius: 12px;
    max-width: 70%;
    margin-bottom: 10px;
    display: inline-block;
}
.chat-row {
    display: flex;
    width: 100%;
    margin-bottom: 5px;
}
.user-row {
    justify-content: flex-end;
}
.bot-row {
    justify-content: flex-start;
}
</style>
"""
st.markdown(bubble_style, unsafe_allow_html=True)

# ---------------------------
# Session State Init
# ---------------------------
if "messages" not in st.session_state:
    st.session_state.messages = []

if "chatbot" not in st.session_state:
    st.session_state.chatbot = JobisChatbot()

# ---------------------------
# Display Chat Messages
# ---------------------------
for msg in st.session_state.messages:
    role = msg["role"]
    content = msg["content"]

    if role == "user":
        st.markdown(
            f"""
            <div class="chat-row user-row">
                <div class="user-bubble">{content}</div>
            </div>
            """,
            unsafe_allow_html=True
        )
    else:
        st.markdown(
            f"""
            <div class="chat-row bot-row">
                <div class="bot-bubble">{content}</div>
            </div>
            """,
            unsafe_allow_html=True
        )

# ---------------------------
# User Input
# ---------------------------
user_input = st.chat_input("질문을 입력하세요")

# 글자가 하나씩 출력되는 애니메이션(streaming)
def stream_answer(text):
    import time
    for char in text:
        yield char
        time.sleep(0.02)  # 속도 조절 가능

if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})

    # 사용자 메시지 출력
    st.markdown(
        f"""
        <div class="chat-row user-row">
            <div class="user-bubble">{user_input}</div>
        </div>
        """,
        unsafe_allow_html=True
    )

    # ---- RAG 호출 + 스피너 ----
    with st.spinner("Jobis 생각 중..."):
        bot_response = st.session_state.chatbot.ask(user_input)

    # 메시지 저장
    st.session_state.messages.append({"role": "assistant", "content": bot_response})

    # ---- 스트리밍 출력 ----
    with st.chat_message("assistant"):
        st.write_stream(stream_answer(bot_response))