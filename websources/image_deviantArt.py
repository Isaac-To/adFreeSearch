from .tools import linkRequester
from urllib import parse

def deviantArtResults(params):
    dvArtParams = params.copy()
    dvArtParams["page"] = params.get('start') / 10
    soup = linkRequester(
        f'https://www.deviantart.com/search/deviations?{parse.urlencode(dvArtParams)}')
    img_items = soup.find_all('a', href=True)
    results = []
    for item in img_items:
        imgs = item.find_all(src=True)
        for img in imgs:
            if img.get('src').startswith('https://images-wixmp'):
                results.append({"source": img.get('src'),
                            "link": item.get('href')})
    return results
