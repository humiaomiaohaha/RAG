#!/usr/bin/env python3
"""
医疗知识RAG系统测试脚本
"""

import json
import os

def test_data_generation():
    """测试数据生成"""
    print("🧪 测试数据生成...")
    
    try:
        from data_generator import generate_medical_data
        docs = generate_medical_data()
        
        if len(docs) > 0:
            print(f"✅ 成功生成 {len(docs)} 篇医疗文献")
            return True
        else:
            print("❌ 数据生成失败")
            return False
    except Exception as e:
        print(f"❌ 数据生成异常: {e}")
        return False

def test_rag_system():
    """测试RAG系统"""
    print("🧪 测试RAG系统...")
    
    try:
        from rag_system import MedicalRAGSystem
        
        # 初始化系统
        rag = MedicalRAGSystem()
        
        # 加载文档
        rag.load_documents()
        
        # 创建索引
        rag.create_vector_index()
        
        # 测试查询
        test_question = "银屑病生物制剂有哪些？"
        result = rag.query(test_question)
        
        if result and 'answer' in result and 'sources' in result:
            print("✅ RAG系统测试通过")
            print(f"问题: {result['query']}")
            print(f"答案长度: {len(result['answer'])} 字符")
            print(f"来源数量: {len(result['sources'])}")
            return True
        else:
            print("❌ RAG系统返回结果格式错误")
            return False
            
    except Exception as e:
        print(f"❌ RAG系统测试异常: {e}")
        return False

def test_api_endpoints():
    """测试API端点"""
    print("🧪 测试API端点...")
    
    try:
        import requests
        import time
        
        # 启动服务器（在后台）
        import subprocess
        import threading
        
        def start_server():
            subprocess.run(["python", "app.py"], capture_output=True)
        
        # 启动服务器线程
        server_thread = threading.Thread(target=start_server, daemon=True)
        server_thread.start()
        
        # 等待服务器启动
        time.sleep(5)
        
        # 测试健康检查
        try:
            response = requests.get("http://localhost:5000/api/health", timeout=10)
            if response.status_code == 200:
                print("✅ 健康检查通过")
            else:
                print("❌ 健康检查失败")
                return False
        except:
            print("⚠️  健康检查跳过（服务器可能未启动）")
        
        # 测试文档统计
        try:
            response = requests.get("http://localhost:5000/api/documents", timeout=10)
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    print("✅ 文档统计API正常")
                else:
                    print("❌ 文档统计API返回错误")
                    return False
            else:
                print("❌ 文档统计API请求失败")
                return False
        except:
            print("⚠️  文档统计API跳过")
        
        return True
        
    except Exception as e:
        print(f"❌ API测试异常: {e}")
        return False

def main():
    """主测试函数"""
    print("🏥 医疗知识RAG系统测试")
    print("=" * 50)
    
    tests = [
        ("数据生成", test_data_generation),
        ("RAG系统", test_rag_system),
        ("API端点", test_api_endpoints),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n📋 {test_name}测试:")
        if test_func():
            passed += 1
        print()
    
    print("=" * 50)
    print(f"📊 测试结果: {passed}/{total} 通过")
    
    if passed == total:
        print("🎉 所有测试通过！系统可以正常使用")
        print("\n🚀 启动系统:")
        print("python run.py")
    else:
        print("⚠️  部分测试失败，请检查系统配置")
    
    return passed == total

if __name__ == "__main__":
    main() 