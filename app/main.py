import streamlit as st
from typing import List, Optional
from pydantic import BaseModel

st.set_page_config(
    page_title="LLM Chat",
    page_icon="💬",
    layout="wide"
)

st.title("LLM Chat Interface")

# 初始化聊天歷史
if "messages" not in st.session_state:
    st.session_state.messages = []

# 顯示聊天歷史
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 聊天輸入
if prompt := st.chat_input("輸入您的訊息..."):
    # 添加用戶訊息
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # TODO: 在這裡實現RAG邏輯
    response = "這是一個測試回應。RAG功能即將實現。"

    # 添加助手回應
    st.session_state.messages.append({"role": "assistant", "content": response})
    with st.chat_message("assistant"):
        st.markdown(response)

# 文件上傳功能
uploaded_file = st.sidebar.file_uploader("上傳文件", type=["txt", "pdf", "doc", "docx"])
if uploaded_file is not None:
    st.sidebar.success(f"文件 '{uploaded_file.name}' 上傳成功！")
    # TODO: 實現文件處理邏輯

class Message(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    messages: List[Message]
    context: Optional[str] = None

class ChatResponse(BaseModel):
    response: str
    sources: Optional[List[str]] = None
