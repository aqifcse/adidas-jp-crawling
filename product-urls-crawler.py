from bs4 import BeautifulSoup
from requests_html import HTMLSession

session = HTMLSession()

hdr = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.105 Safari/537.36'}

keyword = 'pant'

file_object = open('urls.txt', 'a')

def get_urls_from_keyword(keyword):
    for page in range(1, 32):
        resp = session.get('https://shop.adidas.jp/item/?q=' + keyword + '&page=' + str(page), headers=hdr, timeout=15)
        soup = BeautifulSoup(resp.content, 'html.parser')
        products = soup.find_all('div', {'class':'articleDisplayCard-children'})

        product_url_list = []
        for product in products:
            product_url = product.find('a')['href']
            file_object.write('https://shop.adidas.jp' + product_url + '\n')

get_urls_from_keyword(keyword)