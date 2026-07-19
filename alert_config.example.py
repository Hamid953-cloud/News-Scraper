"""
Alert Configuration TEMPLATE.

Setup instructions:
1. Copy this file and rename the copy to: alert_config.py
2. Fill in your own Gmail address, App Password, and keywords below.
3. alert_config.py is in .gitignore, so it will NEVER be uploaded to GitHub.
"""

# --- Gmail settings ---
EMAIL_ADDRESS = "youraddress@gmail.com"      # the Gmail account SENDING the alert
EMAIL_APP_PASSWORD = "xxxx xxxx xxxx xxxx"   # 16-character Gmail App Password (not your normal password)
RECIPIENT_EMAIL = "youraddress@gmail.com"    # where alerts should be sent

# --- Keywords to watch ---
# Case-insensitive. An article triggers an alert if its title contains
# ANY of these words/phrases.
KEYWORDS = [
    # "Pakistan",
    # "cricket",
    # "AI",
]