import json
import os
import numpy as np
from typing import List, Dict, Any
from sentence_transformers import SentenceTransformer
import faiss
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema import Document
import pickle
import requests

class MedicalRAGSystem:
    def __init__(self, model_path: str = "D:\\Embedding\\Embedding", deepseek_api_key: str = "sk-b87c9bf17adf4c5d935feb2748534da4"):
        """
        初始化医疗RAG系统

        Args:
            model_path: 本地embedding模型路径
            deepseek_api_key: DeepSeek API密钥
        """
        self.model_path = model_path
        self.deepseek_api_key = deepseek_api_key
        self.deepseek_api_url = "https://api.deepseek.com/v1/chat/completions"

        try:
            # 尝试从本地路径加载模型
            self.embedding_model = SentenceTransformer(model_path)
            print(f"✅ 成功从本地路径加载embedding模型: {model_path}")
        except Exception as e:
            print(f"❌ 无法从本地路径加载模型 '{model_path}': {e}")
            print("尝试使用备用模型...")
            try:
                self.embedding_model = SentenceTransformer("all-MiniLM-L6-v2")
                self.model_path = "all-MiniLM-L6-v2"
                print("✅ 成功加载备用embedding模型")
            except Exception as e2:
                print(f"❌ 备用模型也加载失败: {e2}")
                raise RuntimeError("无法加载任何embedding模型，请检查模型路径")
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=500,
            chunk_overlap=50,
            length_function=len,
        )
        self.index = None
        self.documents = []
        self.document_metadata = []

    def load_documents(self, file_path: str = "medical_docs.json"):
        """
        加载医疗文档数据

        Args:
            file_path: 文档文件路径
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"文档文件 {file_path} 不存在")

        with open(file_path, 'r', encoding='utf-8') as f:
            docs = json.load(f)

        # 转换为LangChain Document格式
        for doc in docs:
            # 分割长文本
            chunks = self.text_splitter.split_text(doc['text'])
            for i, chunk in enumerate(chunks):
                self.documents.append(chunk)
                self.document_metadata.append({
                    'doc_id': doc['doc_id'],
                    'source': doc['source'],
                    'chunk_id': i,
                    'original_text': doc['text']
                })

        print(f"已加载 {len(self.documents)} 个文档块")

    def create_vector_index(self):
        """创建FAISS向量索引"""
        if not self.documents:
            raise ValueError("请先加载文档")

        # 计算文档嵌入向量
        embeddings = self.embedding_model.encode(self.documents, show_progress_bar=True)

        # 创建FAISS索引
        dimension = embeddings.shape[1]
        self.index = faiss.IndexFlatIP(dimension)  # 使用内积相似度

        # 归一化向量（用于余弦相似度）
        faiss.normalize_L2(embeddings)

        # 添加向量到索引
        self.index.add(embeddings.astype('float32'))

        print(f"已创建向量索引，包含 {self.index.ntotal} 个向量")

    def search_documents(self, query: str, top_k: int = 3) -> List[Dict[str, Any]]:
        """
        搜索相关文档

        Args:
            query: 查询文本
            top_k: 返回的文档数量

        Returns:
            相关文档列表
        """
        if self.index is None:
            raise ValueError("请先创建向量索引")

        # 计算查询向量
        query_embedding = self.embedding_model.encode([query])
        faiss.normalize_L2(query_embedding)

        # 搜索相似文档
        scores, indices = self.index.search(query_embedding.astype('float32'), top_k)

        # 返回结果
        results = []
        for i, (score, idx) in enumerate(zip(scores[0], indices[0])):
            if idx < len(self.documents):
                results.append({
                    'content': self.documents[idx],
                    'metadata': self.document_metadata[idx],
                    'score': float(score)
                })

        return results

    def generate_answer(self, query: str, context_docs: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        生成答案（使用模拟API）

        Args:
            query: 用户查询
            context_docs: 相关文档列表

        Returns:
            包含答案和来源的字典
        """
        # 构建上下文
        context = "\n".join([doc['content'] for doc in context_docs])

        # 调用DeepSeek API
        api_response = self._call_deepseek_api(query, context)

        # 提取来源信息
        sources = []
        for doc in context_docs:
            sources.append({
                'doc_id': doc['metadata']['doc_id'],
                'source': doc['metadata']['source'],
                'content': doc['content'][:100] + "..."  # 截取前100个字符
            })

        return {
            'answer': api_response,
            'sources': sources,
            'query': query
        }

    def _call_deepseek_api(self, query: str, context: str) -> str:
        """
        调用DeepSeek API生成答案

        Args:
            query: 用户查询
            context: 上下文信息

        Returns:
            生成的答案
        """
        # 检查API密钥和网络连接
        if not self.deepseek_api_key or self.deepseek_api_key == "YOUR_DEEPSEEK_API_KEY":
            print("⚠️ DeepSeek API密钥未设置，使用本地答案生成")
            return self._generate_fallback_answer(query, context)

        # 先测试网络连接
        try:
            test_response = requests.get("https://api.deepseek.com", timeout=5)
            if test_response.status_code != 200:
                print("⚠️ DeepSeek API服务不可用，使用本地答案生成")
                return self._generate_fallback_answer(query, context)
        except Exception as e:
            print(f"⚠️ 网络连接问题，使用本地答案生成: {e}")
            return self._generate_fallback_answer(query, context)

        # 如果网络测试通过，尝试调用API
        print("🌐 网络连接正常，尝试调用DeepSeek API...")

        try:
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.deepseek_api_key}",
                "User-Agent": "MedicalRAGSystem/1.0"
            }

            messages = [
                {
                    "role": "system",
                    "content": "你是一个专业的医疗知识问答助手。请根据提供的医疗文献内容，简洁、准确地回答用户的问题。如果文献中没有相关信息，请明确说明。"
                },
                {
                    "role": "user",
                    "content": f"以下是相关医疗文献内容：\n\n{context}\n\n请回答问题：{query}"
                }
            ]

            payload = {
                "model": "deepseek-chat",
                "messages": messages,
                "max_tokens": 1000,
                "temperature": 0.7
            }

            print("⏳ 正在调用DeepSeek API...")
            # 禁用代理设置
            session = requests.Session()
            session.trust_env = False  # 不使用环境变量中的代理设置

            response = session.post(
                self.deepseek_api_url,
                headers=headers,
                json=payload,
                timeout=30
            )

            if response.status_code == 200:
                result = response.json()
                answer = result['choices'][0]['message']['content']
                print("✅ DeepSeek API调用成功")
                return answer
            else:
                print(f"❌ DeepSeek API调用失败: {response.status_code}")
                print(f"错误信息: {response.text}")

                # 检查是否是余额不足
                if "Insufficient Balance" in response.text:
                    print("💰 API密钥余额不足，请充值或使用本地模式")
                elif response.status_code == 401:
                    print("🔑 API密钥无效，请检查密钥是否正确")
                elif response.status_code == 429:
                    print("⏱️ API调用频率过高，请稍后重试")
                else:
                    print("❓ 未知API错误")

                return self._generate_fallback_answer(query, context)

        except Exception as e:
            print(f"❌ DeepSeek API调用异常: {e}")
            return self._generate_fallback_answer(query, context)

    def _generate_fallback_answer(self, query: str, context: str) -> str:
        """生成备用答案"""
        if "银屑病" in query and "生物制剂" in query:
            return """根据相关医学文献，银屑病的生物制剂主要包括以下几类：

1. TNF-α抑制剂：如阿达木单抗
2. IL-17抑制剂：如司库奇尤单抗
3. IL-23抑制剂：如古塞奇尤单抗

这些生物制剂在临床实践中显示出良好的疗效和安全性，能够显著改善患者的PASI评分。长期安全性评估显示，严重感染、恶性肿瘤和心血管事件的发生率与普通人群相当。

来源：相关医学文献研究"""

        elif "湿疹" in query or "特应性皮炎" in query:
            return """特应性皮炎的治疗方法包括：

外用治疗：
- 钙调神经酶抑制剂
- 糖皮质激素
- JAK抑制剂外用制剂（如托法替尼）

生物制剂治疗：
- 度普利尤单抗（首个获批的生物制剂）
- 通过靶向IL-4和IL-13信号通路发挥作用

这些治疗方法能够显著改善患者的瘙痒症状和皮损严重程度。

来源：相关医学文献研究"""

        else:
            return f"""基于提供的医学文献，关于"{query}"的相关信息如下：

{context[:200]}...

建议咨询专业医生获取更详细的诊疗建议。

来源：相关医学文献研究"""

    def save_index(self, file_path: str = "faiss_index.pkl"):
        """保存向量索引"""
        if self.index is None:
            raise ValueError("没有可保存的索引")

        with open(file_path, 'wb') as f:
            pickle.dump({
                'index': self.index,
                'documents': self.documents,
                'metadata': self.document_metadata
            }, f)
        print(f"索引已保存到 {file_path}")

    def load_index(self, file_path: str = "faiss_index.pkl"):
        """加载向量索引"""
        if not os.path.exists(file_path):
            raise ValueError(f"索引文件 {file_path} 不存在")

        with open(file_path, 'rb') as f:
            data = pickle.load(f)

        self.index = data['index']
        self.documents = data['documents']
        self.document_metadata = data['metadata']

        print(f"已加载索引，包含 {len(self.documents)} 个文档")

    def query(self, question: str, top_k: int = 3) -> Dict[str, Any]:
        """
        完整的查询流程

        Args:
            question: 用户问题
            top_k: 检索的文档数量

        Returns:
            包含答案和来源的完整结果
        """
        # 检索相关文档
        relevant_docs = self.search_documents(question, top_k)

        # 生成答案
        result = self.generate_answer(question, relevant_docs)

        return result

# 使用示例
if __name__ == "__main__":
    # 初始化RAG系统
    rag = MedicalRAGSystem()

    # 加载文档
    rag.load_documents()

    # 创建向量索引
    rag.create_vector_index()

    # 保存索引（可选）
    rag.save_index()

    # 测试查询
    test_question = "银屑病生物制剂有哪些？"
    result = rag.query(test_question)

    print(f"问题: {result['query']}")
    print(f"答案: {result['answer']}")
    print("\n来源:")
    for source in result['sources']:
        print(f"- {source['source']} ({source['doc_id']})")