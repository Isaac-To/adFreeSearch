from distutils.command.build import build
from flask import Flask, render_template, request, session
from bs4 import BeautifulSoup
from urllib import parse
import requests
from fake_useragent import UserAgent

app = Flask(__name__)


def urlParse(url):
    return parse.parse_qs(parse.urlparse(url).query)


def googleResults(params):
    link = 'https://google.com/search?' + parse.urlencode(params)
    print(f'forwarded to {link}')
    # a random UA
    ua = UserAgent()
    req = requests.get(link, ua.random)
    # notify if blocked by Re-Captcha
    if req.status_code == 200:
        soup = BeautifulSoup(req.text, "html.parser")
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
        outputHTML = ""
        for r in resultsDict:
            buildHTML = render_template(
                "singleResult.html", title=r['title'], link=r['link'], directory=r["directory"], summary=r["summary"])
            outputHTML += buildHTML
        return outputHTML
    else:
        return "Err: 200 Ran into Re-Captcha, try hosting from another IP-addr or waiting a while"

@app.route('/')
@app.route('/', methods=['POST'])
@app.route('/search')
@app.route('/search', methods=['POST'])
def query_post():
    # handles new queries from the URL
    session.permanent = True
    if session.new:
        urlparams = urlParse(request.url)
        session['q'] = urlparams.get('q')
        session['start'] = urlparams.get('start')
    # if there is a new query from the search bar or an update from the page buttons
    if request.method == "POST":
        if request.form.get('query') != None:
            session.new = True
            session['q'] = request.form.get('query')  # type: ignore
            session['start'] = 0
        elif request.form.get('pg-btn') != None:
            # page change button backend
            session['start'] = int(request.form.get('pg-btn')) # type: ignore
        elif request.form.get('proxy-btn') != None:
            # proxy button backend
            ua = UserAgent()
            req = requests.get(request.form.get('proxy-btn'), ua.random)  # type: ignore
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
                    link['href'] = "https://" + str((parse.urlparse(request.form.get('proxy-btn'))).netloc) + link["href"],
            return render_template('index.html') + soup.prettify()
    params = {
        'q': session["q"],
        'start': session["start"],
    }
    # change page buttons
    pgButtons = "<div class='footer'>"
    totalNumberOfButtons = 10
    offset = max(0, int(session['start'] / 10) - int(totalNumberOfButtons / 2))
    for i in range(offset, offset + totalNumberOfButtons):
        pgButtons += render_template('pageChangeButtons.html', startResult= i * 10, pageNum=i)
    pgButtons += "</div>"
    return render_template('index.html') + googleResults(params) + pgButtons


if __name__ == '__main__':
    app.secret_key = "TEMP VALUE CHANGE LATER"
    app.run(debug=True)
