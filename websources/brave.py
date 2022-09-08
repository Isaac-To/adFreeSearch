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
        link = rawResult.find("a", class_ ="result-header", href=True).get("href")
        link = await linkFormatter(link)
        result = {
            'title': rawResult.find('span', class_ = "snippet-title").text,
            'link': link,
            'source': ['brave.com'],
            'summary': rawResult.find("p", class_ = "snippet-description").text,
        }
        return result
    except Exception as e:
        print(e)
        return None

async def braveResults(params):
    """
    It takes a dictionary of parameters, and returns a list of dictionaries, each of which represents a
    search result from Brave
    
    :param params: a dictionary of parameters to be passed to the search engine
    :return: A list of dictionaries.
    """
    braveParams = params.copy()
    if params.get('start') != 0:
        braveParams['offset'] = int(params.get("start") / 10)
    del braveParams['start']
    soup = await linkRequester('https://search.brave.com/search?' + parse.urlencode(braveParams))
    if soup is None:
        return None
    # return soup.prettify()
    ress = soup.find_all("div", class_="snippet fdb") #type: ignore
    resultsTask = []
    for r in ress:
        resultsTask.append(asyncio.create_task(buildResults(r))) # type: ignore
    return [i for i in await asyncio.gather(*resultsTask) if i is not None]