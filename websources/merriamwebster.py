from .tools import linkRequester
from flask import render_template
def wordDefinition(query):
    if len(query.split(' ')) != 1:
        return ''
    link = f'https://www.merriam-webster.com/dictionary/{query}'
    soup = linkRequester(link)
    try:
        text = (soup.find('span', class_ = 'dtText').get_text()) #type: ignore
        if text.startswith(':'):
            return render_template('definition.html', title=query.title(), text=text[1:], source = link)
    except: pass
    return ''