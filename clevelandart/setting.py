# -*- coding: utf-8 -*-
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.120 Safari/537.36'
}

url = 'https://www.clevelandart.org'

url_search = '/art/collection/search?filter-department=Chinese+Art&i=2&limit=48&skip={}'

img_path = './clevelandart/'

MYSQL = {
    'host': 'localhost',
    'port': 3306,
    'user': 'temp',
    'password': '123456',
    'database': 'clevelandart',
    'charset': 'utf8'
}


start_page = 0
end_page = 2408