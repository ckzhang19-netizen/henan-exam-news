
import requests
import os
import sys # 引入sys库

# 1. 尝试加载 Token (我们已知这步成功)
TOKEN = os.environ.get("PUSHPLUS_TOKEN") 

if not TOKEN:
    print("FATAL: Token未加载，无法测试！")
    sys.exit(1)

url = 'http://www.pushplus.plus/send'
data = {
    "token": TOKEN,
    "title": "【GitHub最终网络测试】",
    "content": "如果这条消息没收到，说明GitHub服务器IP被暂时封锁。",
    "template": "html"
}

print("--- START FINAL NETWORK TEST ---")

try:
    # 强制设置一个较长的超时时间，确保请求完成
    resp = requests.post(url, json=data, timeout=30)
    
    # 强制打印 HTTP 状态码和 API 原始回复
    print("HTTP Status Code:", resp.status_code)
    print("API Raw Response:", resp.text) 

except requests.exceptions.RequestException as e:
    # 捕获所有网络错误，并打印详细信息
    print(f"NETWORK FAILURE: 连接错误或超时。错误信息: {e}")
    
print("--- END FINAL NETWORK TEST ---")
