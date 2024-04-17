import asyncio
import time

import aiohttp
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse, urljoin

prices = []
raw_prices = []

pages_response_codes = []


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
    try:
        href = link.get('href')
        # print(website, href)
        item_url = urljoin(website, href)
        # print(item_url)

        # print(f'Processing {item_url}')
        async with aiohttp.ClientSession() as session:
            async with session.get(item_url) as response:
                response_code = response.status
                if response_code == 200:
                    await asyncio.sleep(1)
                    print('Processing ' + link.get('href'))
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
                    await asyncio.sleep(1)
                    await process_link(link, website)
    except aiohttp.client_exceptions.InvalidURL as error:
        print(error)
        return
    except aiohttp.client_exceptions.ClientOSError:
        print('Client OSError')
        return


async def process_page_link(link, website='https://sunlight.net'):
    async with aiohttp.ClientSession() as session:
        async with session.get(link) as response:
            response.code = response.status
            match response.status:
                case 200:
                    html_page_text = await response.text()
                    items_links = get_raw_links_from_page_text(html_page_text, 'a', 'cl-item-link js-cl-item-link js-cl-item-root-link')
                    for link in items_links:
                        await process_link(link, website)
                case 503:
                    await asyncio.sleep(1)
                    await process_page_link(link)


async def run_parser(main_url):
    parsed = urlparse(main_url)
    website = f'{parsed.scheme}://{parsed.netloc}'

    async with aiohttp.ClientSession() as session:
        html_page_response = await session.get(main_url)
        html_page_text = await html_page_response.text()
        page_links = get_page_links(html_page_text, main_url)

        tasks = []
        # links = get_raw_links_from_page_text(html_page_text, 'a', 'cl-item-link js-cl-item-link js-cl-item-root-link')
        for link in page_links:
            tasks.append(process_page_link(link, website))
        await asyncio.gather(*tasks)

    print(prices)
    # print(pages_response_codes)
    # print(len(pages_response_codes))
    print(len(prices))
