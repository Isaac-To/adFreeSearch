from distutils.command.build import build
from flask import Flask, render_template, request, session, redirect
from bs4 import BeautifulSoup
from urllib import parse
import requests
from fake_useragent import UserAgent
import uuid

app = Flask(__name__)
app.secret_key = uuid.uuid1().hex

def urlParse(url):
    return parse.parse_qs(url)

def randomAgent():
    ua = UserAgent()
    header = {'User-Agent': str(ua.random)}
    print(header)
    return header

def linkRequester(url):
    req = requests.get(url, headers = randomAgent())
    return BeautifulSoup(req.text, "html.parser")

def googleResults(params):
    soup = linkRequester('https://google.com/search?' + parse.urlencode(params))
    # return soup.prettify()
    # fP1Qef is the class used to represent each result for google
    ress = soup.find_all("div", class_="fP1Qef")
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

def resultsToHTML(resultsDict):
    outputHTML = "<div class='content'>"
    for r in resultsDict:
        buildHTML = render_template(
            "singleResult.html", title=r['title'], link=r['link'], directory=r["directory"], summary=r["summary"])
        outputHTML += buildHTML
    return outputHTML + "</div>"

@app.route('/')
def index():
    return render_template("index.html")

@app.route('/s')
@app.route('/search')
def search():
    urlparams = urlParse(request.url)
    try:
        session['q'] = urlparams.get('q')[0]
    except:
        # if there is no query
        return redirect('/')
    try:
        session['start'] = urlparams.get('start')[0]
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
            session['start'] = 0
        elif request.form.get('pg-btn') != None:
            # page change button backend
            session['start'] = int(request.form.get('pg-btn')) # type: ignore
        elif request.form.get('proxy-btn') != None:
            # proxy button backend
            req = requests.get(request.form.get('proxy-btn'), headers = randomAgent())  # type: ignore
            soup = BeautifulSoup(req.text, "html.parser")
            # strips external JS. Only allows transparent on page js.
            scripts = soup.find_all('script', src=True)
            for script in scripts: 
                script.decompose()
            links = soup.find_all("a", href=True)
            # applies proxy on links as well
            for link in links:
                # converts to full links
                if (link.get("href")).startswith("/"):
                    link['href'] = "https://" + str((parse.urlparse(request.form.get('proxy-btn'))).hostname) + link["href"],
            return soup.prettify()
    params = {
        'q': session["q"],
        'start': session["start"],
    }
    # change page buttons
    pgButtons = "<div class='footer'><div class='pg-btn-container'>"
    totalNumberOfButtons = 10
    offset = max(0, int((session['start'] if session['start'] != None else 0) / 10) - int(totalNumberOfButtons / 2))
    for i in range(offset, offset + totalNumberOfButtons):
        pgButtons += render_template('pageChangeButtons.html', startResult= i * 10, pageNum=i)
    pgButtons += "</div></div>"
    return render_template('index.html') + resultsToHTML(googleResults(params)) + pgButtons


if __name__ == '__main__':
    app.run(debug=True)
