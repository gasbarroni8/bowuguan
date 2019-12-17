# -*- coding: utf-8 -*-
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.120 Safari/537.36'
}

url = 'https://art.nelson-atkins.org'
page_url ='/collections/27506/east-asian-art/objects/list?filter=thesfilter%3A1545150%3BmediaExistence%3Atrue&page={}'

img_path = './img/'

dase_name = 'nelson'
table_name = 'nelson'

MYSQL = {
    'host': 'localhost',
    'port': 3306,
    'user': 'temp',
    'password': '123456',
    'database': dase_name,
    'charset': 'utf8'
}

start_page = 1
end_page = 369

