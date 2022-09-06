from .tools import linkRequester
from flask import render_template

async def wordDefinition(params):
    """
    It takes the query out of the passed parameters, and returns the definition of that word
    
    :param params: The parameters that are passed to the function
    :return: The definition of the word.
    """
    query = params.get('q')
    link = f'https://www.merriam-webster.com/dictionary/{query}'
    soup = await linkRequester(link)
    try:
        text = (soup.find('span', class_ = 'dtText').get_text()) #type: ignore
        if text.startswith(':'):
            return render_template('definition.html', title=query.title(), text=text[1:], source = link)
    except: pass
    return ''