from distutils.command.build import build
from flask import Flask, render_template, request, session, redirect
from bs4 import BeautifulSoup
from urllib import parse
import requests
from fake_useragent import UserAgent
import uuid

# self wrote
import adLists

app = Flask(__name__)
app.secret_key = uuid.uuid1().hex

def randomAgent():
    ua = UserAgent()
    header = {'User-Agent': str(ua.random)}
    return header

def linkRequester(url):
    req = requests.get(url, headers = randomAgent())
    if req.status_code not in range(200, 299):
        # try again one more time
        req = requests.get(url, headers = randomAgent())
    # print(req.status_code, url)
    return BeautifulSoup(req.text, "html.parser")

def googleResults(params):
    soup = linkRequester('https://google.com/search?' + parse.urlencode(params))
    # return soup.prettify()
    # fP1Qef is the class used to represent each result for google
    ress = soup.find_all("div", class_="fP1Qef") #type: ignore
    resultsDict = []
    for r in ress:
        try:
            trackerLink = r.find("a", href=True)['href'][r.find("a", href=True)['href'].find('http'):]
            trackerLink = parse.unquote(trackerLink)
            strippedLink = trackerLink[:trackerLink.find('&')]
            result = {
                'title': r.find("h3").text,
                'link': strippedLink,
                'directory': r.find("div", class_="UPmit").text,
                'summary': r.find("div", class_="BNeawe s3v9rd AP7Wnd").text,
            }
            resultsDict.append(result)
        except Exception as e:
            print(e)
            pass
    return resultsDict

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
            soup = BeautifulSoup(req.text, "html.parser")
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
