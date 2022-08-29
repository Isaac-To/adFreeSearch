from .tools import linkRequester
from urllib import parse
async def googleResults(params):
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
            if not link.startswith('http'):
                link = 'https://' + link
            if not link.endswith('/'):
                link += '/'
            result = {
                'title': r.find("h3").text,
                'link': link,
                'source': 'google.com',
                'summary': r.find("div", class_="BNeawe s3v9rd AP7Wnd").text,
            }
            resultsDict.append(result)
        except Exception as e:
            print(e)
            pass
    return resultsDict