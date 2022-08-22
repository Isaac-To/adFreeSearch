from .tools import linkRequester
from urllib import parse
def googleResults(params):
    soup = linkRequester('https://google.com/search?' + parse.urlencode(params))
    # return soup.prettify()
    # fP1Qef is the class used to represent each result for google
    ress = soup.find_all("div", class_="fP1Qef") #type: ignore
    resultsDict = []
    for r in ress:
        try:
            trackerLink = r.find("a", href=True)['href'][r.find("a", href=True)['href'].find('http'):]
            trackerLink = parse.unquote(trackerLink)
            strippedLink = trackerLink[:trackerLink.find('&')]
            result = {
                'title': r.find("h3").text,
                'link': strippedLink,
                'directory': r.find("div", class_="UPmit").text,
                'summary': r.find("div", class_="BNeawe s3v9rd AP7Wnd").text,
            }
            resultsDict.append(result)
        except Exception as e:
            print(e)
            pass
    return resultsDict