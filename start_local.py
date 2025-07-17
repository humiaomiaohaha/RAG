#!/usr/bin/env python3
"""
本地模式启动脚本 - 不依赖外部API
"""

import os
import sys

def check_dependencies():
    """检查基本依赖"""
    try:
        import flask
        print("✅ Flask已安装")
    except ImportError:
        print("❌ Flask未安装，请运行: pip install flask flask-cors")
        return False
    
    try:
        import json
        print("✅ JSON模块可用")
    except ImportError:
        print("❌ JSON模块不可用")
        return False
    
    return True

def generate_data_if_needed():
    """如果需要则生成数据"""
    if not os.path.exists("medical_docs.json"):
        print("📊 生成示例医疗数据...")
        try:
            from data_generator import generate_medical_data
            generate_medical_data()
            print("✅ 数据生成完成")
        except Exception as e:
            print(f"❌ 数据生成失败: {e}")
            return False
    else:
        print("✅ 数据文件已存在")
    
    return True

def start_local_server():
    """启动本地服务器"""
    print("🚀 启动本地医疗知识RAG系统...")
    print("📱 访问地址: http://localhost:5000")
    print("🔧 模式: 本地关键词匹配（无需外部API）")
    print("⏹️  按 Ctrl+C 停止服务器")
    print("-" * 50)
    
    try:
        # 导入并启动简化RAG系统
        from simple_rag_system import SimpleMedicalRAGSystem
        from flask import Flask, request, jsonify, render_template
        from flask_cors import CORS
        
        app = Flask(__name__)
        CORS(app)
        
        # 初始化RAG系统
        rag_system = SimpleMedicalRAGSystem()
        rag_system.load_documents()
        
        @app.route('/')
        def index():
            return render_template('index.html')
        
        @app.route('/api/query', methods=['POST'])
        def query():
            try:
                data = request.get_json()
                question = data.get('question', '').strip()
                
                if not question:
                    return jsonify({
                        'success': False,
                        'error': '问题不能为空'
                    }), 400
                
                # 执行查询
                result = rag_system.query(question, top_k=3)
                
                return jsonify({
                    'success': True,
                    'data': result
                })
                
            except Exception as e:
                return jsonify({
                    'success': False,
                    'error': f'查询失败: {str(e)}'
                }), 500
        
        @app.route('/api/health', methods=['GET'])
        def health_check():
            return jsonify({
                'status': 'healthy',
                'mode': 'local_keyword_matching'
            })
        
        @app.route('/api/documents', methods=['GET'])
        def get_documents():
            return jsonify({
                'success': True,
                'data': {
                    'total_documents': len(rag_system.documents),
                    'index_size': len(rag_system.documents)
                }
            })
        
        # 启动服务器
        app.run(debug=True, host='0.0.0.0', port=5000)
        
    except KeyboardInterrupt:
        print("\n👋 服务器已停止")
    except Exception as e:
        print(f"❌ 服务器启动失败: {e}")

def main():
    """主函数"""
    print("🏥 医疗知识RAG系统 - 本地模式")
    print("=" * 50)
    
    # 检查依赖
    if not check_dependencies():
        sys.exit(1)
    
    # 生成数据
    if not generate_data_if_needed():
        sys.exit(1)
    
    # 启动服务器
    start_local_server()

if __name__ == "__main__":
    main() 