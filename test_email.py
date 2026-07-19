"""
Test script — sends ONE fake alert email immediately, to verify your
Gmail App Password and settings in alert_config.py are working correctly.
This does NOT touch your real articles database.

Run: python test_email.py
"""

import alerts

fake_articles = [
    {
        "title": "TEST: New AI breakthrough announced today",
        "source": "Test Source",
        "link": "https://example.com/test-article",
    }
]

print("Sending a test alert email...")
alerts.send_email_alert(fake_articles)
print("Done. Check your inbox (and Spam folder) in the next minute or two.")
print("If nothing arrives, check the error printed above, or scraper.log")