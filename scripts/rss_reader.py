import feedparser
import json
import os
from datetime import datetime
from pathlib import Path

# -------------------------
# Config
# -------------------------
RSS_FEEDS = [
    "http://www.nature.com/nature/current_issue/rss",
    "https://www.science.org/action/showFeed?type=etoc&feed=rss&jc=science",
    "https://www.science.org/action/showFeed?type=etoc&feed=rss&jc=sciadv",
    "https://www.nature.com/ngeo.rss",
    "https://www.nature.com/ncomms.rss",
    "https://www.nature.com/natrevearthenviron.rss",
    "https://www.pnas.org/action/showFeed?type=searchTopic&taxonomyCode=topic&tagCode=earth-sci",
    "https://www.annualreviews.org/rss/content/journals/earth/latestarticles?fmt=rss",
    "https://rss.sciencedirect.com/publication/science/00128252",
    "https://rss.sciencedirect.com/publication/science/0012821X",
    "https://agupubs.onlinelibrary.wiley.com/feed/19448007/most-recent",
    "https://agupubs.onlinelibrary.wiley.com/feed/21699356/most-recent",
    "https://agupubs.onlinelibrary.wiley.com/feed/15252027/most-recent",
    "https://rss.sciencedirect.com/publication/science/00167037"
]

SEEN_FILE = Path("state/seen.json")
OUTPUT_FILE = Path("output/daily.md")


# -------------------------
# Load / Save Seen IDs
# -------------------------
def load_seen():
    SEEN_FILE.parent.mkdir(exist_ok=True, parents=True)
    if not SEEN_FILE.exists() or SEEN_FILE.stat().st_size == 0:
        return set()
    with open(SEEN_FILE, "r", encoding="utf-8") as f:
        return set(json.load(f))


def save_seen(seen):
    with open(SEEN_FILE, "w", encoding="utf-8") as f:
        json.dump(list(seen), f, indent=2)


# -------------------------
# Fetch New RSS Entries
# -------------------------
def fetch_new_entries():
    seen = load_seen()
    new_entries = []

    for url in RSS_FEEDS:
        feed = feedparser.parse(url)
        source_name = feed.feed.get("title", url)
        for entry in feed.entries:
            uid = entry.get("id") or entry.get("link")
            if not uid or uid in seen:
                continue

            new_entries.append({
                "source": source_name,
                "title": entry.get("title", "No title"),
                "link": entry.get("link", ""),
                "summary": entry.get("summary", "").replace("\n", " ").strip()
            })
            seen.add(uid)

    save_seen(seen)
    return new_entries, len(seen)


# -------------------------
# Group by Source
# -------------------------
def group_by_source(entries):
    groups = {}
    for item in entries:
        groups.setdefault(item["source"], []).append(item)
    return groups


# -------------------------
# Write Markdown
# -------------------------
def write_markdown(entries, total_seen):
    today = datetime.utcnow().strftime("%Y-%m-%d")
    new_count = len(entries)

    OUTPUT_FILE.parent.mkdir(exist_ok=True, parents=True)

    md = f"# Daily Paper Digest — {today}\n\n"
    md += f"**今日新增论文**：{new_count}\n"
    md += f"已累计收录：{total_seen} 篇\n\n"
    md += "---\n\n"

    if not entries:
        md += "今天没有新增论文。\n"
    else:
        md += "**摘要整理**：\n"
        md += "今日新增论文条目已按来源分类并生成概要。\n\n"
        grouped = group_by_source(entries)
        for source, items in grouped.items():
            md += f"## {source}\n\n"
            for item in items:
                md += f"- **{item['title']}**  \n"
                md += f"  🔗 {item['link']}\n"
                if item["summary"]:
                    md += f"  📝 {item['summary']}\n"
                md += "\n"

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write(md)


# -------------------------
# Main
# -------------------------
if __name__ == "__main__":
    entries, total_seen = fetch_new_entries()
    write_markdown(entries, total_seen)
    print(f"Done! New entries: {len(entries)}, Total seen: {total_seen}")
