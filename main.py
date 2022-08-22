from distutils.command.build import build
from flask import Flask, render_template, request, session, redirect
from bs4 import BeautifulSoup
from urllib import parse
import requests
import uuid

# self wrote
# import adLists
from websources.google import googleResults
from websources.merriamwebster import wordDefinition
from websources.wikipedia import wikipediaInSearch

app = Flask(__name__)
app.secret_key = uuid.uuid1().hex

def resultsToHTML(resultsDict):
    outputHTML = "<div class='content'>"
    for r in resultsDict:
        buildHTML = render_template(
            "singleResult.html", title=r['title'], link=r['link'], directory=r["directory"], summary=r["summary"])
        outputHTML += buildHTML
    return outputHTML + "</div>"

@app.route('/')
def index():
    return f'<h1 class="brand-name">{parse.urlparse(request.url).hostname}</h1>' + render_template("index.html")

@app.route('/s')
@app.route('/search')
def search():
    urlparams = parse.parse_qs(parse.urlparse(request.url).query)
    try:
        session['q'] = urlparams.get('q')[0] #type: ignore
    except Exception as e:
        # if there is no query
        return redirect('/')
    try:
        session['start'] = urlparams.get('start')[0] # type: ignore
    except:
        # by default, it should start at 0 unless denoted in the url
        session['start'] = 0
    return query_post()

@app.route('/', methods=['POST'])
@app.route('/s', methods=['POST'])
@app.route('/search', methods=['POST'])
def query_post():
    session.permanent = True
    # if there is a new query from the search bar or an update from the page buttons
    if request.method == "POST":
        if request.form.get('query') != None:
            session['q'] = request.form.get('query')  # type: ignore
            if session["q"] == "":
                return redirect("/")
            session['start'] = 0
        elif request.form.get('pg-btn') != None:
            # page change button backend
            session['start'] = int(request.form.get('pg-btn')) # type: ignore
        elif request.form.get('proxy-btn') != None:
            # proxy button backend
            req = requests.get(request.form.get('proxy-btn'), headers = randomAgent())  # type: ignore
            # soup = BeautifulSoup(req.text, "html.parser")
            # removes all references to external elements if flagged to be an ad/tracker BEING WORKED ON
            # externalElements = soup.find_all(href=True)
            # externalElements.extend(soup.find_all(src=True))
            # for elem in externalElements:
            #     try:
            #         if adLists.compareURL(elem.get('href')):
            #             elem.decompose()
            #     except: pass
            #     try:
            #         if adLists.compareURL(elem.get('src')):
            #             elem.decompose()
            #     except: pass
            return req.text
    params = dict()
    # incase errors
    try: params['q'] = session['q']
    except: return(redirect('/'))
    try: params['start'] = session["start"]
    except: params["start"] = 0
    # change page buttons
    pgButtons = "<div class='footer'><div class='pg-btn-container'>"
    totalNumberOfButtons = 10
    offset = max(0, int((session['start'] if session['start'] != None else 0) / 10) - int(totalNumberOfButtons / 2))
    for i in range(offset, offset + totalNumberOfButtons):
        pgButtons += render_template('pageChangeButtons.html', startResult= i * 10, pageNum=i)
    pgButtons += "</div></div>"
    # wikipedia fetching
    searchResults = googleResults(params)
    # layering
    html = ''
    html += render_template('index.html')
    html += '<div class="widgetContainer">'
    html += wordDefinition(params['q'])
    html += wikipediaInSearch(searchResults)
    html += '</div>'
    html += f'<br><h3 class="content">Showing results for {params["q"]}</h3>'
    html += resultsToHTML(searchResults)
    html += pgButtons
    return html

if __name__ == '__main__':
    app.run(debug=True)
