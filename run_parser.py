import asyncio
import time

import aiohttp
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse, urljoin

prices = []
raw_prices = []


def get_raw_links_from_page_text(html_page_text, tag, class_):
    soup = BeautifulSoup(html_page_text, 'html.parser')
    return soup.find_all(tag, class_)


def get_page_links(html_page_text, main_url):
    soup = BeautifulSoup(html_page_text, 'html.parser')
    page_links = soup.find(class_='catalog-noscript-pagination')
    page_numbers = page_links.get_text(' ', strip=True).split()
    page_links = []
    for page_number in page_numbers:
        page_link = main_url.replace('5', page_number)
        page_links.append(page_link)
    return page_links

async def process_link(link, website):
    item_url = urljoin(website, link.get('href'))
    # print(f'Processing {item_url}')
    async with aiohttp.ClientSession() as session:
        async with session.get(item_url) as response:
            response_code = response.status
            if response_code == 200:
                html_page_text = await response.text()
                soup = BeautifulSoup(html_page_text, 'html.parser')
                price = soup.find_all('div', class_='supreme-product-card__price-discount-price')
                name = soup.find('h1', class_='supreme-product-card__about-title')
                strip_price = ''.join(symbol if symbol.isdigit() else ' ' for symbol in str(price).split()).strip() if price else 'price not found'
                strip_name = name.get_text(strip=True) if name else 'name not found'
                name_and_price = {strip_name: strip_price}
                prices.append(name_and_price)
            if response_code == 503:
                # print('Retrying in 1 second')
                await asyncio.sleep(0.5)
                await process_link(link, website)


def run_parser(main_url):
    print(main_url)
    parsed = urlparse(main_url)
    print(parsed)
    website = f'{parsed.scheme}://{parsed.netloc}'
    print(website)

    loop = asyncio.get_event_loop()
    tasks = []

    html_page_text = requests.get(main_url).text
    page_links = get_page_links(html_page_text, main_url)

    print(page_links)
    links = get_raw_links_from_page_text(html_page_text, 'a', 'cl-item-link js-cl-item-link js-cl-item-root-link')
    for link in links:
        # print(link)
        tasks.append(process_link(link, website))

    loop.run_until_complete(asyncio.gather(*tasks))
    loop.close()

    print(prices)

