from .tools import linkRequester, linkFormatter
from urllib import parse
import asyncio

async def buildResult(rawResult):
    """
    It takes a raw result from Google and returns a dictionary with the title, link, source, and summary
    of the result.
    
    :param rawResult: The raw result from the google search
    :return: A dictionary with the title, link, source, and summary of the search result.
    """
    try:
        trackerLink = rawResult.find("a", href=True)['href'][rawResult.find("a", href=True)['href'].find('http'):]
        trackerLink = parse.unquote(trackerLink)
        link = trackerLink[:trackerLink.find('&')]
        link = await linkFormatter(link)
        result = {
            'title': rawResult.find("h3").text,
            'link': link,
            'source': ['google.com'],
            'summary': rawResult.find("div", class_="BNeawe s3v9rd AP7Wnd").text,
        }
        return result
    except:
        return None

async def googleResults(params):
    """
    It takes a dictionary of parameters, and returns a list of dictionaries, each dictionary
    representing a search result from Google
    
    :param params: a dictionary of parameters to be passed to the google search
    :return: A list of dictionaries.
    """
    googleParams = params.copy()
    if params.get('start') == 0:
        del googleParams['start']
    soup = await linkRequester('https://google.com/search?' + parse.urlencode(googleParams))
    if soup is None:
        return None
    # return soup.prettify()
    # fP1Qef is the class used to represent each result for google
    ress = soup.find_all("div", class_="fP1Qef") #type: ignore
    resultsTask = []
    for r in ress:
        resultsTask.append(asyncio.create_task(buildResult(r))) # type: ignore
    return [i for i in await asyncio.gather(*resultsTask) if i is not None]