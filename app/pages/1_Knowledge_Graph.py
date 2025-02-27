import streamlit as st
import networkx as nx
from pyvis.network import Network
import tempfile
from pathlib import Path
import json
import os
from io import StringIO

st.set_page_config(page_title="Knowledge Graph Visualization", page_icon="🕸️", layout="wide")
st.title("知識圖譜可視化")

def visualize_graph(graph):
    # 创建一个 pyvis 网络对象
    net = Network(height="600px", width="100%", bgcolor="#ffffff", font_color="black")
    
    # 配置物理布局
    net.force_atlas_2based()
    
    # 添加节点和边
    for node in graph.nodes():
        # 获取节点属性
        node_attrs = graph.nodes[node]
        # 确定节点颜色（行节点和值节点使用不同颜色）
        color = "#ff9999" if node.startswith("row_") else "#99ff99"
        # 创建节点标签
        if "value" in node_attrs:
            label = f"{node_attrs['type']}: {node_attrs['value']}"
        else:
            label = f"Row {node.split('_')[1]}"
        # 添加节点
        net.add_node(node, label=label, title=json.dumps(node_attrs, ensure_ascii=False), color=color)
    
    # 添加边
    for edge in graph.edges():
        source, target = edge
        edge_data = graph.get_edge_data(source, target)
        net.add_edge(source, target, title=edge_data.get('relation', ''))
    
    # 生成HTML内容
    try:
        # 创建临时目录（如果不存在）
        temp_dir = Path("temp_graph")
        temp_dir.mkdir(exist_ok=True)
        
        # 使用固定的临时文件名
        temp_file = temp_dir / "graph.html"
        
        # 保存图谱
        net.save_graph(str(temp_file))
        
        # 读取生成的HTML内容
        html_content = temp_file.read_text(encoding='utf-8')
        
        # 删除临时文件
        temp_file.unlink(missing_ok=True)
        
        return html_content
    except Exception as e:
        st.error(f"生成圖譜時發生錯誤：{str(e)}")
        return None

# 检查是否已有图谱数据
if "graph_rag" in st.session_state and st.session_state.graph_rag.graph.number_of_nodes() > 0:
    graph = st.session_state.graph_rag.graph
    
    # 显示图谱统计信息
    st.sidebar.title("圖譜統計")
    stats = st.session_state.graph_rag.get_graph_statistics()
    st.sidebar.info(f"""
    - 節點數：{stats['num_nodes']}
    - 邊數：{stats['num_edges']}
    - 節點類型數：{stats['node_types']}
    - 是否連通：{'是' if stats['is_connected'] else '否'}
    """)
    
    # 添加过滤选项
    st.sidebar.title("過濾選項")
    
    # 获取所有节点类型
    node_types = set()
    for node, attrs in graph.nodes(data=True):
        if 'type' in attrs:
            node_types.add(attrs['type'])
    
    # 创建类型过滤器
    selected_types = st.sidebar.multiselect(
        "選擇節點類型",
        list(node_types),
        default=list(node_types)
    )
    
    # 根据选择过滤图
    filtered_graph = graph.copy()
    nodes_to_remove = []
    for node, attrs in graph.nodes(data=True):
        if 'type' in attrs and attrs['type'] not in selected_types:
            nodes_to_remove.append(node)
    filtered_graph.remove_nodes_from(nodes_to_remove)
    
    # 可视化图谱
    html_content = visualize_graph(filtered_graph)
    st.components.v1.html(html_content, height=600)
    
    # 添加下载按钮
    st.download_button(
        label="下載圖譜HTML",
        data=html_content,
        file_name="knowledge_graph.html",
        mime="text/html"
    )
    
else:
    st.warning("尚未上傳或處理CSV文件。請先在主頁上傳並處理CSV文件。")
