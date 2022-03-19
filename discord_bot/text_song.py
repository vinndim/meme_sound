import re

import requests
from bs4 import BeautifulSoup

from selenium.webdriver.common.by import By

from selenium.webdriver import Firefox
from selenium.webdriver.firefox.options import Options

opts = Options()
opts.set_preference('general.useragent.override', 'whip')

opts.add_argument("--headless")  # без графического интерфейса.
browser = Firefox(options=opts)
site_with_text = "genius"


async def get_lyric(song):
    search_song = re.sub(r"[$#%!@*&—]", "", song)
    search_song = re.sub(r'\s+', ' ', search_song)
    try:
        search_song = search_song.split("(")[0] + search_song.split(")")[1]
    except IndexError:
        pass
    print(search_song)
    browser.get('https://yandex.ru/search/?text=' + search_song + site_with_text)
    elems = browser.find_elements(by=By.XPATH, value="//a[@href]")
    url = ''
    text = ''
    for elem in elems:
        some_url = elem.get_attribute("href")
        if some_url.startswith("https://genius.com/"):
            url = some_url
            break
    if url:
        try:
            soup = BeautifulSoup(requests.get(url).content, 'lxml')
            for tag in soup.select('div[class^="Lyrics__Container"], .song_body-lyrics p'):
                text += tag.get_text(strip=True, separator='\n')

            return url + "/n" + text
        except Exception as e:
            print(e)
    return "**Не найдено на https://genius.com/**"
