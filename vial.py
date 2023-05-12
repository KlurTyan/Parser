import requests
from bs4 import BeautifulSoup

import re
import xlsxwriter

from tqdm import tqdm

url = 'https://vial.by/'

print('Работа парсера будет выполнена в течении от 5± минут, пожалуйста подождите.\n\nПРЕДУПРЕЖДЕНИЕ: Долгая работа парсера может зависить от вашей скорости интернета!')

header = {'user-agent': 'Mozilla/5.0 (Windows; U; Windows NT 6.1; en-US; rv:1.9.2.13) Gecko/20101213 Opera/9.80 (Windows NT 6.1; U; zh-tw) Presto/2.7.62 Version/11.01'}

params = {
    'limit': '300',
}
main_response = requests.get(url, headers=header).text
main_soup = BeautifulSoup(main_response, 'lxml')
navbar = main_soup.find('ul', class_ = 'nav navbar-nav')
link = navbar.find_all('li', class_ = None)

data = [['ID','URL','Категория','Название','Цена с учетом НДС']]    

def product(url, cat):
    r = requests.get(url, headers=header, params=params).text
    soup = BeautifulSoup(r, 'lxml')
    product_block = soup.find_all('div', class_ ='product-layout product-list col-xs-12')
    for i in product_block:
        re_id = re.search(r'class="product-thumb product_\d+"', str(i)).group(0)
        id = re.search(r'\d+', re_id).group(0)

        name = i.find('h4', class_ = None)
        link = name.find('a').get('href')

        price_block = i.find('div', class_ = 'price')
        if price_block is not None:
            price_re = re.findall(r'\d+', price_block.text)
            price = '.'.join(price_re).strip()
            data.append([id,link,cat,name.text.strip(), price])
        else:
            price_block = i.find('p', class_ = 'price na_zakaz').text.strip()
            data.append([id,link,cat,name.text.strip(), price_block])
def product_other(url, cat):
    r = requests.get(url, headers=header, params=params).text
    soup = BeautifulSoup(r, 'lxml')
    table_body = soup.find_all('tbody', class_ = 't431__tbody')
    for i in table_body:
        tr = i.find_all('tr')
        for j in tr:
            td = j.find_all('td')
            for table in td:
                link = table.find('a')

                price_block = table.find_next('td', class_ = 't431__td')
                
                name_b = table.find('b')
                if link is not None and price_block:
                    name = link.text
                    price_re = re.findall(r'\d+', price_block.text)
                    price = '.'.join(price_re).strip()

                    data.append(['NO ID',link.get('href'), cat, name,price])
                elif link is None and name_b:
                    link = 'https://vial.by/prosoft/'
                    data.append(['NO ID',link,cat,name_b.text, price])

for i in tqdm(link):  
    product_link = i.find('a', class_ = None)
    if product_link is not None:
        r = requests.get(product_link.get('href'),headers=header, params=params).text
        soup = BeautifulSoup(r, 'lxml')
        sub_cat = soup.find('a', class_ = 'col-xs-6 col-sm-4 col-md-3 col-lg-2')
        table = soup.find('tbody', class_ = 't431__tbody')
        if sub_cat:
            sub_cat = soup.find_all('a', class_ = 'col-xs-6 col-sm-4 col-md-3 col-lg-2')
            for sub_category in sub_cat:
                sub_cat_r = requests.get(sub_category.get('href'), headers=header   ).text
                sub_cat_soup = BeautifulSoup(sub_cat_r, 'lxml')
                subsub_cat = sub_cat_soup.find('a', class_ = 'col-xs-6 col-sm-4 col-md-3 col-lg-2')
                if subsub_cat:
                    subsub_cat = sub_cat_soup.find_all('a', class_ = 'col-xs-6 col-sm-4 col-md-3 col-lg-2')
                    for subsub_category in subsub_cat:
                        product(subsub_category.get('href'),subsub_category.text)
                else:
                    product(sub_category.get('href'),sub_category.text)
        elif sub_cat is None:
            product(product_link.get('href'),product_link.text)
        if table:
            product_other(product_link.get('href'),product_link.text)     

with xlsxwriter.Workbook('vial.xlsx') as wb:
    worksheet = wb.add_worksheet()

    for row_num, info in enumerate(data):
        worksheet.write_row(row_num, 0 ,info)