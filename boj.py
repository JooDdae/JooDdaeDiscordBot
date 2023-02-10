from typing import Optional
from datetime import datetime as dt
import re
from bs4 import BeautifulSoup
import requests

from constants import REQUESTS_TIMEOUT


headers = {"User-Agent": "JooDdae Bot"}

shared_id_prog = re.compile(r"[0-9a-f]{32}")


async def get_accepted_submission(user_id: str, problem_id: int) -> int:
    url = f"https://www.acmicpc.net/status?problem_id={problem_id}&user_id={user_id}&result_id=4"
    page = requests.get(url, headers=headers, timeout=REQUESTS_TIMEOUT)

    soup = BeautifulSoup(page.content, "html.parser")
    if len(soup.select("tbody > tr")) == 0:
        return -1

    return int(soup.select("tbody > tr")[-1].select("td")[0].text)

async def get_shared_source(share_url: str) -> Optional[tuple[str, str]]:
    share_id = share_url
    if share_url[:37] == "https://www.acmicpc.net/source/share/":
        share_id = share_url[37:]
    elif share_url[:14] == "http://boj.kr/":
        share_id = share_url[14:]
    elif shared_id_prog.fullmatch(share_url) is None:
        return None

    url = f"https://www.acmicpc.net/source/share/{share_id}"
    page = requests.get(url, headers=headers, timeout=REQUESTS_TIMEOUT)
    if page.status_code != 200:
        return None

    soup = BeautifulSoup(page.content, "html.parser")
    input_string = soup.select("div.sample-source > div.form-group > div.col-md-12 > textarea")[0].text
    problem_info = soup.select("div.breadcrumbs > div.container")[0].text.split()

    return (str(problem_info[-1]), input_string)

async def get_user(boj_id: str) -> Optional[str]:
    url = f"https://www.acmicpc.net/user/{boj_id}"
    page = requests.get(url, headers=headers, timeout=REQUESTS_TIMEOUT)
    if page.status_code != 200:
        return None

    return ""

async def get_submit_time(submit_id: int) -> Optional[dt]:
    url = f"https://www.acmicpc.net/status?top={submit_id}"
    page = requests.get(url, headers=headers, timeout=REQUESTS_TIMEOUT)
    if page.status_code != 200:
        return None

    soup = BeautifulSoup(page.content, "html.parser")
    if len(soup.select("tbody > tr")) == 0:
        return None

    return dt.strptime(str(soup.select("tbody > tr")[0].select("td")[-1].select('a')[0]['title']), "%Y-%m-%d %H:%M:%S")