import asyncio
import aiohttp
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse, urljoin

prices = []
raw_prices = []


async def process_link(link, website):
    item_url = urljoin(website, link.get('href'))
    print(f'Processing {item_url}')
    async with aiohttp.ClientSession() as session:
        async with session.get(item_url) as response:
            response_code = response.status
            if response_code == 200:
                html = await response.text()
                soup = BeautifulSoup(html, 'html.parser')
                price = soup.find('div', class_='supreme-product-card__price-discount-price')
                raw_prices.append(price)
                name = soup.find('h1', class_='supreme-product-card__about-title')
                strip_price = ''.join(symbol if symbol.isdigit() else ' ' for symbol in str(price).split()).strip() if price else 'price not found'
                strip_name = name.get_text(strip=True) if name else 'name not found'
                name_and_price = {strip_name: strip_price}
                prices.append(name_and_price)
            if response_code == 503:
                print('Retrying in 1 second')
                await asyncio.sleep(1)
                await process_link(link, website)


def run_parser(main_url):
    parsed = urlparse(main_url)
    website = f'{parsed.scheme}://{parsed.netloc}'
    html = requests.get(main_url).text
    soup = BeautifulSoup(html, 'html.parser')
    links = soup.find_all('a', class_='cl-item-link js-cl-item-link js-cl-item-root-link')

    loop = asyncio.get_event_loop()
    tasks = []
    for link in links:
        tasks.append(process_link(link, website))

    loop.run_until_complete(asyncio.gather(*tasks))
    loop.close()

    sorted_prices = sorted(prices, key=lambda price: list(price.values())[0])
    print(sorted_prices)
