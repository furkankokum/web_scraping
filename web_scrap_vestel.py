import requests
from bs4 import BeautifulSoup

header = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.0.0 "
                  "Safari/537.36",
}
MAIN_URL = 'https://www.vestel.com.tr'

def get_html(URL):
    r = requests.get(URL,headers=header)
    soup = BeautifulSoup(r.text,'lxml')
    return soup

def category_page_links(MAIN_URL):
    '''
        INPUT: https://www.vestel.com.tr

        OUTPUT: https://www.vestel.com.tr/beyaz-esya-c-1  type:list
                https://www.vestel.com.tr/tv-ses-c-2
        '''
    category_links=[]
    main_url_soup=get_html(MAIN_URL)
    category_links_raw=main_url_soup.find("ul",attrs={"class":"menu-list"}).find_all("li",attrs={"class":"parent-menu-wrap"})

    for category_links_index in range(len(category_links_raw)):
        category_links.append(str(MAIN_URL)+str(category_links_raw[category_links_index].find("a").get("href")))
    return category_links


def product_group_links(category_link):
    '''
       INPUT: https://www.vestel.com.tr/beyaz-esya-c-1

       OUTPUT: https://www.vestel.com.tr/buzdolabi-c-13
            https://www.vestel.com.tr/derin-dondurucular-c-15
       '''

    category_url_soup = get_html(category_link)
    global category_name
    category_name=category_url_soup.find("span",attrs={"class":"cat-name"}).get_text()
    category_raw=category_url_soup.find_all("li",attrs={"class":"item col col-12 col-xl-3"})
    product_group_pages=[]

    for category_index in range(len(category_raw)):
        product_group_pages.append(str(MAIN_URL)+str(category_raw[category_index].find("a").get("href")))

    return product_group_pages

def number_of_product_in_page(product_group_page):
    "Finding a number of the product pages"
    number_of_product_in_page_soup=get_html(product_group_page)
    number_of_product=number_of_product_in_page_soup.find("div",attrs={"data-total":True}).get("data-total")
    return number_of_product

def collecting_product_links(product_group_page):
    '''
           INPUT: https://www.vestel.com.tr/buzdolabi-c-13

           OUTPUT:
                list of urls => https://www.vestel.com.tr/vestel-puzzle-fd65101-ex-maya-588-lt-no-frost-buzdolabi-p-2516
           '''
    products_links=[]
    number=number_of_product_in_page(product_group_page)
    product_soup=get_html(product_group_page+f"/?dropListingPageSize={number}")
    products_links_html=product_soup.find_all("li",attrs={"class":"col col-12 col-lg-4 col-xl-4 product-list-item-wrap js-product-item"})

    for products_link_html in products_links_html:
        half_product_link=products_link_html.find("a").get("href")
        product_link=str(MAIN_URL)+str(half_product_link)

        if product_link not in products_links:
            products_links.append(product_link)
    return products_links


def collecting_product_details(products_links):
    """
    Input: https://www.vestel.com.tr/vestel-puzzle-fd65101-ex-maya-588-lt-no-frost-buzdolabi-p-2516
    Ouput: Lİst of each product info as a dict

    """
    products=[]
    product_count_by_feature={}

    for product in products_links:
        product_soup=get_html(product)
        features={}
        tech_info_elements = product_soup.find("div", attrs={"class": "tech-info"})
        li_elements = tech_info_elements.find_all("li")
        # Get the key and value of feature in product --> li_element(label,value)
        for li_element in li_elements:
            key = li_element.find("span", attrs={"class": "label"}).get_text()
            value = li_element.find("span", attrs={"class": "value"}).get_text()
            # To not count duplicate products again
            if value not in features:
                features[key] = value
                # Get the number of feature that common in all products
                if value not in product_count_by_feature:
                    product_count_by_feature[value]=0
                product_count_by_feature[value]+=1


        price_with_spaces = product_soup.find("span", attrs={"class": "discounted"}).get_text()
        price_with_str = price_with_spaces.split(" ")

        # Extract the product main details from html (like model,price,)
        model = product_soup.find("div", attrs={"class": "product-short-desc"}).find("h1").get_text().strip()
        brand=model.split(" ")[0].capitalize()
        list=category_name

        # Get the number(int) without TL
        price = int(((price_with_str[0].replace(".", ""))))
        image_link=product_soup.find_all("a",attrs={"class":"inline-popup-gallery group1 cboxElement"})[0].get("href")

        product_info = {
            "model": model,
            "brand": brand,
            "price": price,
            "list": list,

            "features": features,
            "picture": image_link,
        }

        products.append(product_info)

    return products,product_count_by_feature

def get_sorted_features(product_count_by_feature):

    sorted_features = sorted(product_count_by_feature.items(), key=lambda x: x[1], reverse=True)
    return sorted_features

def get_max_n_features(sorted_features,n):
    dict_sorted_features=dict(sorted_features)
    max_n_features=list(dict_sorted_features.items())[:n]
    print(max_n_features)


def startUp():
    category_links=category_page_links(MAIN_URL)
    print("Reaching Website...")

    product_group_page=product_group_links(category_links[2])[0]
    print("Reaching Category Links...")

    product_links=collecting_product_links(product_group_page)
    print("Reaching Product Group Links...")

    result,product_count_by_feature=collecting_product_details(product_links)
    print("Reaching Product Details ...")

    sorted_f=get_sorted_features(product_count_by_feature)
    custom=int(input("Specify How Many Features You Want To Come In Order: "))

    print("Listing Features In Order...")
    get_max_n_features(sorted_f,custom)


startUp()
