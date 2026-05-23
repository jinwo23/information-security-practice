                                                                                                                                                                                                                                                       # app/validators/sanitizer.py
# ПР6: Влад — санітизація та перевірка вхідних даних

import bleach
import re


def sanitize_text(text: str) -> str:
    # Видаляє ВСІ HTML-теги через bleach — захист від XSS
    cleaned = bleach.clean(text, tags=[], strip=True)
    return cleaned.strip()


def contains_sql_patterns(text: str) -> bool:
    # Перевіряє SQL-патерни — захист від SQL Injection
    sql_patterns = [
        r"(\b(UNION|SELECT|INSERT|DELETE|DROP)\b)",
        r"(--|;\/\*|\*\/)",
        r"(\bOR\b\s+\b1\s*=\s*1\b)",
    ]
    for pattern in sql_patterns:
        if re.search(pattern, text, re.IGNORECASE):
            return True
    return False


def contains_xss_patterns(text: str) -> bool:
    # Перевіряє XSS-патерни у тексті
    xss_patterns = [
        r"<script[^>]*>",
        r"javascript\s*:",
        r"on\w+\s*=",
        r"<iframe[^>]*>",
    ]
    for pattern in xss_patterns:
        if re.search(pattern, text, re.IGNORECASE):
            return True
    return False