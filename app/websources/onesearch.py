from .tools import linkRequester, linkFormatter
from urllib import parse
import asyncio
import uvloop

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
    resultsDict = []
    for r in ress:
        try:
            link = r.find("span", class_="fz-ms").text
        except:
            continue
        link = linkFormatter(link)
        try:
            result = {
                'title': r.find('h3', class_="title").text,
                'link': link,
                'source': 'onesearch.com',
                'summary': r.find("p", class_="fz-ms").text,
            }
            resultsDict.append(result)
        except Exception as e:
            pass
    return resultsDict

asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())