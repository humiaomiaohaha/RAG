import json
import re
from collections import Counter

class SimpleMedicalRAGSystem:
    def __init__(self):
        self.documents = []
        self.keyword_index = {}
    
    def load_documents(self):
        try:
            with open('medical_docs.json', 'r', encoding='utf-8') as f:
                self.documents = json.load(f)
            
            self._build_keyword_index()
            print(f"已加载 {len(self.documents)} 篇医疗文献")
            
        except FileNotFoundError:
            print("医疗数据文件不存在，请先运行数据生成器")
            self.documents = []
        except Exception as e:
            print(f"加载文档失败: {str(e)}")
            self.documents = []
    
    def _build_keyword_index(self):
        self.keyword_index = {}
        
        for doc in self.documents:
            text = doc['text'].lower()
            words = re.findall(r'\w+', text)
            
            for word in words:
                if len(word) > 2:
                    if word not in self.keyword_index:
                        self.keyword_index[word] = []
                    self.keyword_index[word].append(doc['doc_id'])
    
    def _calculate_similarity(self, query, doc_text):
        query_words = set(re.findall(r'\w+', query.lower()))
        doc_words = set(re.findall(r'\w+', doc_text.lower()))
        
        if not query_words:
            return 0
        
        intersection = query_words.intersection(doc_words)
        return len(intersection) / len(query_words)
    
    def query(self, question, top_k=3):
        if not self.documents:
            return {
                'answer': '抱歉，系统中没有可用的医疗文献数据。',
                'sources': [],
                'query': question
            }
        
        scores = []
        for doc in self.documents:
            similarity = self._calculate_similarity(question, doc['text'])
            scores.append((similarity, doc))
        
        scores.sort(key=lambda x: x[0], reverse=True)
        
        top_docs = scores[:top_k]
        relevant_docs = [doc for score, doc in top_docs if score > 0]
        
        if not relevant_docs:
            return {
                'answer': '抱歉，没有找到与您问题相关的医疗文献。请尝试使用不同的关键词。',
                'sources': [],
                'query': question
            }
        
        answer = self._generate_answer(question, relevant_docs)
        
        sources = []
        for doc in relevant_docs:
            sources.append({
                'doc_id': doc['doc_id'],
                'text': doc['text'][:200] + '...',
                'source': doc['source']
            })
        
        return {
            'answer': answer,
            'sources': sources,
            'query': question
        }
    
    def _generate_answer(self, question, relevant_docs):
        if not relevant_docs:
            return "抱歉，没有找到相关信息。"
        
        answer_parts = []
        answer_parts.append("根据相关医学文献，")
        
        for i, doc in enumerate(relevant_docs):
            if i == 0:
                answer_parts.append(doc['text'])
            else:
                answer_parts.append(f"此外，{doc['text']}")
        
        answer = " ".join(answer_parts)
        
        if len(answer) > 1000:
            answer = answer[:1000] + "..."
        
        return answer 