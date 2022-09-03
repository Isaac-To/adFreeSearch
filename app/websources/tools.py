from bs4 import BeautifulSoup
from fake_useragent import UserAgent
from flask import render_template
from urllib import parse
import aiohttp
import orjson
import asyncio
import uvloop

async def linkRequester(url):
    """
    It takes a URL, makes a request to that URL, and returns the HTML of the page
    
    :param url: The URL to be scraped
    :return: A BeautifulSoup object
    """
    async with aiohttp.ClientSession(json_serialize=orjson.dumps) as session:
        headers = await randomAgent() 
        async with session.get(url, headers=headers) as r:
            data = await r.text()
            return BeautifulSoup(data, "lxml")
        
asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())

async def randomAgent():
    """
    It returns a random user agent from the user_agents library
    :return: A dictionary with a key of User-Agent and a value of a random user agent.
    """
    ua = UserAgent()
    header = {'User-Agent': str(ua.random)}
    return header

asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())

async def resultsToHTML(resultsDict):
    """
    It takes a dictionary of results and returns a string of HTML
    
    :param resultsDict: A dictionary of results from the search engine
    :return: The resultsDict is being returned as a string of HTML.
    """
    outputHTML = ''
    for r in resultsDict:
        buildHTML = render_template(
            "singleResult.html", title=parse.unquote(r['title']), link=parse.unquote(r['link']), source=parse.unquote(r["source"]), summary=parse.unquote(r["summary"]))
        outputHTML += buildHTML
    return outputHTML

asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())

async def imgResultsToHTML(resultsDict):
    """
    It takes a dictionary of image results and returns a string of HTML
    
    :param resultsDict: A dictionary of results. Each result is a dictionary with the following keys:
    :return: A string of HTML code.
    """
    outputHTML = ""
    for r in resultsDict:
        outputHTML += render_template('imageResults.html', link = r['link'], source = r["source"])
    return outputHTML

asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())

async def interlace(containsMultipleLists):
    """
    It takes a list of lists and returns a list of the first elements of each list, then the second
    elements of each list, and so on
    
    :param containsMultipleLists: A list of lists
    :return: A list of all the elements in the list of lists, but in a different order.
    """
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

asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())

async def relevancyByOccurances(listOfResults):
    """
    It takes a list of results, and returns a list of results, but with the results sorted by how many
    sources they came from
    
    :param listOfResults: A list of dictionaries, each dictionary containing the following keys:
    :return: A list of dictionaries.
    """
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

asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())

def linkFormatter(link):
    if not link.startswith('http'):
        link = 'https://' + link
    if link.endswith("..."):
        link = link[:-3]
    if not link.endswith('/'):
        link += '/'
    return link