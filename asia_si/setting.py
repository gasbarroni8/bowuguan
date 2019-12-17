# -*- coding: utf-8 -*-
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.120 Safari/537.36'
}

url = 'https://asia.si.edu/collection-area/chinese-art/page/{}/'

img_path = './img/'
img_min_url = '&max_h=999&max_w=120'

dase_name = 'asia_si'
table_name = 'asia_si'

MYSQL = {
    'host': 'localhost',
    'port': 3306,
    'user': 'temp',
    'password': '123456',
    'database': dase_name,
    'charset': 'utf8'
}

start_page = 1
end_page = 701
