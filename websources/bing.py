from .tools import linkRequester, linkFormatter
from urllib import parse
import asyncio

async def buildResults(rawResult):
    """
    It takes the raw result from the search engine, and formats it into a dictionary
    
    :param rawResult: The raw result from the HTML page
    :return: A dictionary with the title, link, source, and summary of the search result.
    """
    try:
        link = rawResult.find("div", class_ ="b_attribution").text
        link = await linkFormatter(link)
        result = {
            'title': rawResult.find('h2').text,
            'link': link,
            'source': ['bing.com'],
            'summary': rawResult.find("p").text,
        }
        return result
    except:
        return None

async def bingResults(params):
    """
    It takes a dictionary of parameters, and returns a list of dictionaries, each of which represents a
    search result from Bing
    
    :param params: a dictionary of parameters to be passed to the search engine
    :return: A list of dictionaries.
    """
    bingParams = params.copy()
    if params.get('start') != 0:
        bingParams['first'] = params.get("start") + 1
    del bingParams['start']
    soup = await linkRequester('https://bing.com/search?' + parse.urlencode(bingParams))
    if soup is None:
        return None
    # return soup.prettify()
    ress = soup.find_all("li", class_="b_algo") #type: ignore
    resultsTask = []
    for r in ress:
        resultsTask.append(asyncio.create_task(buildResults(r))) # type: ignore
    return [i for i in await asyncio.gather(*resultsTask) if i is not None]