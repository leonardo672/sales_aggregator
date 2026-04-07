import time
import requests

CACHE_TTL = 3600

_cache = {
    "rate": None,
    "timestamp": 0
}


def get_usd_rate():
    now = time.time()

    if _cache["rate"] and now - _cache["timestamp"] < CACHE_TTL:
        return _cache["rate"]

    try:
        resp = requests.get("https://www.cbr-xml-daily.ru/daily_json.js")
        data = resp.json()

        rate = data["Valute"]["USD"]["Value"]

        _cache["rate"] = rate
        _cache["timestamp"] = now

        return rate

    except Exception:
        raise Exception("Currency API unavailable")