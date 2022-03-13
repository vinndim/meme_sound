import requests
from bs4 import BeautifulSoup

from selenium.webdriver.common.by import By

from selenium.webdriver import Firefox
from selenium.webdriver.firefox.options import Options

opts = Options()

opts.add_argument("--headless")  # без графического интерфейса.

browser = Firefox(options=opts)


def get_lyric(Song):
    browser.get('https://genius.com/search?q=' + Song)
    url = browser.find_element(by=By.CLASS_NAME, value='mini_card').get_attribute('href')
    browser.quit()

    soup = BeautifulSoup(requests.get(url).content, 'lxml')
    text = ''
    for tag in soup.select('div[class^="Lyrics__Container"], .song_body-lyrics p'):
        text += tag.get_text(strip=True, separator='\n')
    print(text)
    return text


print(get_lyric('SHADOWRAZE — SHOWDOWN'))
