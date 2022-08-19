from distutils.command.build import build
from flask import Flask, render_template, request, redirect
from bs4 import BeautifulSoup
from urllib import parse
import requests

app = Flask(__name__)


@app.route('/')
def index():
    return render_template("index.html")


def urlParse(url):
    return parse.parse_qs(parse.urlparse(url).query)


def googleResults(params):
    if params.get('start') == "0":
        googlifiedParams = {'q': params['q'][0], 'start': params["start"][0]}
    else:
        googlifiedParams = {'q': params['q'][0]}
    link = 'https://google.com/search?' + parse.urlencode(googlifiedParams)
    print(f'forwarded to {link}')
    req = requests.get(link).text
    soup = BeautifulSoup(req, "html.parser")
    ress = soup.find_all("div", class_="fP1Qef")
    resultsDict = []
    for r in ress:
        try:
            resultsDict.append({
                'title': r.find("h3").text,
                'link': r.find("a", href=True)['href'][len('/url?q='):].split("&")[0],
                'directory': r.find("div", class_="UPmit").text,
                'summary': r.find("div", class_="BNeawe s3v9rd AP7Wnd").text,
            })
        except:
            pass
    return resultsDict


def resultsHTML(url):
    params = urlParse(url)
    resultsDict = googleResults(params)
    outputHTML = ""
    for r in resultsDict:
        buildHTML = render_template(
            "singleResult.html", title=r['title'], link=r['link'], directory=r["directory"], summary=r["summary"])
        outputHTML += buildHTML
    return outputHTML


def pageChangeButtons(url):
    oldParams = urlParse(url)
    params = {
        'q': oldParams["q"][0],
    }
    outputHTML = '<div class="footer">'
    if (oldParams.get('start')):
        oldStart = int(oldParams["start"][0])
    else:
        oldStart = 0
    # allow the user to change to a surround page + a few seeker pages
    offset = max(oldStart - 50, 0)
    for i in range(0, 10):
        params['start'] = offset  # type: ignore
        outputHTML += render_template("pageChangeButtons.html", path='search?' +
                                      parse.urlencode(params), pageNumber=int(offset / 10))
        offset += 10
    return outputHTML + "</div>"


@app.route('/search')
def query():
    return render_template('index.html') + resultsHTML(request.url) + pageChangeButtons(request.url)  # type: ignore


@app.route('/', methods=['POST'])
@app.route('/search', methods=['POST'])
def query_post():
    query = request.form.get('query')  # type: ignore
    return redirect(f'/search?q={query}')


if __name__ == '__main__':
    app.run(debug=True)
