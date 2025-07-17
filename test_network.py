#!/usr/bin/env python3
"""
网络连接测试脚本
"""

import requests
import os
import sys

def test_basic_connectivity():
    """测试基本网络连接"""
    print("🌐 测试基本网络连接...")
    
    test_urls = [
        "https://www.baidu.com",
        "https://www.google.com",
        "https://api.deepseek.com"
    ]
    
    for url in test_urls:
        try:
            response = requests.get(url, timeout=10)
            print(f"✅ {url} - 状态码: {response.status_code}")
        except Exception as e:
            print(f"❌ {url} - 连接失败: {e}")

def test_deepseek_api():
    """测试DeepSeek API连接"""
    print("\n🔑 测试DeepSeek API连接...")
    
    api_key = "sk-b87c9bf17adf4c5d935feb2748534da4"
    api_url = "https://api.deepseek.com/v1/chat/completions"
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}",
        "User-Agent": "MedicalRAGSystem/1.0"
    }
    
    payload = {
        "model": "deepseek-chat",
        "messages": [
            {"role": "user", "content": "Hello"}
        ],
        "max_tokens": 10
    }
    
    try:
        # 方法1：使用默认设置
        print("方法1：使用默认requests设置...")
        response = requests.post(api_url, headers=headers, json=payload, timeout=30)
        print(f"状态码: {response.status_code}")
        if response.status_code == 200:
            print("✅ API连接成功")
            return True
        else:
            print(f"❌ API返回错误: {response.text}")
    except Exception as e:
        print(f"❌ 方法1失败: {e}")
    
    try:
        # 方法2：禁用代理
        print("\n方法2：禁用代理设置...")
        session = requests.Session()
        session.trust_env = False
        
        response = session.post(api_url, headers=headers, json=payload, timeout=30)
        print(f"状态码: {response.status_code}")
        if response.status_code == 200:
            print("✅ API连接成功")
            return True
        else:
            print(f"❌ API返回错误: {response.text}")
    except Exception as e:
        print(f"❌ 方法2失败: {e}")
    
    try:
        # 方法3：使用不同的超时设置
        print("\n方法3：使用更长的超时时间...")
        response = requests.post(api_url, headers=headers, json=payload, timeout=60)
        print(f"状态码: {response.status_code}")
        if response.status_code == 200:
            print("✅ API连接成功")
            return True
        else:
            print(f"❌ API返回错误: {response.text}")
    except Exception as e:
        print(f"❌ 方法3失败: {e}")
    
    return False

def check_environment_variables():
    """检查环境变量中的代理设置"""
    print("\n🔍 检查环境变量...")
    
    proxy_vars = ['HTTP_PROXY', 'HTTPS_PROXY', 'http_proxy', 'https_proxy']
    
    for var in proxy_vars:
        value = os.environ.get(var)
        if value:
            print(f"⚠️  发现代理设置: {var} = {value}")
        else:
            print(f"✅ {var} 未设置")

def suggest_solutions():
    """提供解决方案建议"""
    print("\n💡 解决方案建议:")
    print("1. 检查网络连接是否正常")
    print("2. 如果使用代理，请设置正确的代理配置")
    print("3. 尝试在命令行中设置代理环境变量:")
    print("   set HTTP_PROXY=http://your-proxy:port")
    print("   set HTTPS_PROXY=http://your-proxy:port")
    print("4. 或者清除代理设置:")
    print("   set HTTP_PROXY=")
    print("   set HTTPS_PROXY=")
    print("5. 检查防火墙设置")
    print("6. 尝试使用VPN或更换网络环境")

def main():
    """主函数"""
    print("🔧 网络连接诊断工具")
    print("=" * 50)
    
    # 检查环境变量
    check_environment_variables()
    
    # 测试基本连接
    test_basic_connectivity()
    
    # 测试DeepSeek API
    api_success = test_deepseek_api()
    
    if not api_success:
        suggest_solutions()
    
    print("\n" + "=" * 50)
    if api_success:
        print("🎉 网络连接正常，可以正常使用DeepSeek API")
    else:
        print("⚠️  网络连接存在问题，请参考上述解决方案")

if __name__ == "__main__":
    main() 