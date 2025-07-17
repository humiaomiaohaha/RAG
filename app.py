# =============================================================================
# 医疗知识RAG系统 - Flask后端应用主文件
# 功能：提供RESTful API服务，处理用户查询请求，管理RAG系统生命周期
# 作者：AI助手
# 日期：2024年
# =============================================================================

# 导入Flask框架相关模块
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS  # 处理跨域请求
import json  # JSON数据处理
import os    # 操作系统接口

# 智能导入RAG系统模块 - 实现自动降级机制
try:
    # 尝试导入完整的RAG系统（需要深度学习模型）
    from rag_system import MedicalRAGSystem
    USE_SIMPLE_RAG = False  # 标记使用完整RAG系统
    print("✅ 成功导入完整RAG系统")
except ImportError:
    # 如果完整RAG系统导入失败，使用简化版本（基于关键词匹配）
    from simple_rag_system import SimpleMedicalRAGSystem
    USE_SIMPLE_RAG = True   # 标记使用简化RAG系统
    print("⚠️ 完整RAG系统导入失败，使用简化版本")

# =============================================================================
# Flask应用初始化
# =============================================================================

# 创建Flask应用实例
app = Flask(__name__)

# 启用跨域资源共享(CORS) - 允许前端页面调用后端API
CORS(app)

# 全局变量：存储RAG系统实例
# 在整个应用生命周期中保持单一实例，避免重复初始化
rag_system = None

# =============================================================================
# RAG系统初始化函数
# 功能：根据环境情况选择合适的RAG系统实现，加载数据，创建索引
# =============================================================================

def initialize_rag():
    """
    初始化RAG（检索增强生成）系统

    该函数负责：
    1. 根据环境情况选择完整RAG系统或简化RAG系统
    2. 确保医疗数据文件存在
    3. 加载文档数据
    4. 创建向量索引（仅完整RAG系统）
    5. 处理各种异常情况

    返回：
        bool: 初始化成功返回True，失败返回False
    """
    global rag_system  # 声明使用全局变量

    try:
        # 根据导入情况选择RAG系统类型
        if USE_SIMPLE_RAG:
            # 使用简化RAG系统 - 基于关键词匹配，无需深度学习模型
            print("🔧 使用简化RAG系统（关键词匹配模式）...")
            rag_system = SimpleMedicalRAGSystem()
        else:
            # 使用完整RAG系统 - 基于向量检索和深度学习模型
            print("🚀 使用完整RAG系统（向量检索模式）...")
            # 配置DeepSeek API密钥和本地embedding模型路径
            rag_system = MedicalRAGSystem(
                model_path="D:\\Embedding\\Embedding",  # 本地embedding模型路径
                deepseek_api_key="sk-b87c9bf17adf4c5d935feb2748534da4"  # DeepSeek API密钥
            )

        # =============================================================================
        # 数据文件检查和生成
        # =============================================================================

        # 检查医疗数据文件是否存在，不存在则自动生成
        if not os.path.exists("medical_docs.json"):
            print("📊 医疗数据文件不存在，正在生成示例数据...")
            from data_generator import generate_medical_data
            generate_medical_data()
            print("✅ 示例数据生成完成")
        else:
            print("✅ 医疗数据文件已存在")

        # =============================================================================
        # 文档数据加载
        # =============================================================================

        # 加载医疗文档数据到RAG系统
        print("📚 正在加载医疗文档数据...")
        rag_system.load_documents()
        print("✅ 文档数据加载完成")

        # =============================================================================
        # 向量索引管理（仅完整RAG系统）
        # =============================================================================

        if not USE_SIMPLE_RAG:
            # 检查是否已有保存的向量索引文件
            if os.path.exists("faiss_index.pkl"):
                print("🔄 发现已存在的向量索引，正在加载...")
                rag_system.load_index()
                print("✅ 向量索引加载完成")
            else:
                print("🔨 未发现向量索引，正在创建新的索引...")
                rag_system.create_vector_index()  # 创建FAISS向量索引
                rag_system.save_index()           # 保存索引到文件
                print("✅ 向量索引创建并保存完成")

        print("🎉 RAG系统初始化完成")
        return True

    except Exception as e:
        # =============================================================================
        # 异常处理和降级机制
        # =============================================================================

        print(f"❌ RAG系统初始化失败: {str(e)}")
        print("🔄 正在尝试降级到简化RAG系统...")

        try:
            # 尝试使用简化RAG系统作为备用方案
            from simple_rag_system import SimpleMedicalRAGSystem
            rag_system = SimpleMedicalRAGSystem()

            # 确保数据文件存在
            if not os.path.exists("medical_docs.json"):
                print("📊 正在生成示例数据...")
                from data_generator import generate_medical_data
                generate_medical_data()

            # 加载文档数据
            print("📚 正在加载文档数据...")
            rag_system.load_documents()
            print("✅ 简化RAG系统初始化完成")
            return True

        except Exception as e2:
            print(f"❌ 简化RAG系统也初始化失败: {str(e2)}")
            print("💡 建议检查：")
            print("   1. Python依赖是否正确安装")
            print("   2. 数据文件是否可访问")
            print("   3. 系统权限是否足够")
            return False

# =============================================================================
# API端点定义
# 功能：提供RESTful API接口，处理前端请求
# =============================================================================

