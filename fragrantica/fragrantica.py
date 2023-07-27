# python3.8 playwright_luminati.py '{"proxy_platform":"luminati","luminati_country":"us","luminati_username":"hl_7fb35c97","luminati_zone":"fragrantica","luminati_password":"nrk6aj9igkzp"}'

import sys
import urllib.parse
import json
import time
import random
from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup as bs
import mysql.connector
import re

class db_handler:

    def __init__(self, database='', host='', username='', password='', port=3306):
        
        self.database = database
        self.host = host
        self.username = username
        self.password = password
        self.port = port


    def get_db_connection(self):

        connection = mysql.connector.connect(
            host = self.host,
            database = self.database,
            username = self.username,
            password = self.password,
            port = self.port
        )

        return connection
    

    def insert_cats(self, cat):
        try:
            connection = self.get_db_connection()
            cursor = connection.cursor()
            query = ' INSERT INTO fragnatica_cats (cat) VALUES(%s) '
            cursor.execute(query, (cat,))
            connection.commit()
        except mysql.connector.Error as e:
            print(f"python error: failed to insert cat. {e}")
        finally:
            if (connection.is_connected()):
                cursor.close()
                connection.close()
        return []
    

    def insert_urls(self, url):
        try:
            connection = self.get_db_connection()
            cursor = connection.cursor()
            query = ' INSERT INTO fragnatica_product_urls (url) VALUES(%s) '
            cursor.execute(query, (url,))
            connection.commit()
        except mysql.connector.Error as e:
            print(f"python error: failed to insert url. {e}")
        finally:
            if (connection.is_connected()):
                cursor.close()
                connection.close()
        return []
    

    def set_product_url_visited(self, url):
        try:
            connection = self.get_db_connection()
            cursor = connection.cursor()

            query = ' UPDATE fragnatica_product_urls SET `visited`= 1 WHERE `url` = %s '
            cursor.execute(query, (url,))
            connection.commit()
        except mysql.connector.Error as error:
            print("PYTHON ERROR: Failed to update visited field. {}".format(error))
        finally:
            if (connection.is_connected()):
                cursor.close()
                connection.close()

    
    def set_cat_visited(self, cat):
        try:
            connection = self.get_db_connection()
            cursor = connection.cursor()

            query = ' UPDATE fragnatica_cats SET `visited`= 1 WHERE `cat` = %s '
            cursor.execute(query, (cat,))
            connection.commit()
        except mysql.connector.Error as error:
            print("PYTHON ERROR: Failed to update visited field. {}".format(error))
        finally:
            if (connection.is_connected()):
                cursor.close()
                connection.close()



    def get_product_urls(self):
        try:
            connection = self.get_db_connection()
            cursor = connection.cursor(dictionary=True, buffered=True)
            query = ' SELECT url FROM fragnatica_product_urls WHERE visited=0 '
            cursor.execute(query)
        except mysql.connector.Error as e:
            print(f"python error: failed to return urls. {e}")
        finally:
            if(connection.is_connected()):
                cursor.close()
                connection.close()
        return cursor.fetchall()
    

    def get_cats(self):
        try:
            connection = self.get_db_connection()
            cursor = connection.cursor(dictionary=True, buffered=True)
            query = ' SELECT cat FROM fragnatica_cats WHERE visited=0 '
            cursor.execute(query)
        except mysql.connector.Error as e:
            print(f"python error: failed to return cats. {e}")
        finally:
            if(connection.is_connected()):
                cursor.close()
                connection.close()
        return cursor.fetchall()


    def clear_table(self, table_name):
        try:
            connection = self.get_db_connection()
            cursor = connection.cursor()

            query = ' DELETE FROM ' + table_name
            cursor.execute(query) # cursor.execute(query, (table_name,))
            connection.commit()
        except mysql.connector.Error as e:
            print(f"PYTHON ERROR: Failed to delete visited field. {e}")
        finally:
            if (connection.is_connected()):
                cursor.close()
                connection.close()


    def insert(self,table_name, data_dict):
        try:
            connection = self.get_db_connection()
            cursor = connection.cursor()
            defs = ['`'+key+'`' for key in data_dict.keys()]

            vals =  data_dict.values()
            val_placeholder = ['%s' for _ in range(0,len(vals))]
            query = 'INSERT INTO '+table_name+' (' + ', '.join(defs) + ') VALUES (' +', '.join(val_placeholder)+')'
            print(query)
            cursor.execute(query, tuple(vals))
            connection.commit()
        except mysql.connector.Error as error:
            print("PYTHON ERROR: Failed at inserting into "+table_name+". {}".format(error))
        finally:
            if (connection.is_connected()):
                cursor.close()
                connection.close()

        



