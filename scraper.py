"""
News Scraper v4 - Multi-source
Scrapes: Title, Date, Link, Source from multiple news sites (see sources.py)
Saves results to SQLite (articles.db), skipping duplicates.
Logs every run to scraper.log for scheduled/background runs.
"""

import datetime
import logging
import os

import requests
from bs4 import BeautifulSoup

import database
import alerts
from sources import SOURCES

# Always resolve paths relative to THIS file, not the current working
# directory — important because Task Scheduler may run from a different folder.
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LOG_FILE = os.path.join(BASE_DIR, "scraper.log")

logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
)
# Also print to console when run manually
console = logging.StreamHandler()
console.setFormatter(logging.Formatter("%(message)s"))
logging.getLogger().addHandler(console)
HEADERS = {
    # Pretend to be a normal browser so the site doesn't block us
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    )
}


def fetch_page(url: str) -> BeautifulSoup:
    """Download a page and return a parsed BeautifulSoup object."""
    response = requests.get(url, headers=HEADERS, timeout=10)
    response.raise_for_status()  # crashes loudly if site blocks us / errors out
    return BeautifulSoup(response.text, "lxml")


def extract_articles(soup: BeautifulSoup, source: dict) -> list[dict]:
    """
    Find article cards on the page and pull Title, Date, Link using the
    selectors defined for this specific source in sources.py.

    NOTE: Sites change their HTML occasionally. If a source starts
    returning 0 articles, see the "How to fix selectors" section in README.md.
    """
    articles = []
    seen_links = set()

    candidates = soup.select(source["primary_selector"])
    if not candidates:
        for fallback in source.get("fallback_selectors", []):
            candidates = soup.select(fallback)
            if candidates:
                break
    if not candidates:
        candidates = soup.find_all("a", href=True)  # last resort, very loose

    for a_tag in candidates:
        link = a_tag.get("href", "").strip()
        if not link:
            continue

        # Make relative links absolute (e.g. "/news/world-123" -> full URL)
        if link.startswith("/"):
            link = source["base_url"] + link

        domain = source["base_url"].split("//")[-1].replace("www.", "")
        if domain not in link or link in seen_links:
            continue

        # Title: prefer a dedicated headline element inside the card,
        # fall back to the link's own text
        title_tag = a_tag.find(attrs=source["headline_attrs"]) if source.get("headline_attrs") else None
        title = title_tag.get_text(strip=True) if title_tag else a_tag.get_text(strip=True)

        if not title or len(title) < 8:  # skip empty/junk links (icons, "Home", etc.)
            continue

        # Date: use a dedicated timestamp element if this source has one,
        # otherwise record the scrape time so you always know when it was captured.
        date_tag = a_tag.find(attrs=source["date_attrs"]) if source.get("date_attrs") else None
        if date_tag:
            date = date_tag.get_text(strip=True)
        else:
            date = f"scraped:{datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}"

        seen_links.add(link)
        articles.append({"title": title, "date": date, "link": link, "source": source["name"]})

    return articles


def main():
    database.init_db()  # creates articles.db + table if not already there

    grand_total_new = 0
    grand_total_found = 0
    all_new_articles = []  # collected across all sources, for keyword alert check

    for source in SOURCES:
        try:
            logging.info(f"--- {source['name']} ---")
            logging.info(f"Fetching {source['url']} ...")
            soup = fetch_page(source["url"])

            articles = extract_articles(soup, source)
            logging.info(f"Found {len(articles)} articles on the page")

            newly_inserted = database.save_articles(articles)
            logging.info(f"Added {len(newly_inserted)} NEW articles")
            logging.info(f"(Skipped {len(articles) - len(newly_inserted)} already-seen duplicates)")

            grand_total_new += len(newly_inserted)
            grand_total_found += len(articles)
            all_new_articles.extend(newly_inserted)

        except Exception as e:
            # Catch per-source so ONE broken source doesn't stop the others
            # from being scraped. You'll always find the reason in scraper.log
            logging.error(f"{source['name']} run FAILED: {e}", exc_info=True)

    # Check ONLY the newly-inserted articles against your keyword list,
    # so you never get re-alerted for an article you've already seen.
    try:
        alerts.check_and_alert(all_new_articles)
    except Exception as e:
        logging.error(f"Keyword alert check FAILED: {e}", exc_info=True)

    total = database.count_articles()
    logging.info("=== Run summary ===")
    logging.info(f"Total new articles this run: {grand_total_new}")
    logging.info(f"Total articles stored overall: {total}")


if __name__ == "__main__":
    main()
