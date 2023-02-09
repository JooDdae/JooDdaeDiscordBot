headers = {"User-Agent":"JooDdae Bot"}

async def first_ac_submission(user_id, problem_id):
    import requests
    from bs4 import BeautifulSoup
    
    URL = "https://www.acmicpc.net/status?problem_id=" + str(problem_id) + "&user_id=" + user_id + "&result_id=4"
    page = requests.get(URL, headers=headers)
    soup = BeautifulSoup(page.content, "lxml")
    if len(soup.select("tbody > tr")) == 0 :
        return -1
    return int(soup.select("tbody > tr")[-1].select("td")[0].text)

async def submit_id_code(url):
    import requests
    page = requests.get(url, headers=headers)

    if page.status_code != 200:
        return ["-1", "-1"]

    from bs4 import BeautifulSoup
    soup = BeautifulSoup(page.content, 'html.parser')

    input_string = soup.select("div.sample-source > div.form-group > div.col-md-12 > textarea")[0].text
    problem_info = soup.select("div.breadcrumbs > div.container")[0].text.split()

    return [str(problem_info[-1]), input_string]