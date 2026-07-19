# News Scraper (v2) — BBC News

Scrapes **Title**, **Date**, and **Link** from BBC News and saves them into a
**SQLite database** (`articles.db`), automatically skipping duplicates you've
already scraped before.

## Setup

```bash
# 1. Create and activate a virtual environment
python3 -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run the scraper
python scraper.py
```

You should see output like:
```
Fetching https://www.bbc.com/news ...
Extracting articles ...
Found 42 articles on the page
Added 42 NEW articles to the database
(Skipped 0 already-seen duplicates)
Total articles stored so far: 42

Most recent 5 in DB:
- Some headline here  |  3 hrs ago  |  https://www.bbc.com/news/articles/xxxx
```

**Run it again** a few minutes later — you'll see something like
`Added 3 NEW articles` and `Skipped 39 already-seen duplicates`, because the
`link` column is UNIQUE in the database, so re-scraping never creates repeats.

### Peek inside the database
```bash
sqlite3 articles.db "SELECT title, date FROM articles LIMIT 5;"
```
Or use a free GUI tool like **DB Browser for SQLite** to view it visually.

## If it finds 0 articles (selectors broke)

News sites redesign their HTML often — this is the #1 thing that breaks scrapers.
Here's how to fix it in under a minute:

1. Open https://www.bbc.com/news in Chrome/Firefox
2. Right-click a headline → **Inspect**
3. Look at the `<a>` tag wrapping the headline — note its attributes
   (e.g. `data-testid="internal-link"` or a `class="..."`)
4. Update the selector in `extract_articles()` in `scraper.py`:
   ```python
   candidates = soup.select('a[data-testid="internal-link"]')  # <-- update this line
   ```
5. Do the same for the date element if needed.

## Project Roadmap

- [x] v1: Scrape Title, Date, Link → CSV
- [x] v2: Store in SQLite + deduplicate articles (this version)
- [ ] v3: Scheduling (run automatically every N minutes)
- [ ] v4: Multi-source support (Dawn, Al Jazeera, etc.)
- [ ] v5: Search/filter + simple web dashboard
