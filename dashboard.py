"""
Web Dashboard for the News Scraper.
Run with: python dashboard.py
It will automatically open http://localhost:5000 in your browser.
"""

import os
import threading
import webbrowser

from flask import Flask, render_template, request

import database
import duplicates

app = Flask(__name__)


def open_browser():
    webbrowser.open("http://localhost:5000")


@app.route("/")
def home():
    keyword = request.args.get("q", "").strip()
    source = request.args.get("source", "").strip()

    articles = database.search_articles(keyword=keyword, source=source)
    all_sources = database.get_sources()
    total = database.count_articles()

    return render_template(
        "dashboard.html",
        articles=articles,
        total=total,
        shown=len(articles),
        keyword=keyword,
        selected_source=source,
        all_sources=all_sources,
    )


@app.route("/analytics")
def analytics():
    source_counts = database.get_source_counts()
    daily_counts = database.get_daily_counts(days=7)
    total = database.count_articles()

    return render_template(
        "analytics.html",
        total=total,
        source_labels=[row[0] for row in source_counts],
        source_values=[row[1] for row in source_counts],
        daily_labels=[row[0] for row in daily_counts],
        daily_values=[row[1] for row in daily_counts],
    )


@app.route("/related")
def related():
    articles = database.get_all_articles()
    clusters = duplicates.find_related_stories(articles)

    return render_template(
        "related.html",
        clusters=clusters,
        cluster_count=len(clusters),
    )


if __name__ == "__main__":
    database.init_db()

    # Flask's debug reloader runs this file TWICE (once as a watcher process,
    # once as the real server). WERKZEUG_RUN_MAIN is only set on the real
    # one, so we check it to avoid opening the browser twice.
    if os.environ.get("WERKZEUG_RUN_MAIN") == "true":
        threading.Timer(1.0, open_browser).start()

    # host="0.0.0.0" lets you open this from your phone too, as long as
    # it's connected to the SAME WiFi network as this computer.
    app.run(host="0.0.0.0", port=5000, debug=True)
