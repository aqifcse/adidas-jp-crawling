import os.path
import json
import pandas as pd
from requests_html import HTMLSession
from bs4 import BeautifulSoup
from requests.exceptions import Timeout
from urllib.parse import urljoin

session = HTMLSession()

hdr = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.105 Safari/537.36'}

def get_soup_from_url(url, timeout=90, retries=3):
    try:
        for _ in range(retries):
            try:
                resp = session.get(url, headers=hdr, timeout=timeout)
                resp.raise_for_status()  # Raise exception for bad status codes
                # Render JavaScript content
                resp.html.render(timeout=timeout)
                soup = BeautifulSoup(resp.html.html, 'html.parser')
                return soup
            except Timeout:
                print("Request timed out. Retrying...")
                continue
        print("Exceeded maximum number of retries.")
        return None
    except Exception as e:
        print("Error fetching URL:", e)
        return None

def get_review_script(soup):
    try:
        script_data = json.loads(soup.find('script', {'type':'application/ld+json'}).text)
    except AttributeError:
        script_data = {}
    return script_data 

def parse_coordinate_products(url):
    product_code = url.replace('https://shop.adidas.jp/products/', '')
    api_v2_url = 'https://shop.adidas.jp/f/v2/web/pub/products/article/' + product_code
    api_v2_resp = session.get(api_v2_url, headers=hdr).json()

    if not api_v2_resp.get('product') == None:
        if not api_v2_resp.get('product').get('article').get('coordinates') == None:
            coordinate_products = api_v2_resp['product']['article']['coordinates']['articles']
        else:
            coordinate_products = []
    else:
        coordinate_products = []

    coordinate_product_list = []
    coordinate_product_dict = {
        'coordinate_product_name':'',
        'coordinate_product_pricing':'',
        'coordinate_product_number':'',
        'coordinate_product_image_url':'',
        'coordinate_product_link':''
    }

    for coordinate_product in coordinate_products:
        coordinate_product_name = coordinate_product['name']
        coordinate_product_pricing = coordinate_product['price']['current']['withTax']
        coordinate_product_number = coordinate_product['articleCode']
        coordinate_product_image_url = 'https://shop.adidas.jp' + coordinate_product['image']
        coordinate_product_link = 'https://shop.adidas.jp/products/' + coordinate_product['articleCode'] + '/'

        coordinate_product_dict = {
            'coordinate_product_name': coordinate_product_name,
            'coordinate_product_pricing': coordinate_product_pricing,
            'coordinate_product_number': coordinate_product_number,
            'coordinate_product_image_url': coordinate_product_image_url,
            'coordinate_product_link': coordinate_product_link
        }

        coordinate_product_list.append(coordinate_product_dict)
    
    return coordinate_product_list

def parse_title_of_description(soup):
    try:
        title_of_description = soup.find('h4', {'class': 'heading itemFeature test-commentItem-subheading'}).text
    except AttributeError:
        title_of_description = None
    return title_of_description

def parse_general_description_of_the_product(soup):
    try:
        general_description_of_the_product = soup.find('div', {'class':'commentItem-mainText test-commentItem-mainText'}).text
    except AttributeError:
        general_description_of_the_product = None
    return general_description_of_the_product

def parse_general_description_itemization(soup):
    try:
        general_description_itemization = soup.find('div', {'class':'description clearfix test-descriptionBlock'}).find('ul').text
    except AttributeError:
        general_description_itemization = None
    return general_description_itemization

def parse_overall_rating(script):
    if not script.get('aggregateRating') == None:
        overall_rating = script['aggregateRating']['ratingValue']
    else:
        overall_rating = None
    return overall_rating

def parse_total_number_of_reviews(script):
    if not script.get('aggregateRating') == None:
        total_number_of_reviews = script['aggregateRating']['reviewCount']
    else:
        total_number_of_reviews = None
    return total_number_of_reviews

