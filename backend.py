import sqlite3
import feedparser
import time
import datetime
import hashlib
from flask import Flask, jsonify, request
from flask_cors import CORS
import threading

DB_FILE = "news_database.db"

def init_db():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS sources (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            url TEXT NOT NULL,
            category TEXT NOT NULL,
            language TEXT NOT NULL,
            last_sync TEXT
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS articles (
            id TEXT PRIMARY KEY,
            title TEXT NOT NULL,
            summary TEXT,
            source_name TEXT NOT NULL,
            source_id TEXT NOT NULL,
            link TEXT UNIQUE NOT NULL,
            published_at TEXT,
            fetched_at TEXT,
            category TEXT,
            language TEXT,
            FOREIGN KEY (source_id) REFERENCES sources(id)
        )
    ''')
    default_sources = [
        ("bbc-world", "BBC World News", "http://feeds.bbci.co.uk/news/world/rss.xml", "Svět", "en", None),
        ("technology-org", "Technology Org", "https://www.technology.org/feed/", "Technologie", "en", None),
        ("sci-news", "Sci-News", "http://feeds.feedburner.com/science-news", "Věda", "en", None)
    ]
    cursor.executemany('''
        INSERT OR IGNORE INTO sources (id, name, url, category, language, last_sync) 
        VALUES (?, ?, ?, ?, ?, ?)
    ''', default_sources)
    conn.commit()
    conn.close()

def fetch_and_normalize_news():
    print("Synchronizuji RSS kanály...")
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, url, category, language FROM sources")
    sources = cursor.fetchall()
    
    for src_id, src_name, src_url, src_category, src_lang in sources:
        try:
            feed = feedparser.parse(src_url)
            for entry in feed.entries:
                link = entry.get('link', '')
                if not link: continue
                article_id = hashlib.md5(link.encode('utf-8')).hexdigest()
                title = entry.get('title', 'Bez názvu')
                summary = entry.get('summary', entry.get('description', ''))
                import re
                summary = re.sub('<[^<]+?>', '', summary)[:300]
                published = entry.get('published', '')
                fetched_at = datetime.datetime.now(datetime.timezone.utc).isoformat()
                
                try:
                    cursor.execute('''
                        INSERT INTO articles 
                        (id, title, summary, source_name, source_id, link, published_at, fetched_at, category, language)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (article_id, title, summary, src_name, src_id, link, published, fetched_at, src_category, src_lang))
                except sqlite3.IntegrityError:
                    continue
            
            current_time = datetime.datetime.now(datetime.timezone.utc).isoformat()
            cursor.execute("UPDATE sources SET last_sync = ? WHERE id = ?", (current_time, src_id))
        except Exception as e:
            print(f"Chyba při stahování {src_name}: {e}")
            
    conn.commit()
    conn.close()
    print("Synchronizace hotova.")

app = Flask("NewsAggregatorBackend")
CORS(app)

@app.route('/api/news', methods=['GET'])
def get_news():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM articles ORDER BY fetched_at DESC LIMIT 50")
    articles = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return jsonify(articles)

if __name__ == '__main__':
    init_db()
    fetch_and_normalize_news()
    app.run(host='0.0.0.0', port=5000)
