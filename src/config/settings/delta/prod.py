"""
Small delta for production.

Only put the *differences* here; everything else is inherited.
"""

DEBUG = False

# Security-minded defaults — override via ENV/.env if needed
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_BROWSER_XSS_FILTER = True  # Django may deprecate some headers over time
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_HSTS_SECONDS = 60 * 60 * 24 * 30  # 30 days
SECURE_HSTS_INCLUDE_SUBDOMAINS = False
SECURE_HSTS_PRELOAD = False
