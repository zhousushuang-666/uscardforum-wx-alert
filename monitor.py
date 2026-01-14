import requests
import re
import os
import time

# -----------------------------
# 配置
TOPIC_URL = "https://www.uscardforum.com/t/topic/240330.json"
STATE_FILE = "last_post_id.txt"        # 记录上一次抓取的帖子 ID
WX_APP_TOKEN = os.environ.get("WX_APP_TOKEN")
WX_UID = os.environ.get("WX_UID")

# 关键词列表，可根据需要修改
KEYWORDS = [
    r"JFK",
    r"开卡",
    r"instant approval",
    r"\bDP\b",
    r"成功",
    r"秒批"
]

# -----------------------------
# 函数：读取上一次帖子 ID
def load_last_id():
    if os.path.exists(STATE_FILE):
        try:
            return int(open(STATE_FILE).read())
        except:
            return 0
    return 0

# 函数：保存最新帖子 ID
def save_last_id(pid):
    open(STATE_FILE, "w").write(str(pid))

# 函数：发送微信通知
def send_wx(title, content):
    try:
        url = "https://wxpusher.zjiecode.com/api/send/message"
        payload = {
            "appToken": WX_APP_TOKEN,
            "content": content,
            "summary": title,
            "uids": [WX_UID],
            "contentType": 1
        }
        requests.post(url, json=payload)
    except Exception as e:
        print(f"微信推送失败: {e}")

# -----------------------------
# 主逻辑
last_id = load_last_id()

# 在 URL 加时间戳，避免缓存
url = f"{TOPIC_URL}?ts={int(time.time())}"
try:
    resp = requests.get(url, timeout=15)
    resp.raise_for_status()
except Exception as e:
    print(f"请求帖子失败: {e}")
    exit(1)

try:
    data = resp.json()
except Exception as e:
    print(f"JSON解析失败: {e}")
    exit(1)

# 获取帖子回复列表
posts = data.get("post_stream", {})._
