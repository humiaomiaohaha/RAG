#!/usr/bin/env python3
"""
医疗知识RAG系统启动脚本
"""

import os
import sys
import subprocess

def check_dependencies():
    """检查依赖是否安装"""
    try:
        import flask
        import langchain
        import faiss
        import sentence_transformers
        print("✅ 所有依赖已安装")
        return True
    except ImportError as e:
        print(f"❌ 缺少依赖: {e}")
        print("请运行: pip install -r requirements.txt")
        return False

def generate_data():
    """生成示例数据"""
    print("📊 生成示例医疗数据...")
    try:
        from data_generator import generate_medical_data
        generate_medical_data()
        print("✅ 数据生成完成")
        return True
    except Exception as e:
        print(f"❌ 数据生成失败: {e}")
        return False

def start_server():
    """启动Flask服务器"""
    print("🚀 启动医疗知识RAG系统...")
    print("📱 访问地址: http://localhost:5000")
    print("⏹️  按 Ctrl+C 停止服务器")
    print("-" * 50)
    
    try:
        from app import app
        app.run(debug=True, host='0.0.0.0', port=5000)
    except KeyboardInterrupt:
        print("\n👋 服务器已停止")
    except Exception as e:
        print(f"❌ 服务器启动失败: {e}")

def main():
    """主函数"""
    print("🏥 医疗知识RAG系统")
    print("=" * 50)
    
    # 检查依赖
    if not check_dependencies():
        sys.exit(1)
    
    # 生成数据
    if not os.path.exists("medical_docs.json"):
        if not generate_data():
            sys.exit(1)
    else:
        print("✅ 数据文件已存在")
    
    # 启动服务器
    start_server()

if __name__ == "__main__":
    main() 