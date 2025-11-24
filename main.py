import requests
from bs4 import BeautifulSoup
import datetime
import os

# 环境变量获取 Token
TOKEN = os.environ.get("PUSHPLUS_TOKEN")
# 调试代码：检查 Token 是否加载
if TOKEN:
    print(f"DEBUG: Token已加载，开头为: {TOKEN[:4]}****")
else:
    print("DEBUG: 警告！Token未加载成功！")

# 关键词
KEYWORDS = ["中考", "高考", "招生", "分数线", "志愿", "录取", "发布", "时间"]

def get_current_date():
    return datetime.datetime.now().strftime("%Y-%m-%d")

def fetch_haeea():
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
        print(f"Error: {e}")
    return results[:10]

def send_push(content):
    if not TOKEN: return
    url = 'http://www.pushplus.plus/send'
    data = {"token": TOKEN, "title": f"河南招考日报 {get_current_date()}", "content": content, "template": "markdown"}
    requests.post(url, json=data)

def main():
    news = fetch_haeea()
    if not news:
        print("无新内容")
        return
    
    msg = [f"## 📅 {get_current_date()} 河南招考资讯", "---", "### 🏛️ 省教育考试院"]
    for item in news:
        msg.append(f"- [{item['title']}]({item['url']})")
    msg.append("\n---")
    msg.append("🔍 *来自自动脚本*")
    
    send_push("\n".join(msg))

if __name__ == "__main__":
    main()
