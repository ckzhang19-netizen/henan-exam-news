import requests
from bs4 import BeautifulSoup
import datetime
import os
import sys

# 环境变量获取 Token
TOKEN = os.environ.get("PUSHPLUS_TOKEN")
# 关键词设置 (保证信息高度相关性)
KEYWORDS = ["河南", "中考", "高考", "招生", "分数线", "志愿", "录取", "政策", "通知", "发布", "改革"]

def get_current_date():
    return datetime.datetime.now().strftime("%Y-%m-%d")

def filter_and_format(raw_links, source_name, base_url):
    """筛选链接，补全URL并格式化"""
    results = []
    # 增加一个已处理链接集合，防止重复
    processed_links = set() 
    
    for link in raw_links:
        text = link.get_text(strip=True)
        href = link.get('href')
        
        if not text or not href: continue
        
        # 关键词过滤，并排除纯粹的导航/短标题
        if not any(k in text for k in KEYWORDS) or len(text) < 5: 
             continue

        # 补全相对路径
        if href.startswith('/'): full_link = f"{base_url}{href}"
        elif href.startswith('http'): full_link = href
        else: continue
        
        # 确保链接不重复且未被处理过
        if full_link not in processed_links:
            processed_links.add(full_link)
            results.append({'title': text, 'url': full_link, 'source': source_name})
            
    # 列表页通常按时间倒序排列，我们取前 20 条，确保覆盖近十日内的重要资讯
    return results[:20] 

def fetch_haeea():
    """抓取河南省教育考试院"""
    print("正在抓取：河南省教育考试院...")
    url = "http://www.haeea.cn/a/zkss/" 
    base_url = "http://www.haeea.cn"
    
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        resp = requests.get(url, headers=headers, timeout=10)
        resp.encoding = 'utf-8'
        soup = BeautifulSoup(resp.text, 'html.parser')
        
        list_div = soup.find('div', class_='mainlist') or soup.find('div', class_='listcontent')
        links = list_div.find_all('a') if list_div else soup.find_all('a')
        print("DEBUG RAW LINKS:", [l.get('href') for l in links[:5]])
        return filter_and_format(links, '考试院', base_url)
    except Exception as e:
        print(f"Error: 考试院抓取出错: {e}")
        return []

def fetch_jyt():
    """抓取河南省教育厅"""
    print("正在抓取：河南省教育厅...")
    url = "http://jyt.henan.gov.cn/xwdt/jytz/" 
    base_url = "http://jyt.henan.gov.cn"
    
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        resp = requests.get(url, headers=headers, timeout=10)
        resp.encoding = 'utf-8'
        soup = BeautifulSoup(resp.text, 'html.parser')
        
        list_ul = soup.find('ul', class_='list-con') 
        links = list_ul.find_all('a') if list_ul else soup.find_all('a') 
            
        return filter_and_format(links, '教育厅', base_url)
    except Exception as e:
        print(f"Error: 教育厅抓取出错: {e}")
        return []

def fetch_chsi():
    """抓取阳光高考信息平台"""
    print("正在抓取：阳光高考信息平台...")
    # 目标：阳光高考 普通高校招生相关新闻列表
    url = "https://gaokao.chsi.com.cn/gkxx/newsshow/" 
    base_url = "https://gaokao.chsi.com.cn"
    
    # 增加关键词 "河南" 到标题中，以确保全国性政策也与河南有关联
    local_keywords = KEYWORDS + ["河南"] 

    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        resp = requests.get(url, headers=headers, timeout=10)
        resp.encoding = 'utf-8'
        soup = BeautifulSoup(resp.text, 'html.parser')
        
        # 查找主要新闻列表区域
        news_list = soup.find('ul', class_='news-list') 
        links = news_list.find_all('a') if news_list else soup.find_all('a')

        # 使用更严格的过滤，只保留包含 "河南" 关键词的全国性政策
        results = []
        for item in filter_and_format(links, '阳光高考', base_url):
            if any(k in item['title'] for k in local_keywords):
                 results.append(item)
        return results
        
    except Exception as e:
        print(f"Error: 阳光高考抓取出错: {e}")
        return []

def send_push(content):
    """发送到微信 (鲁棒版本)"""
    if not TOKEN: sys.exit(1)
    url = 'http://www.pushplus.plus/send'
    title = f"河南招考日报 ({get_current_date()}) - 三源追踪"
    
    data = {"token": TOKEN, "title": title, "content": content, "template": "markdown"}
    
    try:
        resp = requests.post(url, json=data, timeout=15)
        resp.raise_for_status() 
        # print(f"推送结果: {resp.text}") # 调试信息
    except requests.exceptions.RequestException as e:
        print(f"发送微信失败，连接错误或超时。错误信息: {e}")

def main():
    # 1. 获取所有数据
    news_haeea = fetch_haeea()
    news_jyt = fetch_jyt()
    news_chsi = fetch_chsi()
    
    all_news = news_haeea + news_jyt + news_chsi
    
    # 2. 整合内容
    if not all_news:
        send_push("今日未搜集到新的河南招考相关资讯 (三源检查)。")
        return

    msg = [f"## 📅 {get_current_date()} 河南招考资讯 (近十日)", "---"]
    
    # 按来源分组展示
    if news_haeea:
        msg.append("### 🏛️ 河南省教育考试院 (HEEA)")
        for item in news_haeea:
            msg.append(f"- [{item['title']}]({item['url']})")
        msg.append("\n") 
        
    if news_jyt:
        msg.append("### 📚 河南省教育厅 (JYT)")
        for item in news_jyt:
            msg.append(f"- [{item['title']}]({item['url']})")
        msg.append("\n")

    if news_chsi:
        msg.append("### ☀️ 阳光高考 (CHSI)")
        for item in news_chsi:
            msg.append(f"- [{item['title']}]({item['url']})")
        msg.append("\n")

    msg.append("\n---")
    msg.append("*🔍 三源追踪，近十日重点资讯。请以官方发布为准。*")
    
    final_content = "\n".join(msg)
    
    # 3. 发送
    send_push(final_content)

if __name__ == "__main__":
    main()
