from .tools import linkRequester, linkFormatter
from urllib import parse
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
    # return soup.prettify()
    ress = soup.find_all("li", class_="b_algo") #type: ignore
    resultsDict = []
    for r in ress:
        link = r.find("div", class_ ="b_attribution").text
        link = linkFormatter(link)
        try:
            result = {
                'title': r.find('h2').text,
                'link': link,
                'source': 'bing.com',
                'summary': r.find("p").text,
            }
            resultsDict.append(result)
        except Exception as e:
            pass
    return resultsDict