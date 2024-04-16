import requests
from LxmlSoup import LxmlSoup
from urllib.parse import urlparse

# avito = 'https://avito.ru/all/kvartiry/prodam-ASgBAgICAUSSA8YQ?context=H4sIAAAAAAAA_0q0MrSqLraysFJKK8rPDUhMT1WyLrYyNLNSKk5NLErOcMsvyg3PTElPLVGyrgUEAAD__xf8iH4tAAAA'

hexlet = 'https://ru.hexlet.io'


# <a href="https://sunlight.net/catalog/bracelets_238528.html" class="cl-item-hover-img-wrap-link js-cl-item-link"></a>


# def run_parser():
#     response = requests.get(sunlight).text
#     print(response)
#     # , class_=
#     soup = LxmlSoup(response)
#     headings = soup.find_all('a')
#     print(headings)
#     for heading in headings:
#         url = heading.get('href')
#         print(url)

def run_parser(main_site):
    parsed = urlparse(main_site)
    website = f'{parsed.scheme}://{parsed.netloc}'
    html = requests.get(main_site).text
    soup = LxmlSoup(html)

    links = soup.find_all('a', class_='cl-item-link js-cl-item-link js-cl-item-root-link')
    for link in links:
        item_link = website + link.get('href')
        print(item_link)
        # run_parser(link.get('href'))
