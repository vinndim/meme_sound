import asyncio
from pprint import pprint

import aiohttp
from bs4 import BeautifulSoup


async def get_album_yandex(url):
    async with aiohttp.ClientSession() as session:
        async with session.get(url, allow_redirects=True) as resp:
            soup = BeautifulSoup(await resp.text(), 'lxml')
            album_title = soup.select_one('h1').text
            if album_title is not None:
                songs_titles = soup.select('a[class="d-track__title deco-link deco-link_stronger"]')
                lst_songs_titles = [title.get_text("\n", strip=True)
                                    for title in songs_titles]
                songs_durations = soup.select('span[class="typo-track deco-typo-secondary"]')
                lst_songs_durations = [dur.get_text("\n", strip=True)
                                       for dur in songs_durations]
                if url.count("/") > 4:
                    im_album = "https:" + soup.select_one('img[class="playlist-cover__img deco-pane"]').get("src")
                    im_songs = soup.select('img[class="entity-cover__image deco-pane"]')
                    lst_imgs_songs = ["https:" + im.get("src") for im in im_songs]
                    songs_executors = soup.select('span[class="d-track__artists"]')
                    lst_executors_tr = [ex.get_text("\n", strip=True)
                                        for ex in songs_executors]
                    return {"album_title": album_title, "lst_excutor_album": None,
                            "im_album": im_album, "lst_songs_titles": lst_songs_titles,
                            "lst_executors_tr": lst_executors_tr,
                            "lst_imgs_songs": lst_imgs_songs, "lst_songs_durations": lst_songs_durations}
                else:
                    im_album = "https:" + soup.select_one('img[class="entity-cover__image deco-pane"]').get("src")
                    executor = soup.select('a[class="d-link deco-link"]')
                    lst_excutor_album = list(filter(lambda x: x is not None, [ex.get("title") for ex in executor]))
                    return {"album_title": album_title, "lst_excutor_album": lst_excutor_album,
                            "im_album": im_album, "lst_songs_titles": lst_songs_titles, "lst_executors_tr": None,
                            "lst_imgs_songs": None, "lst_songs_durations": lst_songs_durations}
    return "Альбом не найден"


# data = asyncio.run(get_album_yandex("https://music.yandex.ru/users/dim.vinnickoff/playlists/1000"))
# pprint(data)

# sec = 0
# for j in range(len(data["lst_songs_durations"])):
#
#     for i in range(len(x := data["lst_songs_durations"][j].split(':'))):
#         sec += 60 ** i * int(x[i])
# print(sec)
