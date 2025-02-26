import streamlit as st
import requests
import logging
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime

# 設置日誌
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('chat.log'),
        logging.StreamHandler()
    ]
)

# Ollama API 設置
OLLAMA_API_BASE = "http://localhost:11434"

def get_available_models():
    """獲取可用的模型列表"""
    try:
        response = requests.get(f"{OLLAMA_API_BASE}/api/tags")
        if response.status_code == 200:
            models = [model['name'] for model in response.json()['models']]
            logging.info(f"獲取到的模型列表: {models}")
            return models
        logging.error(f"獲取模型列表失敗: HTTP {response.status_code}")
        return []
    except Exception as e:
        logging.error(f"無法獲取模型列表: {str(e)}")
        st.error(f"無法獲取模型列表: {str(e)}")
        return []

def chat_with_model(model: str, prompt: str) -> str:
    """與選定的模型對話"""
    try:
        logging.info(f"開始與模型 {model} 對話")
        logging.info(f"用戶輸入: {prompt}")
        
        response = requests.post(
            f"{OLLAMA_API_BASE}/api/generate",
            json={
                "model": model,
                "prompt": prompt,
                "stream": False
            }
        )
        
        if response.status_code == 200:
            result = response.json()['response']
            logging.info(f"模型 {model} 回應: {result[:100]}...")  # 只記錄前100個字符
            return result
            
        logging.error(f"模型回應錯誤: HTTP {response.status_code}")
        return f"錯誤: {response.status_code}"
    except Exception as e:
        error_msg = f"與模型 {model} 對話時發生錯誤: {str(e)}"
        logging.error(error_msg)
        return f"錯誤: {str(e)}"

st.set_page_config(
    page_title="LLM Chat",
    page_icon="💬",
    layout="wide"
)

st.title("LLM Chat Interface")

# 初始化聊天歷史
if "messages" not in st.session_state:
    st.session_state.messages = []

# 側邊欄：模型選擇
with st.sidebar:
    st.title("設置")
    available_models = get_available_models()
    if available_models:
        selected_model = st.selectbox(
            "選擇模型",
            available_models,
            index=0 if available_models else None
        )
    else:
        st.error("無法獲取模型列表。請確保 Ollama 服務正在運行。")
        selected_model = None

    # 文件上傳功能
    uploaded_file = st.file_uploader("上傳文件", type=["txt", "pdf", "doc", "docx"])
    if uploaded_file is not None:
        st.success(f"文件 '{uploaded_file.name}' 上傳成功！")
        # TODO: 實現文件處理邏輯

# 顯示聊天歷史
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 聊天輸入
if prompt := st.chat_input("輸入您的訊息..."):
    if not selected_model:
        st.error("請先選擇一個模型")
        logging.warning("使用者嘗試在未選擇模型的情況下發送訊息")
    else:
        # 添加用戶訊息
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # 獲取模型回應
        with st.spinner('思考中...'):
            response = chat_with_model(selected_model, prompt)

        # 添加助手回應
        st.session_state.messages.append({"role": "assistant", "content": response})
        with st.chat_message("assistant"):
            st.markdown(response)

class Message(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    messages: List[Message]
    context: Optional[str] = None

class ChatResponse(BaseModel):
    response: str
    sources: Optional[List[str]] = None
