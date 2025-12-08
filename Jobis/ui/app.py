import streamlit as st
import base64

# ---------------------------
# Title with Logo
# ---------------------------
def load_image_base64(path):
    with open(path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode()

logo_base64 = load_image_base64("./static/logo.png")

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

if user_input:
    # Save user message
    st.session_state.messages.append({"role": "user", "content": user_input})

    # Display user message
    st.markdown(
        f"""
        <div class="chat-row user-row">
            <div class="user-bubble">{user_input}</div>
        </div>
        """,
        unsafe_allow_html=True
    )

    # ---- RAG 호출 위치 ----
    bot_response = "여기에 RAG 기반 챗봇 응답이 들어갑니다."

    # Save bot response
    st.session_state.messages.append({"role": "assistant", "content": bot_response})

    # Display bot message
    st.markdown(
        f"""
        <div class="chat-row bot-row">
            <div class="bot-bubble">{bot_response}</div>
        </div>
        """,
        unsafe_allow_html=True
    )