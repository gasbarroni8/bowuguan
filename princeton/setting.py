# -*- coding: utf-8 -*-
headers = {
    'accept': 'application/json',
    'content-type': 'application/x-ndjson',
    'Origin': 'https://artmuseum.princeton.edu',
    'Referer': 'https://artmuseum.princeton.edu/search/collections?cultureList=%5B%22Chinese%22%5D&typeList=%5B%22paintings%22%5D',
    'Sec-Fetch-Mode': 'cors',
    'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.120 Safari/537.36'
}

url = 'https://data.artmuseum.princeton.edu/searchindex/puam/artobjects/_msearch'
data_url = 'https://artmuseum.princeton.edu/collections/objects/'
img_min_url = '/full/!300,300/0/default.jpg'
img_max_url = '/full/full/0/default.jpg'
img_path = './img/'

dase_name = 'princeton'
table_name = 'princeton'

MYSQL = {
    'host': 'localhost',
    'port': 3306,
    'user': 'temp',
    'password': '123456',
    'database': dase_name,
    'charset': 'utf8'
}

start_page = 0
end_page = 1389
