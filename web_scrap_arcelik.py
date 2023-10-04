import requests
from bs4 import BeautifulSoup
import json

# pip install  beatifulsoup  json requests

header = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.0.0 "
                  "Safari/537.36",
}
MAIN_URL = 'https://www.arcelik.com.tr'

def get_html(URL):
    r = requests.get(URL,headers=header)
    soup = BeautifulSoup(r.text,'lxml')             ####  SOURCE CODE GELIR
    return soup


def category_page_links(MAIN_URL):
    '''
    INPUT: https://www.arcelik.com.tr

    OUTPUT: https://www.arcelik.com.tr/beyaz-esya  type:list
            https://www.arcelik.com.tr/ankastre
    '''

    main_url_soup = get_html(MAIN_URL)
    features_raw = main_url_soup.find('ul', attrs={'class': 'ul-clear menu-category'}).find_all("li", attrs={
        "class": "lv1-li"})

    category_links = []
    for category_index in range(len(features_raw)):
        category_links.append(str(MAIN_URL) + str(features_raw[category_index].find("a").get("href")))

    return category_links


def product_group_links(category_link):
    '''
    INPUT: https://www.arcelik.com.tr/beyaz-esya

    OUTPUT: https://www.arcelik.com.tr/bulasik-makinesi
            https://www.arcelik.com.tr/buzdolabi
    '''

    category_url_soup = get_html(category_link)
    category_raw = category_url_soup.find('ul', attrs={'class': 'ul-clear category-list'}).find_all("li")
    product_group_page = []

    for sub_category in range(len(category_raw)):
        product_group_page.append(str(MAIN_URL) + str(category_raw[sub_category].find("a").get("href")))

    return product_group_page


def numberOfPages(product_group_page):
    "Finding a number of the product pages"

    numberOfPages_soup=get_html(product_group_page)
    numberofPages_real=json.loads(numberOfPages_soup.find("div",attrs={"class":"col-12 productGridPage-page"}).find("span",attrs={"data-options":True}).get("data-options"))["numberOfPages"]

    return numberofPages_real


def collecting_product_links(product_group_page):
    """
    INPUT: https://www.arcelik.com.tr/buzdolabi

    OUTPUT: list of urls --> https://www.arcelik.com.tr/no-frost-buzdolabi/574561-ei-buzdolabi
    """

    product_group = product_group_page.split("/")[-1].replace('-', ' ').capitalize()
    num_page = int(numberOfPages(product_group_page))
    product_links = []

    for i in range(1, num_page + 1):
        product_group_page_iterate = product_group_page + f"?page={i}"
        product_soup = get_html(product_group_page_iterate)
        application_ld = product_soup.find_all("script", attrs={"type": "application/ld+json"})[1].text
        json_application_ld = json.loads(application_ld)
        number_of_product_in_page=application_ld.count("position")

        n=0
        while n<number_of_product_in_page:
            prod_sub_url=json_application_ld["itemListElement"][n]["item"]["offers"]["url"]
            n+=1
            prod_link=str(MAIN_URL)+str(prod_sub_url)

            if prod_link not in product_links:
                product_links.append(prod_link)

    return product_group, product_links



def collection_product_detail(product_links):
    """
    INPUT: https://www.arcelik.com.tr/no-frost-buzdolabi/574561-ei-buzdolabi

    OUTPUT: Lİst of each product info as a dict

    """
    products = []
    product_count_by_feature = {}

    # Get the key of feature in product --> v_element
    for product in product_links:
        product_soup = get_html(product)
        features = {}
        v_elements = product_soup.find_all('div', attrs={"class": "v"})
        # Get the value of feature in product --> t_element
        for v_element in v_elements:
            t_element = v_element.find_next_sibling('div', attrs={"class": "t"})
            feature = v_element.text.strip()
            # To not count duplicate products again
            if t_element is not None and feature not in features:
                features[feature] = t_element.text.strip().replace('\xa0', ' ')
                # Get the number of feature that common in all products
                if feature not in product_count_by_feature:
                    product_count_by_feature[feature] = 0
                product_count_by_feature[feature] += 1

        # Extract the product details from the GTM impression data
        gtm_impression = json.loads(product_soup.find('div', class_='pdp')['data-gtm-impression'])
        model = gtm_impression['name']
        brand = gtm_impression['brand']
        list = gtm_impression['list']
        price = gtm_impression['price']

        swiper_container = product_soup.find("div", {"class": "swiper-zoom-container"})
        img = swiper_container.find("img")
        # Get the value of the srcset attribute
        srcset = img.get("data-srcset")
        link = "https://www.arcelik.com.tr/" + srcset.split(",")[0]

        product_info = {
            "model": model,
            "brand": brand,
            "price": price,
            "list": list,


            "features": features,
            "picture": link,
        }

        products.append(product_info)

    return products, product_count_by_feature

def get_sorted_features(product_count_by_feature):
    sorted_features = sorted(product_count_by_feature.items(), key=lambda x: x[1], reverse=True)
    return sorted_features

def get_max_n_features(sorted_features,n):
    dict_sorted_features=dict(sorted_features)
    max_n_features=list(dict_sorted_features.items())[:n]
    print(max_n_features)


def startUp():
    category_links = category_page_links(MAIN_URL)
    print("Reaching Website...")

    product_group_page = product_group_links(category_links[0])[1]
    print("Reaching Category Links...")

    product_group,product_links=collecting_product_links(product_group_page)
    print("Reaching Product Group Links...")

    result,product_count_by_feature= collection_product_detail(product_links)
    print("Reaching Product Details ...")

    sorted_f=get_sorted_features(product_count_by_feature)
    custom = int(input("Specify How Many Features You Want To Come In Order: "))

    get_max_n_features(sorted_f,custom)


startUp()