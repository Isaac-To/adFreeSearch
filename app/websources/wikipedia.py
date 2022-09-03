from .tools import linkRequester
from urllib import parse
from flask import render_template
import asyncio
import uvloop

async def wikipediaInSearch(results):
    """
    It takes a list of search results, and returns the first Wikipedia page it finds
    
    :param results: The results from the search
    :return: The first sentence of the wikipedia page.
    """
    for res in results:
        hostname = str(parse.urlparse(res.get('link')).hostname)
        if hostname.endswith('wikipedia.org'):
            return await wikipediaPage(res['link'].split('/')[-2])
    return ''

asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())

async def wikipediaPage(query):
    """
    It takes a query, and returns a rendered template with the query's title, image, summary, and
    article url.
    
    :param query: the query to search for
    :return: The wikipedia page for the query.
    """
    if query == None:
        return ''
    articleUrl = f'https://wikipedia.org/wiki/{query}'
    soup = await linkRequester(articleUrl)
    if soup == None:
        return ""
    try:
        infobox = soup.find('td', class_="infobox-image")
        img = infobox.find('img', src=True) # type: ignore
        imageUrl = img.get('src')  # type: ignore
    except:
        imageUrl = None

    links = soup.findAll("a", href=True)
    for link in links:
        if link.get('href').startswith('#cite'):
            link.decompose()
    summarySnippet = soup.find_all("p") # type: ignore
    fullSummary = ""
    for summary in summarySnippet:
        # gets the first 500 or so characters
        if len(fullSummary) < 500:
            fullSummary += summary.text
        else:
            break
    if "may refer to:" in fullSummary and len(fullSummary) < 200:
        return ''
    return render_template('wikipediaResults.html', title = parse.unquote(query).replace('_',' ').title(), imageUrl = imageUrl, summary = fullSummary, articleUrl = articleUrl)
    
asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())