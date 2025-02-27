import pandas as pd
import networkx as nx
from typing import List, Dict, Any
import logging
from pathlib import Path
import chromadb
from sentence_transformers import SentenceTransformer
import numpy as np

class GraphRAG:
    def __init__(self, embedding_model: str = "all-MiniLM-L6-v2"):
        self.graph = nx.Graph()
        self.embedder = SentenceTransformer(embedding_model)
        
        # 确保数据目录存在
        chroma_path = Path("./data/chroma_db")
        chroma_path.mkdir(parents=True, exist_ok=True)
        
        # 初始化 ChromaDB 客户端
        self.chroma_client = chromadb.PersistentClient(
            path=str(chroma_path)
        )
        
        # 删除现有集合（如果存在）并创建新的
        try:
            self.chroma_client.delete_collection(name="csv_collection")
        except:
            pass
            
        self.collection = self.chroma_client.create_collection(
            name="csv_collection",
            metadata={"hnsw:space": "cosine"}
        )

    def process_csv(self, csv_path: str) -> None:
        """处理CSV文件并构建知识图谱"""
        encodings = ['utf-8', 'gbk', 'big5', 'gb18030']
        
        # 清除现有的图和向量存储
        self.graph.clear()
        try:
            self.collection.delete(ids=self.collection.get()["ids"])
        except:
            pass
        
        for encoding in encodings:
            try:
                df = pd.read_csv(csv_path, encoding=encoding)
                logging.info(f"Successfully read CSV file with {encoding} encoding")
                break
            except UnicodeDecodeError:
                if encoding == encodings[-1]:
                    raise Exception(f"無法讀取CSV文件，嘗試過的編碼：{', '.join(encodings)}")
                continue
            except Exception as e:
                raise Exception(f"讀取CSV文件時發生錯誤：{str(e)}")
        
        try:
            # 收集所有要添加的文档和嵌入
            documents = []
            embeddings = []
            ids = []
            metadatas = []
            
            # 为每一行创建节点
            for idx, row in df.iterrows():
                node_id = f"row_{idx}"
                self.graph.add_node(node_id, **row.to_dict())
                
                # 为每个非空的列值创建关系
                for col in df.columns:
                    if pd.notna(row[col]):
                        # 创建列值节点
                        value_node = f"{col}_{row[col]}"
                        self.graph.add_node(value_node, value=row[col], type=col)
                        # 添加边
                        self.graph.add_edge(node_id, value_node, relation=col)
                
                # 存储向量表示
                text_representation = " ".join(str(v) for v in row if pd.notna(v))
                embedding = self.embedder.encode(text_representation)
                
                documents.append(text_representation)
                embeddings.append(embedding.tolist())
                ids.append(node_id)
                metadatas.append({"row_id": node_id, **row.to_dict()})
            
            # 批量添加到 ChromaDB
            if documents:
                self.collection.add(
                    documents=documents,
                    embeddings=embeddings,
                    metadatas=metadatas,
                    ids=ids
                )
            
            logging.info(f"Successfully processed CSV file and built knowledge graph with {self.graph.number_of_nodes()} nodes")
            
        except Exception as e:
            logging.error(f"Error processing CSV file: {str(e)}")
            raise

    def query(self, query: str, k: int = 3) -> Dict[str, Any]:
        """执行混合查询：结合向量相似度和图结构"""
        try:
            # 1. 向量相似度搜索
            query_embedding = self.embedder.encode(query)
            results = self.collection.query(
                query_embeddings=[query_embedding.tolist()],
                n_results=k
            )
            
            # 2. 获取相关节点的图上下文
            relevant_nodes = []
            for idx, node_id in enumerate(results['ids'][0]):
                # 获取节点的邻居
                neighbors = list(self.graph.neighbors(node_id))
                subgraph = self.graph.subgraph([node_id] + neighbors)
                
                # 构建上下文
                context = {
                    'node': dict(self.graph.nodes[node_id]),
                    'neighbors': [dict(self.graph.nodes[n]) for n in neighbors],
                    'score': results['distances'][0][idx]
                }
                relevant_nodes.append(context)
            
            return {
                'query': query,
                'relevant_contexts': relevant_nodes
            }
            
        except Exception as e:
            logging.error(f"Error during query: {str(e)}")
            raise

    def get_graph_statistics(self) -> Dict[str, Any]:
        """获取知识图谱的统计信息"""
        return {
            'num_nodes': self.graph.number_of_nodes(),
            'num_edges': self.graph.number_of_edges(),
            'node_types': len(set(nx.get_node_attributes(self.graph, 'type').values())),
            'is_connected': nx.is_connected(self.graph)
        }
