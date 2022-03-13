import re
import urllib.request
from bs4 import BeautifulSoup


def get_lyrics(url):
    content = urllib.request.urlopen(url).read()
    print(url)
    print(content)
    # lyrics lies between up_partition and down_partition
    # up_partition = '<!-- Usage of azlyrics.com content by any third-party lyrics provider ' \
    #                'is prohibited by our licensing agreement. Sorry about that. -->'
    # down_partition = '<!-- MxM banner -->'
    # lyrics = lyrics.split(up_partition)[1]
    # lyrics = lyrics.split(down_partition)[0]
    # lyrics = lyrics.replace('<br>', '').replace('</br>', '').replace('</div>', '').strip()
