# -*- coding: utf-8 -*-
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.120 Safari/537.36'
}

url = 'http://collection.sdmart.org'
page_url = '/PRT0?rec={}&sid=638&x=32655&sort=9'

img_path = './img/'

dase_name = 'sdmart'
table_name = 'sdmart'

MYSQL = {
    'host': 'localhost',
    'port': 3306,
    'user': 'temp',
    'password': '123456',
    'database': dase_name,
    'charset': 'utf8'
}

start_page = 1
end_page = 2078