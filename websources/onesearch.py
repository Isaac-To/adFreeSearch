from distutils.command.build import build
from .tools import linkRequester, linkFormatter
from urllib import parse
import asyncio

async def buildResults(rawResult):
    """
    It takes a raw result from the search engine, and returns a dictionary with the title, link, source,
    and summary of the result
    
    :param rawResult: The raw result from the search engine
    :return: A dictionary with the title, link, source, and summary of the search result.
    """
    try:
        link = rawResult.find("span", class_="fz-ms").text
        link = await linkFormatter(link)
        result = {
            'title': rawResult.find('h3', class_="title").text,
            'link': link,
            'source': ['onesearch'],
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
    if soup is None:
        return None
    # return soup.prettify()
    ress = soup.find_all("li") #type: ignore
    resultsTask = []
    for r in ress:
        resultsTask.append(asyncio.create_task(buildResults(r))) # type: ignore
    return [i for i in await asyncio.gather(*resultsTask) if i is not None]