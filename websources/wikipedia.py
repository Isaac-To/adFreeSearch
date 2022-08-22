from .tools import linkRequester
from urllib import parse
from flask import render_template

def wikipediaInSearch(results):
    for res in results:
        if 'wikipedia.org' in res['link']:
            return wikipediaPage(res['link'][res['link'].rfind('/') + 1:])
    return ''

def wikipediaPage(query):
    if query == None:
        return ''
    articleUrl = f'https://wikipedia.org/wiki/{query}'
    soup = linkRequester(articleUrl)
    if soup == None:
        return ""
    imgs = soup.find_all("img", src=True)  # type: ignore
    imageUrl = None
    for img in imgs:
        if query in img.get('src'):
            imageUrl = img.get('src')
            break
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