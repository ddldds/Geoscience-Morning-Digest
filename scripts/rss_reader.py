import feedparser
import json
import os
from datetime import datetime

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

SEEN_FILE = "seen/seen.json"
OUTPUT_FILE = "output/daily.md"


def load_seen():
    if not os.path.exists(SEEN_FILE):
        return set()
    try:
        with open(SEEN_FILE, "r") as f:
            data = f.read().strip()
            if not data:
                return set()
            return set(json.loads(data))
    except:
        return set()


def save_seen(seen):
    with open(SEEN_FILE, "w") as f:
        json.dump(list(seen), f, indent=2)


def fetch_new_entries():
    seen = load_seen()
    new_entries = []

    for url in RSS_FEEDS:
        feed = feedparser.parse(url)
        source_name = feed.feed.get("title", "Unknown Source")

        for entry in feed.entries:
            uid = entry.get("id") or entry.get("link")
            if not uid:
                continue
                
            if uid in seen:
                continue  # 已经抓过

            title = entry.get("title", "No title")
            link = entry.get("link", "")
            summary = entry.get("summary", "").strip()

            new_entries.append({
                "source": source_name,
                "title": title,
                "link": link,
                "summary": summary
            })

            seen.add(uid)

    save_seen(seen)
    return new_entries


def group_by_source(entries):
    groups = {}
    for item in entries:
        source = item["source"]
        groups.setdefault(source, []).append(item)
    return groups


def write_markdown(entries):

    today = datetime.utcnow().strftime("%Y-%m-%d")
    
    md = f"# Daily Paper Digest — {today}\n\n"

    if not entries:
        md += "今天没有新增内容。\n"
    else:
        grouped = group_by_source(entries)
        
        for source, items in grouped.items():
            md += f"## {source}\n\n"
            for item in items:
                md += f"- **{item['title']}**  \n"
                md += f"  🔗 {item['link']}\n"
                if item['summary']:
                    clean_sum = item["summary"].replace("\n", " ").strip()
                    md += f"  📝 {clean_sum}\n"
                md += "\n"

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write(md)


if __name__ == "__main__":
    entries = fetch_new_entries()
    write_markdown(entries)
