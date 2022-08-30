import requests
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
from flask import render_template
from urllib import parse

async def linkRequester(url):
    # print(url)
    req = requests.get(url, headers = await randomAgent())
    if req.status_code not in range(200, 299):
        # try again one more time
        req = requests.get(url, headers = await randomAgent())
    # print(req.status_code, url)
    return BeautifulSoup(req.text, "html.parser")

async def randomAgent():
    ua = UserAgent()
    header = {'User-Agent': str(ua.random)}
    return header

async def resultsToHTML(resultsDict):
    outputHTML = ''
    for r in resultsDict:
        buildHTML = render_template(
            "singleResult.html", title=r['title'], link=r['link'], source=r["source"], summary=r["summary"])
        outputHTML += buildHTML
    return outputHTML

async def imgResultsToHTML(resultsDict):
    outputHTML = ""
    for r in resultsDict:
        outputHTML += render_template('imageResults.html', link = r['link'], source = r["source"])
    return outputHTML

async def interlace(containsMultipleLists):
    newList = []
    j = 0
    while True:
        if j >= len(containsMultipleLists):
            j = 0
        for i in range(len(containsMultipleLists)):
            if len(containsMultipleLists[i]) > 0:
                break
        else:
            break
        if len(containsMultipleLists[j]) > 0:
            newList.append(containsMultipleLists[j].pop(0))
        j+=1
    return newList

async def relevancyByOccurances(listOfResults):
    rankings = {}
    for result in listOfResults:
        if rankings.get(result.get('link')):
            rankings[result.get('link')].append(result.get('source'))
        else:
            rankings[result.get('link')] = [result.get("source")]
    rankedList = []
    while len(rankings) > 0:
        max = [0, '']
        for link in rankings.keys():
            if len(rankings[link]) > max[0]:
                max[0] = len(rankings[link])
                max[1] = link
        for result in listOfResults:
            if result.get("link") == max[1]:
                rankedList.append(result)
                rankedList[-1]['source'] = ', '.join(rankings.pop(result.get("link")))
                break
    return rankedList
