import os

from selenium import webdriver

from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

from discord_bot.text_song import get_lyrics

gecko = os.path.normpath(os.path.join(os.path.dirname(__file__), 'geckodriver'))
driver = webdriver.Firefox(executable_path=gecko + '.exe')
Song = 'SHADOWRAZE — SHOWDOWN'
driver.get('https://genius.com/search?q=' + Song)

element = driver.find_element(by=By.CLASS_NAME, value='mini_card')
element.click()
url = driver.current_url  # Find text

# elem.send_keys('SHADOWRAZE — SHOWDOWN')