def parse_recommended_rate(soup):
    recommended_rate = ''
    try:
        # Find the element with class 'BVRRRatingPercentage'
        rating_percentage_div = soup.find('div', class_='BVRRRatingPercentage')
        
        # Check if the element exists
        if rating_percentage_div:
            # Find the element with class 'BVRRNumber' within 'BVRRRatingPercentage'
            recommended_rate_element = rating_percentage_div
            
            # Extract text content if the element exists
            if recommended_rate_element:
                recommended_rate = recommended_rate_element.text.strip()
    except Exception as e:
        print("Error parsing recommended rate:", e)
    return recommended_rate

def parse_sense_of_fitting_and_its_rating(soup):
    sense_of_fitting_and_its_rating = ''
    return sense_of_fitting_and_its_rating

def parse_appropriation_of_length_and_its_rating(soup):
    appropriation_of_length_and_its_rating = ''
    return appropriation_of_length_and_its_rating

def parse_quality_of_material_and_its_rating(soup):
    quality_of_material_and_its_rating = ''
    return quality_of_material_and_its_rating

def parse_comfort_and_its_rating(soup):
    comfort_and_its_rating = ''
    return comfort_and_its_rating

def parse_review_list_from_script(script):
    if not script.get('review') == None:
        reviews = script['review']
    else:
        reviews = []

    review_list = []

    review_dict = {
        'date': '',
        'rating': '',
        'title': '',
        'review_description': '',
        'reviewer_id': ''
    }
    
    for review in reviews:
        date = review['datePublished']
        rating = review['reviewRating']['ratingValue']
        title = ''
        review_description = review['reviewBody']
        reviewer_id = review['identifier']

        review_dict = {
            'date': date,
            'rating': rating,
            'title': title,
            'review_description': review_description,
            'reviewer_id': reviewer_id
        }

        review_list.append(review_dict)
    
    return review_list

def parse_kws(soup):
    kws = soup.find_all('a', {'data-ga-event-category':'pdp-tag_cloud'})
    
    kw_list = []
    for kw in kws:
        keyword = kw.text
        kw_list.append(keyword)

    return kw_list
    
def parse_size_chart(soup, url):
    try:
        model_link = soup.find('link', {'rel': 'canonical'})['href']
        model = model_link.replace('https://shop.adidas.jp/model/', "")
        
        # Retry fetching the size chart with increased timeout
        retries = 3  # Number of retry attempts
        for _ in range(retries):
            try:
                size_chart_resp = session.get('https://shop.adidas.jp/f/v1/pub/size_chart/' + model, timeout=60)  # Increase timeout to 60 seconds
                size_chart_resp.raise_for_status()  # Raise exception for bad status codes
                size_chart_total_data = size_chart_resp.json()
                only_size_chart_data = size_chart_total_data['size_chart']

                # Parse size chart data into a nested list of lists
                size_chart_nested_list = []
                for chart_key in only_size_chart_data:
                    for header_key in only_size_chart_data[chart_key]['header']:
                        row_values = []
                        for row_key in only_size_chart_data[chart_key]['header'][header_key]:
                            row_values.append(f"({header_key}, {row_key}): {only_size_chart_data[chart_key]['header'][header_key][row_key]['value']}")
                        size_chart_nested_list.append(row_values)
                    for body_key in only_size_chart_data[chart_key]['body']:
                        row_values = [f"({body_key}, {column_key}): {only_size_chart_data[chart_key]['body'][body_key][column_key]['value']}" for column_key in only_size_chart_data[chart_key]['body'][body_key]]
                        size_chart_nested_list.append(row_values)

                # Transpose the nested list
                size_chart_nested_list_transposed = list(zip(*size_chart_nested_list))

                # Convert transposed nested list to a string representation
                size_chart_string = '\n'.join(['\t'.join(row) for row in size_chart_nested_list_transposed])

                return size_chart_string
            except Timeout:
                print("Request timed out. Retrying...")
                continue
            except Exception as e:
                print("Error parsing size chart:", e)
                return None
        
        print("Exceeded maximum number of retries.")
        return None
    except Exception as e:
        print("Error fetching size chart URL:", e)
        return None

