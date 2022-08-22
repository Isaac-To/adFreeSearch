import requests
from urllib import parse
from fake_useragent import UserAgent

def randomAgent():
    ua = UserAgent()
    header = {'User-Agent': str(ua.random)}
    return header

def generateFilterList():
    # grabs the lists and adds them to the combined list
    headers = randomAgent()
    combinedList = ''
    combinedList += requests.get('https://easylist.to/easylist/easylist.txt', headers = headers).text
    combinedList += requests.get('https://easylist.to/easylist/easyprivacy.txt', headers = headers).text
    combinedList += requests.get('https://secure.fanboy.co.nz/fanboy-cookiemonster.txt', headers = headers).text
    combinedList += requests.get('https://secure.fanboy.co.nz/fanboy-annoyance.txt', headers = headers).text
    localCache = open('filterLists.txt', 'w', encoding="utf-8")
    localCache.write(combinedList)
    localCache.close()

def compareURL(url):
    try:
        localCache = open("filterLists.txt", "r", encoding="utf-8")
    except FileNotFoundError:
        generateFilterList()
        localCache = open("filterLists.txt", "r", encoding="utf-8")
    # start formatting them
    individualEntry = localCache.readlines()
    localCache.close()
    entryIndex = 0
    # removes all comments (hopefully)
    while entryIndex < len(individualEntry):
        if not len(individualEntry[entryIndex]) == 0 and individualEntry[entryIndex][0] in ['[', '!']:
            individualEntry.pop(entryIndex)
        else:
            entryIndex += 1
    # parse the input url
    urlParts = parse.urlparse(url)
    # compare
    for rule in individualEntry:
        # path comparison
        if rule[0] == '/':
            ruleParts = rule.split("/")
            pathParts = urlParts.path.split('/')
            for partIndex in range(0, min(len(ruleParts), len(pathParts))):
                # checks if paths match or wildcard
                if pathParts[partIndex] not in [ruleParts[partIndex], '*']:
                    if '^' in ruleParts[partIndex]:
                        if pathParts[partIndex].startswith(ruleParts[partIndex][:ruleParts[partIndex].find('^')]):
                            return True
                    else:
                        return True
            else:
                return False # is not an ad
        if rule.startswith('||'):
            if urlParts.hostname == rule[:1]:
                return True
        if rule.startswith('|') and rule.endswith("|"):
            if url == rule[1:-1]:
                return True
        # add exceptions and more detailed blocking in the future
    else:
        return False