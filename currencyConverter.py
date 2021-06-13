import bs4
from bs4 import BeautifulSoup
import requests
import re

base_url = 'https://www.google.com/search?q='


def Convert(from_curr, to_curr,value):
    conversion_code =str(value) + "+" + from_curr + "+to+" + to_curr
    final_url = base_url + conversion_code
    element = requests.get(final_url)
    soup = BeautifulSoup(element.content, 'html.parser')
    content = soup.getText()

    # Search for conversion value inside of text
    pattern = "= (.*?) "
    converted_val = re.search(pattern, content).group(1)
    results = str(round(float(converted_val), 2))
    return results

Convert('usd','cad',10)