from bs4 import BeautifulSoup
from fake_useragent import UserAgent
from flask import render_template
from urllib import parse
import aiohttp
from time import time
import asyncio

async def linkRequester(url):
    """
    It takes a URL, makes a request to that URL, and returns the HTML of the page
    
    :param url: The URL to be scraped
    :return: A BeautifulSoup object
    """
    startTime = time()
    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers = await randomAgent()) as response:
            print(f"Response from {parse.urlparse(url).hostname} in {round(time() - startTime, 5)}s")
            return BeautifulSoup(await response.text(), "html.parser")

async def randomAgent():
    """
    It returns a random user agent from the user_agents library
    :return: A dictionary with a key of User-Agent and a value of a random user agent.
    """
    ua = UserAgent()
    header = {'User-Agent': str(ua.random)}
    return header

async def resultsToHTML(resultsDict):
    """
    It takes a dictionary of results and returns a string of HTML
    
    :param resultsDict: A dictionary of results from the search engine
    :return: The resultsDict is being returned as a string of HTML.
    """
    outputHTML = ''
    for r in resultsDict:
        buildHTML = render_template(
            "singleResult.html", title=parse.unquote(r['title']), link=parse.unquote(r['link']), source=', '.join(r["source"]), summary=parse.unquote(r["summary"]))
        outputHTML += buildHTML
    return outputHTML

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

async def merge(a, b):
    c = []
    while len(a) != 0 and len(b) != 0:
        if len(a[0].get('source')) > len(b[0].get('source')):
            c.append(a.pop(0))
        else:
            c.append(b.pop(0))
    while len(a) != 0:
        c.append(a.pop(0))
    while len(b) != 0:
        c.append(b.pop(0))
    return c

async def msort(c):
    if len(c) > 1:
        aTask = asyncio.create_task(msort(c[:int(len(c) / 2)]))
        bTask = asyncio.create_task(msort(c[int(len(c) / 2):]))
        return await merge(await aTask, await bTask)
    else: return c

async def relevancyByOccurances(listOfResults):
    """
    It takes a list of results, and returns a list of results, but with the results sorted by how many
    sources they came from
    
    :param listOfResults: A list of dictionaries, each dictionary containing the following keys:
    :return: A list of dictionaries.
    """
    # combines the results if they have the same link
    for i in range(len(listOfResults)):
        offset = 0
        for j in range(i + 1, len(listOfResults)):
            if listOfResults[i].get('link') == listOfResults[j - offset].get("link") and listOfResults[j - offset]['source'] is not None:
                # only append if not already in the list
                for source in listOfResults[j - offset].get("source"):
                    if source not in listOfResults[i]['source']:
                        listOfResults[i]['source'].append(source)
                # removes the entry in the list
                listOfResults.pop(j - offset)
                offset += 1
    return await msort(listOfResults)
    
async def linkFormatter(link):
    if not link.startswith('http'):
        link = 'https://' + link
    if link.endswith("..."):
        link = link[:-3]
    if link.endswith('/'):
        link = link[:-1]
    return link