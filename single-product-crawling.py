import json
from requests_html import HTMLSession
from bs4 import BeautifulSoup

session = HTMLSession()

hdr = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.105 Safari/537.36'}

urls = ['https://shop.adidas.jp/products/HB9386/']

def get_soup_from_url(url):
    resp = session.get(url, headers=hdr, timeout=15)
    soup = BeautifulSoup(resp.content, 'html.parser')
    return soup

def get_review_script_from_url(url):
    resp = session.get(url, headers=hdr)
    soup = BeautifulSoup(resp.content, 'html.parser')
    script = json.loads(soup.find('script', {'type':'application/ld+json'}).text)
    return script 

# Parsing required data

def parse_breadcrumb_categories(soup):
    breadcrumb_categories = soup.find_all('li',{'class':'breadcrumbLink test-breadcrumbLink'})

    breadcrumb_category_list = []

    for breadcrumb_category in breadcrumb_categories:
        breadcrumb_category_list.append(breadcrumb_category.find('a').text)
    
    return breadcrumb_category_list

def parse_category_name(soup):
    try:
        category_name = soup.find('span', {'class':'categoryName test-categoryName'}).text
    except AttributeError:
        category_name = None 

    return category_name

def parse_image_urls(script):
    image_urls = script['image']

    image_url_list = []
    for image_url in image_urls:
        image_url_list.append('https://shop.adidas.jp' + image_url)

    return image_url_list

def parse_product_name(soup):
    try:
        product_name = soup.find('h1', {'class':'itemTitle test-itemTitle'}).text
    except AttributeError:
        product_name = None
    return product_name

def parse_pricing(soup):
    try:
        pricing = soup.find('p', {'class':'price-text mod-flat test-price-text'}).text
    except AttributeError:
        pricing = None
    return pricing

def parse_available_size(soup):
    
    available_sizes = soup.find('div', {'class':'inputSelects clearfix'}).find_all('div')[0].find('ul').find_all('li')

    available_size_list = []

    for available_size in available_sizes:
        available_size_text = available_size.find('button').text
        available_size_list.append(available_size_text)

    return available_size_list

# def parse_sense_of_the_size(soup):
#     try:
#         sense_of_the_size = soup.find('span', {'class':'categoryName test-categoryName'}).text
#     except AttributeError:
#         sense_of_the_size = None 

#     return sense_of_the_size

def parse_coordinate_products(url):
    product_code = url.replace('https://shop.adidas.jp/products/', '')
    api_v2_url = 'https://shop.adidas.jp/f/v2/web/pub/products/article/' + product_code
    api_v2_resp = session.get(api_v2_url, headers=hdr).json()
    coordinate_products = api_v2_resp['product']['article']['coordinates']['articles']

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
        title_of_description = soup.find('h4', {'class': 'itemFeature heading test-commentItem-subheading'}).text
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

def parse_size_chart(soup):
    model_link = soup.find('link',{'rel':'canonical'})['href']
    model = model_link.replace('https://shop.adidas.jp/model/', "")
    size_chart_resp = session.get('https://shop.adidas.jp/f/v1/pub/size_chart/' + model)
    size_chart_data = size_chart_resp.json()
    return size_chart_data['size_chart']

def parse_special_function_and_description(soup):
    try:
        special_function_and_description = soup.find('div', {'class':'contents js-technology_contents clearfix'}).text
    except AttributeError:
        special_function_and_description = None
    return special_function_and_description

def parse_overall_rating(script):
    overall_rating = script['aggregateRating']['ratingValue']
    return overall_rating

def parse_total_number_of_reviews(script):
    total_number_of_reviews = script['aggregateRating']['reviewCount']
    return total_number_of_reviews

# def parse_recommended_rate(soup):
#     recommended_rate = ''
#     print(recommended_rate)

# def parse_sense_of_fitting_and_its_rating(soup):
#     sense_of_fitting_and_its_rating = soup.find("div", {"class":"BVRRRating BVRRRatingRadio BVRRRatingFit"}).find("div", {"class":"BVRRRatingRadioImage"}).find("img").get("title")
#     print(sense_of_fitting_and_its_rating)

# def parse_appropriation_of_length_and_its_rating(soup):
#     appropriation_of_length_and_its_rating = soup.find("div", {"class":"BVRRRating BVRRRatingRadio BVRRRatingFit"}).find("div", {"class":"BVRRRatingRadioImage"}).find("img").get("title")
#     print(appropriation_of_length_and_its_rating)

# def parse_quality_of_material_and_its_rating(soup):
#     quality_of_material_and_its_rating = soup.find("div", {"class":"BVRRRating BVRRRatingRadio BVRRRatingFit"}).find("div", {"class":"BVRRRatingRadioImage"}).find("img").get("title")
#     print(quality_of_material_and_its_rating)

# def parse_comfort_and_its_rating(soup):
#     comfort_and_its_rating = soup.find("div", {"class":"BVRRRating BVRRRatingRadio BVRRRatingFit"}).find("div", {"class":"BVRRRatingRadioImage"}).find("img").get("title")
#     print(comfort_and_its_rating)

def parse_review_list_from_script(script):
    reviews = script['review']

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

if __name__ == '__main__':

    for url in urls:
        data = get_soup_from_url(url)
        review_script = get_review_script_from_url(url)

        # parse require data
        breadcrumb_categories = parse_breadcrumb_categories(data)
        category_name = parse_category_name(data)
        image_urls = parse_image_urls(review_script)
        product_name = parse_product_name(data)
        pricing = parse_pricing(data)
        available_size = parse_available_size(data)
        # sense_of_the_size = parse_sense_of_the_size(data)
        coordinate_products_details = parse_coordinate_products(url)
        title_of_description = parse_title_of_description(data)
        general_description_of_the_product = parse_general_description_of_the_product(data)
        general_description_itemization = parse_general_description_itemization(data)
        size_chart = parse_size_chart(data)
        special_function_and_description = parse_special_function_and_description(data)
        overall_rating = parse_overall_rating(review_script)
        total_number_of_reviews = parse_total_number_of_reviews(review_script)
        # recommended_rate = parse_recommended_rate(data)
        # sense_of_fitting_and_its_rating = parse_sense_of_fitting_and_its_rating(data)
        # appropriation_of_length_and_its_rating = parse_appropriation_of_length_and_its_rating(data)
        # quality_of_material_and_its_rating = parse_quality_of_material_and_its_rating(data)
        # comfort_and_its_rating = parse_comfort_and_its_rating(data)
        review_list = parse_review_list_from_script(review_script)
        kws = parse_kws(data)



        



