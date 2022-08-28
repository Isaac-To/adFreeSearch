from .tools import linkRequester
from urllib import parse
def bingResults(params):
    bingParams = params.copy()
    if params.get('start') != 0:
        bingParams['first'] = params.get("start") + 1
    del bingParams['start']
    soup = linkRequester('https://bing.com/search?' + parse.urlencode(bingParams))
    # return soup.prettify()
    # fP1Qef is the class used to represent each result for google
    ress = soup.find_all("li", class_="b_algo") #type: ignore
    resultsDict = []
    for r in ress:
        link = r.find("div", class_ ="b_attribution").text
        if not link.startswith('http'):
            link = 'https://' + link
        if not link.endswith('/'):
            link += '/'
        try:
            result = {
                'title': r.find('h2').text,
                'link': link,
                'source': 'bing.com',
                'summary': r.find("p").text,
            }
            resultsDict.append(result)
        except Exception as e:
            print(e)
            pass
    return resultsDict