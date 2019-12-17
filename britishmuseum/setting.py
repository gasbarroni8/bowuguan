# -*- coding: utf-8 -*-
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.120 Safari/537.36',
    'Referer': 'https://www.britishmuseum.org/',
}

url = 'https://www.britishmuseum.org'
page_url = '/research/collection_online/search.aspx?searchText=china+painting&images=true&lookup-people=e.g.+Hokusai,+Ramesses&people=&lookup-place=e.g.+India,+Shanghai,+Thebes&place=&from=ad&fromDate=&to=ad&toDate=&lookup-object=e.g.+bowl,+hanging+scroll,+print&object=&lookup-subject=e.g.+farming,+New+Testament&subject=&lookup-matcult=e.g.+Choson+Dynasty,+Ptolemaic&matcult=&lookup-technique=e.g.+carved,+celadon-glazed&technique=&lookup-school=e.g.+French,+Mughal+Style&school=&lookup-material=e.g.+canvas,+porcelain,+silk&material=&lookup-ethname=e.g.+Hmong,+Maori,+Tai&ethname=&lookup-ware=e.g.+Imari+ware,+Qingbai+ware&ware=&lookup-escape=e.g.+cylinder,+gravity,+lever&escape=&lookup-bibliography=&bibliography=&citation=&museumno=&catalogueOnly=&view=https://www.britishmuseum.org/research/collection_online/search.aspx&page={}'

img_path = './img/'

dase_name = 'britishmuseum'
table_name = 'britishmuseum'

MYSQL = {
    'host': 'localhost',
    'port': 3306,
    'user': 'temp',
    'password': '123456',
    'database': dase_name,
    'charset': 'utf8'
}

start_page = 1
end_page = 15