@app.route('/api/query', methods=['POST'])
def query():
    """
    处理用户查询请求的API端点

    功能：
    1. 接收前端发送的医疗问题
    2. 验证输入数据的有效性
    3. 调用RAG系统生成答案
    4. 返回标准化的JSON响应

    请求格式：
        POST /api/query
        Content-Type: application/json
        {
            "question": "银屑病生物制剂有哪些？"
        }

    响应格式：
        成功：
        {
            "success": true,
            "data": {
                "answer": "根据相关医学文献...",
                "sources": [...],
                "query": "银屑病生物制剂有哪些？"
            }
        }

        失败：
        {
            "success": false,
            "error": "错误信息"
        }
    """
    try:
        # =============================================================================
        # 请求数据解析和验证
        # =============================================================================

        # 从HTTP请求中解析JSON数据
        data = request.get_json()

        # 提取并清理用户问题（去除首尾空格）
        question = data.get('question', '').strip()

        # 输入验证：检查问题是否为空
        if not question:
            return jsonify({
                'success': False,
                'error': '问题不能为空，请输入您的医疗问题'
            }), 400  # HTTP 400 Bad Request

        # 系统状态检查：确保RAG系统已正确初始化
        if rag_system is None:
            return jsonify({
                'success': False,
                'error': 'RAG系统未初始化，请检查系统配置'
            }), 500  # HTTP 500 Internal Server Error

        # =============================================================================
        # 执行RAG查询
        # =============================================================================

        # 调用RAG系统处理用户问题，返回前3个最相关的文档
        result = rag_system.query(question, top_k=3)

        # =============================================================================
        # 返回成功响应
        # =============================================================================

        return jsonify({
            'success': True,
            'data': result
        })

    except Exception as e:
        # =============================================================================
        # 异常处理和错误响应
        # =============================================================================

        # 捕获所有未预期的异常，返回友好的错误信息
        return jsonify({
            'success': False,
            'error': f'查询处理失败: {str(e)}'
        }), 500  # HTTP 500 Internal Server Error

@app.route('/api/health', methods=['GET'])
def health_check():
    """
    系统健康检查API端点

    功能：
    1. 检查系统运行状态
    2. 验证RAG系统是否已初始化
    3. 提供系统监控信息

    响应格式：
    {
        "status": "healthy",
        "rag_initialized": true/false
    }
    """
    return jsonify({
        'status': 'healthy',  # 系统运行状态
        'rag_initialized': rag_system is not None  # RAG系统初始化状态
    })

@app.route('/api/documents', methods=['GET'])
def get_documents():
    """
    获取文档统计信息的API端点

    功能：
    1. 返回系统中医疗文档的总数量
    2. 返回向量索引的大小（仅完整RAG系统）
    3. 提供系统数据规模的统计信息

    响应格式：
        成功：
        {
            "success": true,
            "data": {
                "total_documents": 25,
                "index_size": 25
            }
        }

        失败：
        {
            "success": false,
            "error": "错误信息"
        }
    """
    # 检查RAG系统是否已初始化
    if rag_system is None:
        return jsonify({
            'success': False,
            'error': 'RAG系统未初始化，无法获取文档统计信息'
        }), 500  # HTTP 500 Internal Server Error

    # =============================================================================
    # 获取索引大小信息
    # =============================================================================

    # 根据RAG系统类型获取不同的索引大小
    if hasattr(rag_system, 'index') and rag_system.index:
        # 完整RAG系统：返回FAISS向量索引的大小
        index_size = rag_system.index.ntotal
    else:
        # 简化RAG系统：返回文档数量作为索引大小
        index_size = len(rag_system.documents)

    # 返回文档统计信息
    return jsonify({
        'success': True,
        'data': {
            'total_documents': len(rag_system.documents),  # 总文档数量
            'index_size': index_size  # 索引大小
        }
    })

@app.route('/')
def index():
    """
    系统主页API端点

    功能：
    1. 返回医疗知识RAG系统的主页面
    2. 提供用户交互界面

    返回：
        HTML页面：templates/index.html
    """
    return render_template('index.html')

# =============================================================================
# 应用启动入口
# 功能：初始化RAG系统并启动Flask Web服务器
# =============================================================================

if __name__ == '__main__':
    """
    应用启动入口点
    
    执行流程：
    1. 调用initialize_rag()初始化RAG系统
    2. 如果初始化成功，启动Flask Web服务器
    3. 如果初始化失败，输出错误信息并退出
    
    服务器配置：
    - 调试模式：开启（便于开发调试）
    - 监听地址：0.0.0.0（允许外部访问）
    - 端口：5000
    """

    print("🏥 医疗知识RAG系统启动中...")
    print("=" * 60)

    # 初始化RAG系统
    if initialize_rag():
        print("✅ RAG系统初始化成功")
        print("🚀 正在启动Flask Web服务器...")
        print("📱 访问地址: http://localhost:5000")
        print("⏹️  按 Ctrl+C 停止服务器")
        print("-" * 60)

        # 启动Flask开发服务器
        app.run(
            debug=True,      # 开启调试模式，自动重载代码
            host='0.0.0.0',  # 监听所有网络接口
            port=5000        # 使用5000端口
        )
    else:
        print("❌ RAG系统初始化失败")
        print("💡 请检查：")
        print("   1. Python依赖是否正确安装")
        print("   2. 数据文件是否可访问")
        print("   3. 模型路径是否正确")
        print("   4. API密钥是否有效")
        print("🔧 无法启动Web服务器") 