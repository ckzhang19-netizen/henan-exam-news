import requests
import datetime
import os
import sys

# PushPlus Token
TOKEN = os.environ.get("PUSHPLUS_TOKEN")

def get_current_date():
    return datetime.datetime.now().strftime("%Y-%m-%d")

def generate_search_query():
    """生成高精准度的搜索查询"""
    # 核心关键词：定位地区和事件
    main_keywords = "河南 高考 中考 招生"
    # 权威来源：确保结果可靠性
    source_keywords = '"河南省教育考试院" OR "河南省教育厅" OR "阳光高考"'
    # 附加时间要求：获取最新信息
    time_modifier = "最新通知"
    
    # 最终的搜索引擎查询字符串
    query = f"{main_keywords} ({source_keywords}) {time_modifier}"
    
    return query

def format_search_results(query_string, results):
    """格式化报告内容"""
    if not results:
        return f"搜索引擎未找到与 '{query_string}' 相关的最新权威资讯。"
    
    # 构建 Markdown 格式报告
    msg = [f"## 🔍 搜索引擎招考日报 ({get_current_date()})", "---"]
    msg.append(f"### 搜索关键词：{query_string}")
    msg.append("\n")
    
    for i, item in enumerate(results[:15]): # 只展示前15条最相关的结果
        msg.append(f"#### {i+1}. {item['title']}")
        msg.append(f"- 来源: {item['source']}")
        msg.append(f"- 链接: [点击查看]({item['url']})\n")
    
    msg.append("---")
    msg.append("*💡 结果来自搜索引擎实时聚合，请核实官方来源。*")
    
    return "\n".join(msg)

def send_push(title, content):
    """发送到微信 (与主程序相同)"""
    if not TOKEN: sys.exit(1)
    url = 'http://www.pushplus.plus/send'
    data = {"token": TOKEN, "title": title, "content": content, "template": "markdown"}
    
    try:
        requests.post(url, json=data, timeout=15)
    except requests.exceptions.RequestException as e:
        print(f"发送微信失败，连接错误或超时。错误信息: {e}")

# ----------------------------------------------------
# 模拟搜索引擎获取结果（由于我们无法直接调用外部搜索引擎API，此处为模拟结构）
# 实际使用时，您需要将此部分替换为可用的搜索引擎 API 调用或 Google/Baidu 网页爬取逻辑
# ----------------------------------------------------
def fetch_and_run_search():
    query = generate_search_query()
    
    # --- 模拟结果 START ---
    # 在实际部署中，你需要用 Google/Baidu 搜索结果填充这个列表
    mock_results = [
        {"title": "河南省2025年普通高考政策解读 - 阳光高考", "source": "阳光高考信息平台", "url": "http://example.chsi.com/2025/abc"},
        {"title": "关于2025年中考招生考试工作安排的通知 - 河南省教育厅", "source": "河南省教育厅官网", "url": "http://example.jyt.henan.gov.cn/2025/xyz"},
        {"title": "最新！我省高职单招报名时间确定 - 河南省教育考试院", "source": "河南省教育考试院", "url": "http://example.haeea.cn/2025/123"}
    ]
    # --- 模拟结果 END ---

    final_content = format_search_results(query, mock_results)
    send_push("搜索引擎招考日报", final_content)

if __name__ == "__main__":
    # 在您的 GitHub Actions 中，这一步会执行搜索并发送报告
    fetch_and_run_search()
