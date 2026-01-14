import requests
import re
import os

TOPIC_URL = "https://www.uscardforum.com/t/topic/240330.json"
STATE_FILE = "last_post_id.txt"

WX_APP_TOKEN = os.environ.get("WX_APP_TOKEN")
WX_UID = os.environ.get("WX_UID")

KEYWORDS = [
    r"approved",
    r"instant approval",
    r"\bDP\b",
    r"漏洞",
    r"成功",
    r"秒批"
]

def load_last_id():
    if os.path.exists(STATE_FILE):
        return int(open(STATE_FILE).read())
    return 0

def save_last_id(pid):
    open(STATE_FILE, "w").write(str(pid))

def send_wx(title, content):
    url = "https://wxpusher.zjiecode.com/api/send/message"
    payload = {
        "appToken": WX_APP_TOKEN,
        "content": content,
        "summary": title,
        "uids": [WX_UID],
        "contentType": 1
    }
    requests.post(url, json=payload)

last_id = load_last_id()

data = requests.get(TOPIC_URL).json()
posts = data["post_stream"]["posts"]

for p in posts:
    pid = p["id"]
    if pid <= last_id:
        continue

    text = re.sub("<.*?>", "", p["cooked"])
    for kw in KEYWORDS:
        if re.search(kw, text, re.I):
            highlight = re.sub(
                kw,
                lambda m: f"【{m.group(0)}】",
                text,
                flags=re.I
            )
            send_wx(
                "⚠️ USCardForum 关键词命中",
                f"作者：{p['username']}\n\n{highlight[:800]}"
            )
            break

    save_last_id(pid)
