from .tools import linkRequester
from flask import render_template

def deviantArtResults(query):
    soup = linkRequester(f'https://www.deviantart.com/search/deviations?q={query}')
    images = soup.find_all('img', src=True)
    links = []
    for i in images:
        if i.get('src').startswith('https://images-wixmp'):
            links.append(i.get('src'))
    HTML = "<div class='content img-container'>"
    for l in links:
        HTML += render_template('imageResults.html', source=l)
    HTML += "</div>"
    return HTML
