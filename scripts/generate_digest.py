# scripts/generate_digest.py
import os
import json
import requests
from datetime import datetime

# 路径设置
DAILY_MD_PATH = "output/daily.md"
SEEN_JSON_PATH = "state/seen.json"

# 从 seen.json 里读取已有记录
with open(SEEN_JSON_PATH, "r", encoding="utf-8") as f:
    seen = json.load(f)

# 如果 seen.json 是 dict，转成 list 方便统一处理
if isinstance(seen, dict):
    seen_list = list(seen.values())
else:
    seen_list = seen

# 今天日期
today = datetime.now().strftime("%Y-%m-%d")

# 收集当天的新论文（如果没有新论文也收集全部，用于生成摘要）
papers = []
for paper in seen_list:
    title = paper.get("title") if isinstance(paper, dict) else str(paper)
    source = paper.get("source") if isinstance(paper, dict) else "未知来源"
    paper_date = paper.get("date") if isinstance(paper, dict) else today
    papers.append(f"- {title} ({source})")

# 生成摘要
print(f"Generating digest for {len(papers)} papers...")

# DeepSeek API 配置
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")
if not DEEPSEEK_API_KEY:
    print("未检测到 DEEPSEEK_API_KEY，摘要将不会生成。")
    digest = "未设置 DeepSeek API Key，无法生成摘要。"
else:
    url = "https://api.deepseek.ai/v1/generate"  # 替换为 DeepSeek 官方 endpoint
    payload = {
        "prompt": (
            f"你是一名地球科学领域的专业科研助手。\n\n"
            f"下面是论文列表，请你完成以下任务：\n"
            "1）提炼论文整体趋势\n"
            "2）用学术语言生成一个“论文晨报”，适合科研工作者快速阅读\n"
            "3）按主题自动分类（如构造、地球化学、地球动力学等）\n"
            "4）每篇论文总结一句话核心贡献\n"
            "5）最后附上原始条目列表\n\n"
            f"今天日期：{today}\n\n"
            "以下是论文条目：\n\n" +
            "\n".join(papers) +
            "\n\n请严格输出 Markdown 格式。"
        ),
        "model": "text-summary"
    }
    headers = {
        "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
        "Content-Type": "application/json"
    }

    try:
        resp = requests.post(url, json=payload, headers=headers)
        resp.raise_for_status()
        digest = resp.json().get("text", "未能生成摘要")
    except Exception as e:
        digest = f"摘要生成失败: {e}"

# 写入 daily.md
if os.path.exists(DAILY_MD_PATH):
    with open(DAILY_MD_PATH, "r", encoding="utf-8") as f:
        daily_md = f.read()
else:
    daily_md = ""

# 在 markdown 顶部加摘要
new_content = f"# Daily Paper Digest — {today}\n\n**论文总数**：{len(papers)}\n\n**摘要整理**：\n{digest}\n\n---\n\n"

# 保留原有内容
new_content += daily_md

with open(DAILY_MD_PATH, "w", encoding="utf-8") as f:
    f.write(new_content)

print("Markdown file updated.")
