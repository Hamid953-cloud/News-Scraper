"""
Sources configuration.
Each source defines its homepage URL and the CSS selectors needed to find
article links, headlines, and dates on that specific site.

NOTE: If a source returns 0 articles, the site's HTML likely changed.
Fix: open the URL in your browser, right-click a headline -> Inspect,
find the <a> tag's attributes/class, and update "primary_selector" below.
"""

SOURCES = [
    {
        "name": "BBC News",
        "url": "https://www.bbc.com/news",
        "primary_selector": 'a[data-testid="internal-link"]',
        "fallback_selectors": ["a.gs-c-promo-heading"],
        "headline_attrs": {"data-testid": "card-headline"},
        "date_attrs": {"data-testid": "card-metadata-lastupdated"},
        "base_url": "https://www.bbc.com",
    },
    {
        "name": "Dawn News",
        "url": "https://www.dawn.com/",
        "primary_selector": "article.story a.story__link",
        "fallback_selectors": ["h2.story__title a", "article a"],
        "headline_attrs": None,  # no separate headline tag -> use link's own text
        "date_attrs": None,
        "base_url": "https://www.dawn.com",
    },
    {
        "name": "Al Jazeera",
        "url": "https://www.aljazeera.com/",
        "primary_selector": "a.u-clickable-card__link",
        "fallback_selectors": ["article a", "h3 a"],
        "headline_attrs": None,
        "date_attrs": None,
        "base_url": "https://www.aljazeera.com",
    },
]
