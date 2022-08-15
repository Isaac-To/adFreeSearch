from distutils.command.build import build
from flask import Flask, render_template, request, redirect
from bs4 import BeautifulSoup
import requests

app = Flask(__name__)

@app.route('/')
def index():
    return render_template("index.html")

def results(query):
    req = requests.get('https://google.com/search?q=' + query).text
    soup = BeautifulSoup(req, "html.parser")
    ress = soup.find_all("div", class_="fP1Qef")
    resultsDict = []
    for r in ress:
        resultsDict.append({
            'title': r.find("div", class_="BNeawe").text,
            'link': r.find("a", href=True)['href'][len('/url?q='):].split("&")[0],
            'directory': r.find("div", class_="UPmit").text,
            'summary': r.find("div", class_="BNeawe s3v9rd AP7Wnd"),
        })
    return resultsDict

def resultsHTML(query):
    resultsDict = results(query)
    outputHTML = ""
    for r in resultsDict:
        buildHTML = ""
        buildHTML += f"<a href='{r['link']}'>{r['title']}</a><br>"
        buildHTML += f"<small>{r['directory']}</small>"
        buildHTML += f"<small>{r['summary']}</small>"
        outputHTML += buildHTML
    return outputHTML

def formattedQuery(path):
    return path[path.rfind("=") + 1:].replace("%20", "+")

@app.route('/search')
def query():
    return render_template('index.html') + resultsHTML(formattedQuery(request.full_path))  # type: ignore

@app.route('/', methods=['POST'])
@app.route('/search', methods=['POST'])
def query_post():
    query = request.form.get('query')  # type: ignore
    return redirect(f'/search?q={query}')

@app.route("/content")
def content():
    resultstoHTML(results(formattedQuery(request.full_path)))  # type: ignore

if __name__ == '__main__':
    app.run(debug=True)