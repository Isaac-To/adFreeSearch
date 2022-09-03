from .tools import linkRequester
from urllib import parse
import asyncio
import uvloop

async def deviantArtResults(params):
    """
    It takes a dictionary of parameters, and returns a list of dictionaries containing the source and
    link of the images found on the page
    
    :param params: A dictionary of parameters to be passed to the search engine
    :return: A list of dictionaries.
    """
    dvArtParams = params.copy()
    dvArtParams["page"] = params.get('start') / 10
    soup = await linkRequester(
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

asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())