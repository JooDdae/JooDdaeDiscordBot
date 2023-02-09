from typing import Any, Literal
import urllib.parse
import requests

from constants import REQUESTS_TIMEOUT


headers = { "Content-Type": "application/json" }


async def get_problems(query: str, sort: str = "random", count: int = 1) -> Literal[-1, -2] | Any:
    query = urllib.parse.quote(query)
    res = requests.get(f"https://solved.ac/api/v3/search/problem?query={query}&sort={sort}", headers=headers, timeout=REQUESTS_TIMEOUT)
    if res.status_code != 200:
        return -1

    problems = res.json()
    if problems["count"] == 0:
        return -2

    return problems["items"][:count]
