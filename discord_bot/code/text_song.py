import re
import requests
from bs4 import BeautifulSoup

from selenium.webdriver.common.by import By

from selenium.webdriver import Firefox
from selenium.webdriver.firefox.options import Options

opts = Options()

opts.add_argument("--headless")  # без графического интерфейса.

# for linux:
browser = Firefox(executable_path="../utils/geckodriver", options=opts)

# # for windows:
# browser = Firefox(executable_path="../discord_bot/geckodriver", options=opts)
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
            if len(text) <= 2000:
                return text
            else:
                return "Текст чет большой слишком"
        except Exception as e:
            print(e)
    return "**Не найдено на https://genius.com/**"
