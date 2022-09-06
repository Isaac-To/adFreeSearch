from .tools import linkRequester
from urllib import parse
from flask import render_template

async def wikipediaInSearch(results):
    """
    It takes a list of search results, and returns the first Wikipedia page it finds
    
    :param results: The results from the search
    :return: The first sentence of the wikipedia page.
    """
    for res in results:
        hostname = str(parse.urlparse(res.get('link')).hostname)
        if hostname.endswith('wikipedia.org'):
            return await wikipediaPage(res.get('link'))
    return ''

async def wikipediaPage(link):
    if link == None:
        return ''
    soup = await linkRequester(link)
    if soup == None:
        return ""
    try:
        infobox = soup.find('td', class_="infobox-image")
        img = infobox.find('img', src=True) # type: ignore
        imageUrl = img.get('src')  # type: ignore
    except:
        imageUrl = None
    articleTitle = soup.find('span', class_="mw-page-title-main").text # type: ignore
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
    return render_template('wikipediaResults.html', title = articleTitle, imageUrl = imageUrl, summary = fullSummary, articleUrl = link)