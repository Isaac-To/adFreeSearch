import requests
from bs4 import BeautifulSoup
from fake_useragent import UserAgent

def linkRequester(url):
    req = requests.get(url, headers = randomAgent())
    if req.status_code not in range(200, 299):
        # try again one more time
        req = requests.get(url, headers = randomAgent())
    # print(req.status_code, url)
    return BeautifulSoup(req.text, "html.parser")

def randomAgent():
    ua = UserAgent()
    header = {'User-Agent': str(ua.random)}
    return header