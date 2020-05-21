# scrape_data.py
# Functions to download web pages

import pickle
import logging
from glob import glob
from time import sleep
from functools import reduce
from datetime import datetime, date

from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from bs4 import BeautifulSoup
from inflection import parameterize

import s3_helper

TODAY = date.today().strftime("%m_%d_%Y")
BRANDS = [
    'J._Crew', 'Naked_&_Famous_Denim', "Levi's", 'Diesel', 'Hugo_Boss',
    'Mavi', 'Big_Star', 'Lucky_Brand', 'True_Religion', 'Wrangler', 'Gap', 'Uniqlo'
    ]
PAGES = 20
logging.basicConfig(filename='logs/scraping.log',
                    filemode='w',
                    format='%(asctime)s - %(message)s',
                    datefmt='%d-%b-%y %H:%M:%S')


def headless_download_page(url):
    "Download HTML source for the given city using a headless Firefox instance"
    options = Options()
    options.headless = True
    driver = webdriver.Firefox(options=options, log_path='logs/geckodriver.log')
    driver.get(url)
    print(url)
    sleep(3)
    html_text = driver.page_source
    driver.close()

    return html_text


def collect_pages(brand):
    "Collect all the pages for a given search query"
    count = 1
    more_pages = True
    pages = []

    while more_pages:
        url = f"https://poshmark.com/brand/{brand}-Men-Jeans?availability=all&sort_by=added_desc&max_id={count}"
        logging.info(url)
        page = headless_download_page(url)
        pages.append(page)
        count += 1
        sleep(3)

        soup = BeautifulSoup(page, 'html.parser')
        btns = soup.find_all('button', class_ = 'btn--pagination')

        if btns[-1].has_attr('disabled'):
            more_pages = False

        if count == PAGES:
            more_pages = False

    return pages

def create_soup(source):
    "Convert HTML source to BeautifulSoup object"
    soup = BeautifulSoup(source, 'html.parser')
    return soup


def extract_tiles(soup):
    "Extract all the clothing tile elements"
    containers = soup.find_all('div', class_ = 'tile')
    return containers


def extract_title(tile):
    "Extract the title string from a tile"
    try:
        title = tile.find('a', class_='tile__title').get_text(strip=True)
    except:
        title = ''

    return title


def extract_status(tile):
    "Extract the status from a tile"
    try:
        status = tile.find('span', class_='condition-tag').get_text(strip=True)
    except:
        status = ''

    return status


def extract_stock(tile):
    "Extract the stock status from a tile"
    try:
        stock = tile.find('i', class_='sold-tag').get_text(strip=True)
    except:
        stock = ''

    return stock


def extract_price(tile):
    "Extract the price integer from a tile"
    try:
        price = tile.find('span', class_="fw--bold").get_text(strip=True)
    except:
        price = ''

    return price


def extract_size(tile):
    "Extract the size integer from a tile"
    try:
        size = tile.find('a', class_="tile__details__pipe__size").get_text(strip=True)
    except:
        size = ''

    return size


def extract_brand(tile):
    "Extract the brand string from a tile"
    try:
        brand = tile.find('a', class_="tile__details__pipe__brand").get_text(strip=True)
    except:
        brand = ''

    return brand


def extract_link(tile):
    "Extract the link string from a tile"
    try:
        link = tile.find('a', class_='tile__title').get('href')
    except:
        link = ''

    return link


def extract_image(tile):
    "Extract the image link string from a tile"
    try:
        image = tile.find('img').get('data-src')
    except:
        image = ''

    return image


def extract_date(url):
    "Extract the posting date from a url"

    try:
        start = url.find('20')
        end = start + 10
        date = url[start:end]
    except:
        date = ''

    return date


def combine_data(tile):
    "Run independent functions and return object of all values"
    title = extract_title(tile)
    status = extract_status(tile)
    stock = extract_stock(tile)
    price = extract_price(tile)
    size = extract_size(tile)
    brand = extract_brand(tile)
    link = extract_link(tile)
    image = extract_image(tile)
    date = extract_date(image)

    return {
        'title': title,
        'status': status,
        'stock': stock,
        'price': price,
        'size': size,
        'brand': brand,
        'link': link,
        'image': image,
        'date': date,
    }


if __name__ == '__main__':
    for tag in BRANDS:
        print('Scraping', tag)
        pages = collect_pages(tag)
        soup_objs = [create_soup(page) for page in pages]
        item_tiles = [extract_tiles(soup) for soup in soup_objs]
        combined_tiles = reduce(lambda x,y: x+y, item_tiles)
        item_objs = [combine_data(tile) for tile in combined_tiles]

        brand_name = parameterize(tag, '_')
        file_name = f"raw_{brand_name}_{TODAY}.p"
        path = 'data/'
        pickle.dump(item_objs, open(path + file_name, 'wb'))
        logging.info(f"Scraped {tag} page, found {len(item_objs)} items")

        s3_helper.upload_file(file_name, path)
        print('Uploaded: ', file_name, 'to S3')
