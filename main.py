from flask import Flask, render_template, request, session, redirect
from urllib import parse
import uuid
import asyncio
from sys import platform
from time import time

# self wrote
# import adLists
# search
from websources.google import googleResults
from websources.bing import bingResults
from websources.onesearch import onesearchResults
from websources.merriamwebster import wordDefinition
from websources.wikipedia import wikipediaInSearch
# images
from websources.image_deviantArt import deviantArtResults
# tools
from websources.tools import resultsToHTML, imgResultsToHTML, relevancyByOccurances, interlace
from generator import generateWidgetBar, generateFooter

# app setup
app = Flask(__name__)
app.secret_key = uuid.uuid1().hex

# no limit on caches for templates
app.jinja_env.cache = {}


@app.route('/')
async def index():
    """
    It returns a string that contains the hostname of the URL that the user is currently on, and then it
    renders the index.html template
    :return: The return value of the function is a string.
    """
    return f'<h1 class="brand-name">{parse.urlparse(request.url).hostname}</h1>' + render_template("index.html", mode='search')


@app.route('/s')
@app.route('/search')
async def search():
    """
    It takes the query from the url and sets it to the session variable 'q' and then calls the
    query_post function
    :return: The return value of the function is the return value of the last line of the function.
    """
    # all queries made through the addr bar should be considered a search
    session['mode'] = 'search'
    urlparams = parse.parse_qs(parse.urlparse(request.url).query)
    try:
        session['q'] = urlparams.get('q')[0]  # type: ignore
    except Exception as e:
        # if there is no query
        return redirect('/')
    try:
        session['start'] = urlparams.get('start')[0]  # type: ignore
    except:
        # by default, it should start at 0 unless denoted in the url
        session['start'] = 0
    return await query_post()


@app.route('/', methods=['POST'])
@app.route('/s', methods=['POST'])
@app.route('/search', methods=['POST'])
async def query_post():
    """
    It takes a query from the search bar, and returns a page with the results.
    :return: The html of the page.
    """
    acceptedTime = time()
    session.permanent = True
    # if there is a new query from the search bar or an update from the page buttons
    if request.form.get('query') != None:
        session['mode'] = request.form.get("mode")
        session['start'] = 0
        session['q'] = request.form.get('query')
    elif request.form.get('pg-btn') != None:
        # page change button backend
        session['start'] = int(request.form.get('pg-btn'))  # type: ignore
    params = dict()
    # incase errors
    try:
        # incase there is no query
        if session["q"] == "":
            return redirect("/")
        # assigns the session query to the param to be subitted
        params['q'] = session['q']
    except:
        return (redirect('/'))
    try:
        params['start'] = session["start"]
    except:
        params["start"] = 0
    # start generating footer buttons
    footer = asyncio.create_task(generateFooter(params['start']))
    html = ''
    html += render_template('index.html', mode=session['mode'])
    html += '<div class="content">'
    if session.get('mode') == "search":
        # fetching
        resultsTasks = [
            asyncio.create_task(googleResults(params)),
            asyncio.create_task(bingResults(params)),
            asyncio.create_task(onesearchResults(params))
        ]
        # load independent widget sources
        widgetTasks = []
        widgetCriteria = len(str(params.get('q')).split(' ')) < 3
        # check if criteria to run widget is met
        if widgetCriteria:
            widgetTasks.append(asyncio.create_task(wordDefinition(params)))
        # collect results
        results = await asyncio.gather(*resultsTasks)
        interlacedResults = await interlace(results)
        combinedSearchResults = asyncio.create_task(
            relevancyByOccurances(interlacedResults))  # type: ignore
        # load dependent widget sources
        # check if criteria to run widget is met
        if widgetCriteria:
            widgetTasks.append(asyncio.create_task(
                wikipediaInSearch(interlacedResults)))
        # sort results
        combinedSearchResults = await combinedSearchResults
        # start assembling HTML for results
        resultsHTML = asyncio.create_task(resultsToHTML(combinedSearchResults))
        # layering
        html += await generateWidgetBar(await asyncio.gather(*widgetTasks))
        html += f'<br><h3 class="queryInfo">Showing results for <i>{params["q"]}</i></h3>'
        html += await resultsHTML
    if session.get("mode") == "images":
        deviantResults = await deviantArtResults(params)
        html += await imgResultsToHTML(deviantResults)
    html += await footer
    html += "</div>"
    print(f"Resolved in {round(time() - acceptedTime, 5)}s")
    return html

if __name__ == '__main__':
    if platform == "linux":
        import uvloop
        # asyncio
        asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
        # app.run(debug=True)
        app.run()
    else:
        print('This program must be run on Linux or in a Linux container')
