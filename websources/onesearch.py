from distutils.command.build import build
from .tools import linkRequester, linkFormatter
from urllib import parse
import asyncio

async def buildResults(rawResult):
    try:
        link = rawResult.find("span", class_="fz-ms").text
        link = linkFormatter(link)
        result = {
            'title': rawResult.find('h3', class_="title").text,
            'link': link,
            'source': 'onesearch.com',
            'summary': rawResult.find("p", class_="fz-ms").text,
        }
        return result
    except:
        return None

async def onesearchResults(params):
    """
    It takes a dictionary of parameters, and returns a list of dictionaries, each of which represents a
    search result from Onesearch
    
    :param params: a dictionary of parameters to be passed to the search engine
    :return: A list of dictionaries.
    """
    onesearchParams = params.copy()
    if params.get('start') != 0:
        onesearchParams['b'] = params.get("start") + 1
    del onesearchParams['start']
    soup = await linkRequester('https://www.onesearch.com/yhs/search?' + parse.urlencode(onesearchParams))
    # return soup.prettify()
    ress = soup.find_all("li") #type: ignore
    resultsTask = []
    for r in ress:
        resultsTask.append(asyncio.create_task(buildResults(r))) # type: ignore
    return [i for i in await asyncio.gather(*resultsTask) if i is not None]