# For localhost testing
# db = db_handler(
# 	host='localhost',
# 	database='fragnatica',
# 	username='nikola',
# 	password='123123',
# 	port = 3306)

# For server6 
db = db_handler(
    host='localhost',
    database='nikola',
    username='nikolad',
    password="rh4jhf4jf",
    port = 3306
)

playwright_args = urllib.parse.unquote(sys.argv[1])
playwright_args = json.loads(playwright_args)
#playwright_args['username']

# link = "http://lumtest.com/myip.json"

proxy="123"

def get_page(link, prod=False):
    with sync_playwright() as p:
        headless = True
        slow_mo = 50
        accept_downloads = True
        if proxy != 'proxyfalse':
            if playwright_args['proxy_platform'] == 'luminati':
                timeint = str(time.time()).replace('.', '')
                timeint = int(timeint)
                timeint = str(timeint)
                ip_section = '-ip-'+proxy
                if 'luminati_country' in playwright_args:
                    ip_section = '-country-'+playwright_args['luminati_country']
                proxy_object = {
                    "server": 'http://zproxy.lum-superproxy.io:22225',
                    "username": 'lum-customer-'+playwright_args['luminati_username']+'-zone-'+playwright_args['luminati_zone']+ip_section+'-dns-local-session-'+timeint,
                    "password": playwright_args['luminati_password']
                }
            else:
                proxy_object = { "server": proxy }
            # print('Proxy:')
            # print(json.dumps(proxy_object))
            browser = p.chromium.launch(headless = headless, slow_mo = slow_mo, proxy =  proxy_object)
        else:
            browser = p.chromium.launch(headless = headless, slow_mo = slow_mo)

        context = browser.new_context(user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.114 Safari/537.36')
        page = context.new_page()

        if prod == True:
            page.goto(str(link + '#all-reviews'),wait_until='commit')
            page.wait_for_timeout(random.randint(592,831))
            page.mouse.wheel(delta_x=0, delta_y=float(random.randint(4141,4549)))
            page.wait_for_timeout(random.randint(1547,2492))

            # page.wait_for_timeout(randint(4587, 5861))
            # page.wait_for_selector('img[class="comments-avatar"]')
        
        else:
            
            page.goto(link)
            page.mouse.wheel(delta_x=0, delta_y=float(random.randint(100,500)))

        # page.wait_for_timeout(random.randint(1000,3000))

        return page.content()




# urls = [
#     "https://www.fragrantica.com/designers/Acqua-di-Parma.html",
#     "https://www.fragrantica.com/designers/Bath-Body-Works.html",
#     "https://www.fragrantica.com/designers/Comme-des-Garcons.html",
#     "https://www.fragrantica.com/designers/Givenchy.html",
#     "https://www.fragrantica.com/designers/Lush.html",
#     "https://www.fragrantica.com/designers/Parfums-de-Marly.html",
#     "https://www.fragrantica.com/designers/Victoria-s-Secret.html"
#     "https://www.fragrantica.com/designers/Zoologist-Perfumes.html"
# ]


base_url = "https://www.fragrantica.com"

def get_cats():
    designer_links = []

    designer_num = [x for x in range(1,12)]
    random.shuffle(designer_num)

    for i in designer_num:

        url = base_url + f"/designers-{i}/"

        title="Just a moment"
        while "Just a moment" in title:

            try:
            
                # print(url)
                page = get_page(url)

                content = bs(page, 'html.parser')

                items = content.select("div.designerlist.cell.small-6.large-4 > a")

                for item in items:
                    designer_link = str(base_url + item.get("href"))
                    designer_links.append(designer_link)
                    db.insert_cats(designer_link)
                    print(designer_link)
                
                print(content.find('title').text)

            except Exception as e:
                print(e)

        time.sleep(random.randint(1,3))




def get_prod_urls():
     
    cats = []
    # fetch categories from db where visited = 0
    category = db.get_cats()
    print(len(category))
    for i in category:
        for cat in i.values():
            cats.append(cat)

    random.shuffle(cats)

    print(len(cats))
    # visit each category and scrape product urls
    cnt = len(cats)
    for cat in cats:
        try:
            print(f"urls left to scrape: {cnt}")
            cnt=cnt-1
            page = get_page(cat)
            content = bs(page, 'html.parser')

            if 'Just a moment' in content.find('title').text:

                ## bot detected so dont waste time go onto the next category
                continue

            parf_links = content.select('div.flex-child-auto > h3 > a')

            if len(parf_links) > 0:
                for parf in parf_links:
                    link = str(base_url + parf.get("href"))
                    print(link)
                    try:
                        db.insert_urls(link)
                    except Exception as e:
                        print(e)

            db.set_cat_visited(cat)
        except Exception as e:
            print(e)

    print("finished with getting urls, checkin if there is more in the db where visited=0")

    if len(db.get_cats()) > 0:
        print("called get_prod_urls from inside of the function")
        get_prod_urls()

    print("\n"*2)
    print("FETCHED ALL PROD URLS ! ! !")
    time.sleep(random.randint(1,3))





def get_prods():

    ## get urls from db where visited=0

    urls = []
    # fetch categories from db where visited = 0
    db_urls = db.get_product_urls()
    for i in db_urls:
        for url in i.values():
            urls.append(url)

    random.shuffle(urls)

    print(len(urls))
    # visit each prod url and scrape info

    cnt = len(urls)
    for url in urls:
        print(f"urls left to scrape: {cnt}")
        print(f"getting ===>  {url}")
        cnt = cnt - 1
        try:
            page = get_page(url, prod=True)
            content = bs(page, 'html.parser')

            if 'Just a moment' in content.find('title').text:
                
                ## bot detected so dont waste time go onto the next url
                continue

            if content.find("h1", class_="text-center") != None:
                    title = content.find("h1", class_="text-center").text
            else:
                title = ""

            if len(content.select("div.cell.small-12 > p")) > 0:
                desc = content.select("div.cell.small-12 > p")[0].text
            else:
                desc = ""

            if len(content.select("p.info-note > span")) > 0:
                rating = content.select("p.info-note > span")[0].text
            else:
                rating = ""

            prod = {
                'name' : title,
                'description' : desc,
                'rating' : rating,
                'url' : url,

            }

            if len(content.select("div.flex-child-auto > div > p")) > 0:    # if reviews found, make dict and insert it into db
                reviews = content.select("div.flex-child-auto > div > p")

                for rev in reviews:
                    # remove unicode chars, they cant go into db
                    rev_clean = re.sub(r"[^\x00-\x7F]+", "", rev.text.strip())

                    rev_prod = {
                        'name' : title,
                        'reviews' : rev_clean
                    }

                    try:
                        db.insert('fragnatica_reviews', rev_prod)
                    except Exception as e:
                        print("Could not insert review into fragnatica_reviews: ", e)

            elif len(content.select("div.flex-child-auto > div > p")) == 0:     # if reviews not found, insert just name into db
                rev_prod = {
                    'name' : title
                }
                try:
                    db.insert('fragnatica_reviews', rev_prod)
                except Exception as e:
                    print(f"There was an error inserting prod without revires: {e}")

            print(f"Product title {title}, product description: {desc} product rating: {rating}")
            print("\n"*2)

            try:
                db.insert('fragnatica_products', prod)
                db.set_product_url_visited(url)
            except Exception as e:
                print("Could not insert product into fragnatica_products: ", e)

        except Exception as e:
            print(e)


    print("finished with getting urls, checkin if there is more in the db where visited=0")

    if len(db.get_product_urls()) > 0:
        print("called get_prods from inside of the function")
        get_prods()

get_cats()
get_prod_urls()
get_prods()



## ako ponovo budes pustao ovaj scrape:
## 1) napravi da duze ceka na svakom product url, i da mozda skrola jos dole zbog ucitavanja komentara
## 2) napravi da loopuje kroz SET tih komentara da izbegnes duplikate
## 3) CISTI komentare (reviewove) od NAVODNIKA, posle ako treba da se izvozi u CSV bude rasulo
## 4) preimenuj tabele iz fragnatica u fragrantica