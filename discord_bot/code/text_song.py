import re

import requests
from bs4 import BeautifulSoup

site_with_lyric = "genius"


async def get_normal_title(song_title):
    search_song = re.sub(r"[$#%!@*&—]", "", song_title)
    search_song = re.sub(r'\s+', ' ', search_song)
    try:
        search_song = search_song.split("(")[0] + search_song.split(")")[1]
    except IndexError:
        pass
    return search_song


async def get_lyric(song):
    search_song = await get_normal_title(song)
    r = requests.get('https://www.google.com/search?q=',
                     params={'q': f'{search_song} {site_with_lyric}'})
    soup = BeautifulSoup(r.content, 'html.parser')
    url = ""
    text = ''
    msg_text = []
    for link in soup.find_all('a'):
        if "https://genius.com/" in link.get('href'):
            url = link.get('href').split("&")[0][7:]
            break
    if url:
        try:
            r = requests.get(url)
            soup = BeautifulSoup(r.content, 'lxml')
            for tag in soup.select('div[class^="Lyrics__Container"], .song_body-lyrics p'):
                text += tag.get_text(strip=True, separator='\n')
            while len(text) > 2000:
                msg_text.append(text[:2000])
                text = text[2000:]
            msg_text.append(text)
            return msg_text
        except Exception as e:
            print(e)
    return "**Не найдено на https://genius.com/**"
