from bs4 import BeautifulSoup
import requests

def isInStock(page):
    try:
        req = requests.get(page)
        req.raise_for_status()
        soup = BeautifulSoup(req.content, "html.parser")
        val = soup.find(id="stockStatus-0").span.text.strip()
        if (val in ['In Stock', 'Out Of Stock']):
            return val
    except:
        pass
    return 'error'