# app/middleware/rate_limiter.py
# ПР6: Артем — Rate Limiting, захист від Brute Force

from slowapi import Limiter
from slowapi.util import get_remote_address

# Ідентифікує клієнта за IP-адресою
limiter = Limiter(key_func=get_remote_address)
