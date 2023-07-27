import requests

from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup as bs
from random import randint


url = "https://www.fragrantica.com/perfume/Tom-Ford/Tobacco-Vanille-1825.html#all-reviews"

with sync_playwright() as p:
    browser = p.firefox.launch(headless=False, slow_mo=300)
    context = browser.new_context(user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.114 Safari/537.36')
    page = context.new_page()

    page.goto(url, wait_until='commit')
    page.wait_for_timeout(randint(592,831))
    page.mouse.wheel(delta_x=0, delta_y=float(randint(4141,4549)))
    page.wait_for_timeout(randint(947,1792))
    html = bs(page.content(), 'html.parser')

    # page.wait_for_timeout(randint(4587, 5861))
    # page.wait_for_selector('title')

    revs = html.select("div.flex-child-auto > div > p")

    tmp_rev = []
    print(len(set(revs)))
    # if len(revs) > 0:
    #     for review in revs:
    #         tmp_rev.append(review.text.strip())
    
    # for index, i in enumerate(set(tmp_rev), start=1):
    #     print(str(index) + ": " + i)
    #     #insert into db