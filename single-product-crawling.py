
import json
import pandas as pd
from requests_html import HTMLSession
from bs4 import BeautifulSoup

session = HTMLSession()

hdr = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.105 Safari/537.36'}

urls = ['https://shop.adidas.jp/products/HB9386/']

def get_soup_from_url(url):
    resp = session.get(url, headers=hdr, timeout=15)
    soup = BeautifulSoup(resp.content, 'html.parser')
    return soup

def parse_breadcrumb_categories(soup):
    breadcrumb_categories = soup.find_all('li',{'class':'breadcrumbLink test-breadcrumbLink'})

    breadcrumb_category_list = []

    for breadcrumb_category in breadcrumb_categories:
        breadcrumb_category_list.append(breadcrumb_category.find('a').text)
    
    return breadcrumb_category_list

def parse_size_chart(soup):
    model_link = soup.find('link',{'rel':'canonical'})['href']
    model = model_link.replace('https://shop.adidas.jp/model/', "")
    size_chart_resp = session.get('https://shop.adidas.jp/f/v1/pub/size_chart/' + model)
    size_chart_data = size_chart_resp.json()
    return size_chart_data['size_chart']

def parse_category_name(soup):
    category_name = soup.find('span', {'class':'categoryName test-categoryName'}).text
    return category_name

# def parse_image_urls(soup):
#     image_urls = soup.find('ul', {'class':'selectable-image-group css-iqyys7'}).find_all('li')

#     print(image_urls)

#     image_url_list = []
#     for image_url in image_urls:
#         image_url_list.append(image_url.find('a').find('img')['src'])

#     return image_url_list

    

    

if __name__ == '__main__':

    for url in urls:
        data = get_soup_from_url(url)

        # parse require data
        size_chart = parse_size_chart(data)
        breadcrumb_categories = parse_breadcrumb_categories(data)
        category_name = parse_category_name(data)
        # image_urls = parse_image_urls(data)
        
        



