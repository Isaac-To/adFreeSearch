from .tools import linkRequester, linkFormatter
from urllib import parse
import asyncio
import uvloop

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
    # return soup.prettify()
    # fP1Qef is the class used to represent each result for google
    ress = soup.find_all("div", class_="fP1Qef") #type: ignore
    resultsDict = []
    for r in ress:
        try:
            trackerLink = r.find("a", href=True)['href'][r.find("a", href=True)['href'].find('http'):]
            trackerLink = parse.unquote(trackerLink)
            link = trackerLink[:trackerLink.find('&')]
            link = linkFormatter(link)
            result = {
                'title': r.find("h3").text,
                'link': link,
                'source': 'google.com',
                'summary': r.find("div", class_="BNeawe s3v9rd AP7Wnd").text,
            }
            resultsDict.append(result)
        except Exception as e:
            pass
    return resultsDict

asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())