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

    # 初始化 GraphRAG
    if "graph_rag" not in st.session_state:
        from graph_rag import GraphRAG
        st.session_state.graph_rag = GraphRAG()

    # 文件上傳功能
    uploaded_file = st.file_uploader("上傳CSV文件", type=["csv"])
    if uploaded_file is not None:
        try:
            # 保存上传的文件
            import tempfile
            import os
            
            with tempfile.NamedTemporaryFile(delete=False, suffix='.csv') as tmp_file:
                tmp_file.write(uploaded_file.getvalue())
                tmp_path = tmp_file.name
            
            # 处理CSV文件
            st.session_state.graph_rag.process_csv(tmp_path)
            
            # 获取图谱统计信息
            stats = st.session_state.graph_rag.get_graph_statistics()
            st.success(f"文件 '{uploaded_file.name}' 處理成功！")
            st.info(f"知識圖譜統計：\n- 節點數：{stats['num_nodes']}\n- 邊數：{stats['num_edges']}\n- 節點類型數：{stats['node_types']}")
            
            # 删除临时文件
            os.unlink(tmp_path)
            
        except Exception as e:
            st.error(f"處理文件時發生錯誤：{str(e)}")

# 顯示聊天歷史
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 聊天輸入
if prompt := st.chat_input("輸入您的訊息..."):
    # 添加用户消息到历史记录
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # 检查是否已上传并处理了CSV文件
    if "graph_rag" in st.session_state:
        try:
            # 使用GraphRAG进行查询
            rag_results = st.session_state.graph_rag.query(prompt)
            
            # 构建带有上下文的提示
            context = "基於以下相關信息回答：\n"
            for ctx in rag_results['relevant_contexts']:
                context += f"- 主要信息：{ctx['node']}\n"
                context += f"- 相關信息：{', '.join(str(n) for n in ctx['neighbors'])}\n"
            
            enhanced_prompt = f"{context}\n用戶問題：{prompt}"
            
        except Exception as e:
            st.error(f"查詢知識圖譜時發生錯誤：{str(e)}")
            enhanced_prompt = prompt
    else:
        enhanced_prompt = prompt

    # 获取模型回应
    if selected_model:
        with st.chat_message("assistant"):
            response = chat_with_model(selected_model, enhanced_prompt)
            st.session_state.messages.append({"role": "assistant", "content": response})
            st.markdown(response)
    else:
        st.error("請先選擇一個模型")

class Message(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    messages: List[Message]
    context: Optional[str] = None

class ChatResponse(BaseModel):
    response: str
    sources: Optional[List[str]] = None
