"""
Keyword Alerts
Checks newly scraped articles against your KEYWORDS list (alert_config.py)
and emails you when there's a match.
"""

import logging
import smtplib
from email.mime.text import MIMEText

import alert_config


def find_matches(articles: list[dict]) -> list[dict]:
    """Return the subset of articles whose title contains any keyword
    from alert_config.KEYWORDS (case-insensitive)."""
    if not alert_config.KEYWORDS:
        return []

    matches = []
    for article in articles:
        title_lower = article["title"].lower()
        for keyword in alert_config.KEYWORDS:
            if keyword.lower() in title_lower:
                matches.append(article)
                break  # don't add the same article twice if it matches 2 keywords
    return matches


def send_email_alert(matched_articles: list[dict]):
    """Send one email listing all matched articles from this run."""
    if not matched_articles:
        return

    subject = f"🔔 News Alert: {len(matched_articles)} new article(s) match your keywords"

    lines = []
    for a in matched_articles:
        lines.append(f"[{a['source']}] {a['title']}\n{a['link']}\n")
    body = "\n".join(lines)

    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = alert_config.EMAIL_ADDRESS
    msg["To"] = alert_config.RECIPIENT_EMAIL

    try:
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login(alert_config.EMAIL_ADDRESS, alert_config.EMAIL_APP_PASSWORD)
            server.send_message(msg)
        logging.info(f"Alert email sent for {len(matched_articles)} matching article(s)")
    except Exception as e:
        # Never let an email failure crash the scraper — just log it
        logging.error(f"Failed to send alert email: {e}", exc_info=True)


def check_and_alert(articles: list[dict]):
    """Convenience function: find matches in `articles` and email if any found."""
    matches = find_matches(articles)
    if matches:
        logging.info(f"Keyword match found in {len(matches)} article(s), sending alert...")
        send_email_alert(matches)
