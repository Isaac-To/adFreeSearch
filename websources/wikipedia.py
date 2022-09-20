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
        if hostname and hostname.endswith('.wikipedia.org'):
            return await wikipediaPage(res.get('link'))
    return ''

async def wikipediaPage(link):
    """
    It takes a wikipedia link, and returns a template with the title, image, summary, and link.
    
    :param link: the link to the wikipedia page
    :return: The wikipedia page
    """
    if link == None:
        return ''
    soup = await linkRequester(link)
    if soup == None:
        return ""
    imgs = soup.find_all('img', src=True)
    for img in imgs:
        if img.get('src').startswith('//upload.wikimedia.org/wikipedia/commons/thumb/'):
            imageUrl = img.get("src")
            break
    else:
        imageUrl = None
    articleTitle = soup.find("h1").text # type: ignore
    citations = soup.findAll("a", href=True)
    for cite in citations:
        if cite.get('href').startswith('#cite'):
            cite.decompose()
    summarySnippet = soup.find_all("p") # type: ignore
    fullSummary = ""
    for summary in summarySnippet:
        # gets the first 250 or so characters
        if len(fullSummary) < 250:
            fullSummary += summary.text
        else:
            break
    if "may refer to:" in fullSummary and len(fullSummary) < 100:
        return ''
    hostname = parse.urlparse(link).hostname
    return render_template('widgetCard.html', title = articleTitle, imageUrl = imageUrl, summary = fullSummary, articleUrl = link, source = hostname)