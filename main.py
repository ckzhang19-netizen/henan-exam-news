import requests
from bs4 import BeautifulSoup
import datetime
import os
import sys

# 环境变量获取 Token
TOKEN = os.environ.get("PUSHPLUS_TOKEN")
# 关键词设置
KEYWORDS = ["中考", "高考", "招生", "分数线", "志愿", "录取", "发布", "时间"]

def get_current_date():
    return datetime.datetime.now().strftime("%Y-%m-%d")

def fetch_haeea():
    """抓取河南省教育考试院相关资讯"""
    print("正在抓取：河南省教育考试院...")
    url = "http://www.haeea.cn/"
    results = []
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        resp = requests.get(url, headers=headers, timeout=10)
        resp.encoding = 'utf-8'
        soup = BeautifulSoup(resp.text, 'html.parser')
        
        links = soup.find_all('a')
        for link in links:
            text = link.get_text(strip=True)
            href = link.get('href')
            if not text or not href: continue
            
            if href.startswith('/'): full_link = f"http://www.haeea.cn{href}"
            elif href.startswith('http'): full_link = href
            else: continue

            if any(k in text for k in KEYWORDS):
                if {'title': text, 'url': full_link} not in results:
                    results.append({'title': text, 'url': full_link})
    except Exception as e:
        print(f"Error: 考试院抓取出错: {e}")
    return results[:10]

def send_push(content):
    """发送到微信 (鲁棒版本)"""
    if not TOKEN:
        print("致命错误：未找到 Token，程序退出。")
        sys.exit(1)
    
    url = 'http://www.pushplus.plus/send'
    title = f"河南招考日报 ({get_current_date()})"
    
    data = {
        "token": TOKEN,
        "title": title,
        "content": content,
        "template": "markdown" # 使用 Markdown 格式
    }
    
    try:
        resp = requests.post(url, json=data, timeout=15)
        resp.raise_for_status() 
        print(f"推送结果: {resp.text}") 
    except requests.exceptions.RequestException as e:
        print(f"致命错误：发送微信失败，连接错误或超时。错误信息: {e}")

def main():
    # 1. 获取数据
    news = fetch_haeea()
    
    # 2. 整合内容
    if not news:
        send_push("今日未搜集到新的河南招考相关资讯。")
        return

    msg = [f"## 📅 {get_current_date()} 河南招考资讯", "---", "### 🏛️ 河南省教育考试院"]
    for item in news:
        # Markdown 格式：[标题](链接)
        msg.append(f"- [{item['title']}]({item['url']})")
    msg.append("\n---")
    msg.append("🔍 *信息由自动脚本搜集，请以官方发布为准*")
    
    final_content = "\n".join(msg)
    
    # 3. 发送
    send_push(final_content)

if __name__ == "__main__":
    main()
