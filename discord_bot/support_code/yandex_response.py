from pprint import pprint
from bs4 import BeautifulSoup
import requests


def get_album_yandex(url):
    try:
        resp = requests.get(url)
        soup = BeautifulSoup(resp.content, 'lxml')
        songs_titles = soup.select('a[class="d-track__title deco-link deco-link_stronger"]')
        lst_songs_titles = [title.get_text("\n", strip=True)
                            for title in songs_titles]
        songs_durations = soup.select('span[class="typo-track deco-typo-secondary"]')
        lst_songs_durations = [dur.get_text("\n", strip=True)
                               for dur in songs_durations]
        if url.count("/") > 4:
            album_title = soup.select_one('h1').text
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
            album_title = soup.select_one('span[class="deco-typo"]').get_text()
            im_album = "https:" + soup.select_one('img[class="entity-cover__image deco-pane"]').get("src")
            executor = soup.select('a[class="d-link deco-link"]')
            lst_excutor_album = list(filter(lambda x: x is not None, [ex.get("title") for ex in executor]))
            return {"album_title": album_title, "lst_excutor_album": lst_excutor_album,
                    "im_album": im_album, "lst_songs_titles": lst_songs_titles, "lst_executors_tr": None,
                    "lst_imgs_songs": None, "lst_songs_durations": lst_songs_durations}
    except Exception:
        return None