def parse_product_data(soup, url):
    product = {}
    # data = get_soup_from_url(url)
    review_script = get_review_script(soup)
    try:
        product['product_url'] = url
        breadcrumb_categories = soup.find_all('li', {'class': lambda x: x and 'breadcrumbListItem' in x.split() and 'back' not in x.split()})
        breadcrumb_items = []
        for breadcrumb in breadcrumb_categories:
            if 'back' not in breadcrumb.get('class', []):
                breadcrumb_items.append(breadcrumb.find('a').text.strip() if breadcrumb.find('a') else '')
        breadcrumb_string = '/'.join(breadcrumb_items)
        product['breadcrumb_categories'] = breadcrumb_string


        category_name_element = soup.find('a', {'class': 'groupName'})
        product['category_name'] = category_name_element.text.strip() if category_name_element else ''

        product_name_element = soup.find('h1', {'class': 'itemTitle test-itemTitle'})
        product['product_name'] = product_name_element.text.strip() if product_name_element else ''

        pricing_element = soup.select_one('div.articlePrice')
        product['pricing'] = pricing_element.text.strip() if pricing_element else ''

        image_elements = soup.find_all('img', {'class': 'selectableImage'})
        image_urls = []
        domain = 'https://shop.adidas.jp'

        for img in image_elements:
            image_url = urljoin(domain, img['src'])
            image_urls.append(image_url)

        product['image_urls'] = image_urls

        available_size_elements = soup.find_all('li', class_='sizeSelectorListItem')
        available_sizes = []

        for size_element in available_size_elements:
            size_button = size_element.find('button', class_='sizeSelectorListItemButton')
            if size_button:
                button_classes = size_button.get('class', [])
                if 'disable' not in button_classes:
                    available_sizes.append(size_button.text.strip())

        product['available_size'] = available_sizes
        product['size_chart'] = parse_size_chart(soup, url)
        product['coordinate_products_details'] = parse_coordinate_products(url)
        product['title_of_description'] = parse_title_of_description(soup)
        product['general_description_of_the_product'] = parse_general_description_of_the_product(soup)
        product['general_description_itemization'] = parse_general_description_itemization(soup)
        product['overall_rating'] = parse_overall_rating(review_script)
        product['total_number_of_reviews'] = parse_total_number_of_reviews(review_script)
        product['review_list'] = parse_review_list_from_script(review_script)
        product['kws'] = parse_kws(soup)

        return product
    except Exception as e:
        print("Error parsing product data:", e)
        return None

def export_scrape_data(product_data):
    file_path = './product-details.xlsx'
    try:
        if os.path.isfile(file_path):
            # If the file already exists, load the existing data
            existing_data = pd.read_excel(file_path)
            # Append the new data to the existing data
            df = pd.concat([existing_data, pd.DataFrame(product_data)], ignore_index=True)
        else:
            # If the file doesn't exist, create a new DataFrame with the new data
            df = pd.DataFrame(product_data)
        # Write the DataFrame to the Excel file
        df.to_excel(file_path, index=False)
        print("Data exported successfully!")
    except Exception as e:
        print("Error exporting data:", e)


def crawl_product_details(urls):
    for url in urls:
        print('Crawling Now!!! url:', url)
        soup = get_soup_from_url(url)
        if soup:
            product = parse_product_data(soup, url)
            if product:
                export_scrape_data([product])  # Export data for only one product
            else:
                print("Error parsing product data:", url)
        else:
            print("Error fetching URL or empty response:", url)

if __name__ == '__main__':
    with open('urls.txt') as f:
        urls = [url.strip() for url in f if url.strip()]  # Remove empty lines
    if urls:
        crawl_product_details(urls)  # Pass the list of URLs
    else:
        print("No URLs found in 'urls.txt'")









        



