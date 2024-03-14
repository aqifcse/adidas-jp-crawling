from bs4 import BeautifulSoup
from requests_html import HTMLSession

session = HTMLSession()

hdr = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.105 Safari/537.36'
}

keyword = 'pant'

def get_urls_from_keyword(keyword):
    with open('urls.txt', 'a') as file_object:
        for page in range(1, 32):
            try:
                resp = session.get(f'https://shop.adidas.jp/item/?q={keyword}&page={page}', headers=hdr, timeout=15)
                resp.raise_for_status()  # Raise exception for bad status codes

                soup = BeautifulSoup(resp.html.html, 'html.parser')
                products = soup.find_all('div', class_='articleDisplayCard-children')

                for product in products:
                    product_url = 'https://shop.adidas.jp' + product.find('a')['href']
                    file_object.write(product_url + '\n')
            except Exception as e:
                print(f"Error fetching URLs from page {page}: {e}")

get_urls_from_keyword(keyword)