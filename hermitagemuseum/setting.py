# -*- coding: utf-8 -*-
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.120 Safari/537.36'
}

url = 'https://www.hermitagemuseum.org/api/v10/search?resultLang=en&queryLang=en&collection=mainweb|kamis|rooms|hermitage&query=meta_woa_cntr_org:(%22China%22)%20AND%20meta_authoring_template:(%22WOA%22)&pageSize=10&page={}&output=application/json'
min_url = 'https://www.hermitagemuseum.org/images/'
max_url = 'https://www.hermitagemuseum.org'
data_url = 'https://www.hermitagemuseum.org/wps/portal/hermitage/digital-collection/'
img_path = './img/'

dase_name = 'hermitagemuseum'
table_name = 'hermitagemuseum'

MYSQL = {
    'host': 'localhost',
    'port': 3306,
    'user': 'temp',
    'password': '123456',
    'database': dase_name,
    'charset': 'utf8'
}

start_page = 1
end_page = 113
