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
from websources.oneSearch import onesearchResults
from websources.brave import braveResults
from websources.merriamWebster import wordDefinition
from websources.wikipedia import wikipediaInSearch
# images
from websources.imageDeviantArt import deviantArtResults
# tools
import websources.tools
from generator import generateWidgetBar, generateFooter
from spellcheck import sentenceBreakDown

# app setup
app = Flask(__name__)
app.secret_key = uuid.uuid1().hex

# no limit on caches for templates
app.jinja_env.cache = {}


@app.route('/')
async def index():
    """
    It returns a string that contains the hostname of the
    URL that the user is currently on, and then it
    renders the index.html template
    :return: The return value of the function is a string.
    """
    webTitle = f'''<h1 class="brandName">
    {parse.urlparse(request.url).hostname}
    </h1>
    '''
    return webTitle + render_template("index.html", mode='search')


@app.route('/s')
@app.route('/search')
async def search():
    """
    It takes the query from the url and sets it to the session
    variable 'q' and then calls the query_post function
    :return: The return value of the function is the return value
    of the last line of the function.
    """
    # all queries made through the addr bar should be considered a search
    session['mode'] = 'search'
    urlparams = parse.parse_qs(parse.urlparse(request.url).query)
    try:
        session['q'] = urlparams.get('q')[0]  # type: ignore
    except IndexError:
        # if there is no query
        return redirect('/')
    try:
        session['start'] = urlparams.get('start')[0]  # type: ignore
    except IndexError:
        # by default, it should start at 0 unless denoted in the url
        session['start'] = 0
    return await accessQuery()


async def searchData(params):
    # fetching
    resultsTasks = [
        asyncio.create_task(googleResults(params)),
        asyncio.create_task(bingResults(params)),
        asyncio.create_task(onesearchResults(params)),
        asyncio.create_task(braveResults(params)),
    ]
    # collect results
    results = await asyncio.gather(*resultsTasks)
    combinedSearchResults = await websources.tools.interlace(results)
    # sort results
    return await websources.tools.relevancyByOccurances(
        combinedSearchResults)


@app.route('/', methods=['POST'])
@app.route('/s', methods=['POST'])
@app.route('/search', methods=['POST'])
async def accessQuery():
    """
    It takes a query from the search bar, and returns a page with the results.
    :return: The html of the page.
    """
    acceptedTime = time()
    session.permanent = True
    # if there is a page update request
    if request.form.get('query') is not None:
        session['mode'] = request.form.get("mode")
        session['start'] = 0
        session['q'] = request.form.get('query')
    elif request.form.get('correctQueryButton') is not None:
        session['mode'] = request.form.get("mode")
        session['start'] = 0
        session['q'] = request.form.get('correctQueryButton')
    elif request.form.get('pgBtn') is not None:
        # page change button backend
        session['start'] = int(request.form.get('pgBtn'))  # type: ignore
    params = dict()
    # incase errors
    try:
        # incase there is no query
        if session["q"] == "":
            return redirect("/")
        # assigns the session query to the param to be subitted
        params['q'] = session['q']
    except KeyError:
        return (redirect('/'))
    try:
        params['start'] = session["start"]
    except KeyError:
        params["start"] = 0
    try:
        if session['mode'] is None:
            session['mode'] = 'search'
    except KeyError:
        session['mode'] = 'search'
    # start spellchecking the query
    querySpellingTask = asyncio.create_task(sentenceBreakDown(params['q']))
    # start generating footer buttons
    footer = asyncio.create_task(generateFooter(params['start']))
    html = ''
    html += render_template('index.html', mode=session['mode'])
    html += '<div class="displaySpace">'
    html += '<div class="content">'
    if session.get('mode') == "search":
        # load independent widget sources
        widgetTasks = []
        widgetTasks.append(asyncio.create_task(wordDefinition(params)))
        searchTask = asyncio.create_task(searchData(params))
        # layering
        html += f'''<br>
        <h3 class="queryInfo">
        Results for <i>{params["q"]}</i>
        </h3>
        '''
        corrected_query = await querySpellingTask
        if params['q'] != corrected_query:
            html += render_template('didYouMean.html',
                                    corrected_query=corrected_query)
        # gather search results
        combinedSearchResults = await searchTask
        # start generating wikipedia widgets based on the results
        if combinedSearchResults is not None:
            widgetTasks.append(asyncio.create_task(
                wikipediaInSearch(combinedSearchResults)))
        # start generating the HTML based on the results
        resultsHTML = asyncio.create_task(
            websources.tools.resultsToHTML(combinedSearchResults))
        html += await generateWidgetBar(await asyncio.gather(*widgetTasks))
        html += await resultsHTML
    if session.get("mode") == "images":
        deviantResults = await deviantArtResults(params)
        html += await websources.tools.imgResultsToHTML(deviantResults)
    html += await footer
    html += "</div></div>"
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
        print('This is running without UVLoop, expect slower performance')
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
        app.run()
