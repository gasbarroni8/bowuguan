# -*- coding: utf-8 -*-
import requests
import re
import time
from artworkclass import ArtworkClass
import os
from mysqlclass import MysqlClass
from setting import headers, url, page_url, img_path, start_page, end_page, table_name
from mylogclass import MyLogClass
from concurrent.futures import ThreadPoolExecutor, as_completed
import json

mylogObj = MyLogClass()


def request(url):
    try:
        rq_response = requests.get(url, headers=headers)
        if rq_response.status_code == 200:
            mylogObj.logger.info(url + "请求成功！")
            return rq_response
        else:
            mylogObj.logger.warning(url + "请求失败！code:" + str(rq_response.status_code))
            return None
    except Exception as e:
        mylogObj.logger.warning(url + "请求失败！code:" + str(rq_response.status_code))
        mylogObj.logger.warning(e)
        return None


def parser_index(in_response):
    try:
        item_list = re.findall('<div data-emuseum-id(.*?)</div></div></div></div>', in_response.text, re.S)
        if item_list != []:
            for item in item_list:
                artObj = ArtworkClass()
                primaryMaker = re.search('<div class="primaryMaker.*?>(.*?)</div>', item, re.S)
                if primaryMaker:
                    artObj.art_dict['primaryMaker'] = primaryMaker[1]
                invno = re.search('<div class="invno.*?</span>(.*?)</div>', item, re.S)
                if invno:
                    artObj.art_dict['invno'] = invno[1].replace('/', '_')
                creditline = re.search('<div class="creditline.*?</span>(.*?)</div>', item, re.S)
                if creditline:
                    artObj.art_dict['creditline'] = creditline[1]
                dimensions = re.search('<div class="dimensions.*?</span>(.*?)</div>', item, re.S)
                if dimensions:
                    artObj.art_dict['dimensions'] = dimensions[1]
                medium = re.search('<div class="medium.*?</span>(.*?)</div>', item, re.S)
                if medium:
                    artObj.art_dict['medium'] = medium[1]
                displayDate = re.search('<div class="displayDate.*?</span>(.*?)</div>', item, re.S)
                if displayDate:
                    artObj.art_dict['displayDate'] = displayDate[1]
                title_url = re.search('<div class="title.*?href="(.*?)">(.*?)</a>', item, re.S)
                if title_url:
                    artObj.art_dict['data_url'] = url + title_url[1]
                    artObj.art_dict['title'] = title_url[2]
                img_min_url = re.search('class="emuseum-img-wrap.*?src="(.*?)">', item, re.S)
                if img_min_url:
                    artObj.art_dict['img_min_url'] = url + img_min_url[1]
                    artObj.art_dict['img_max_url'] = artObj.art_dict['img_min_url'].replace('postagestamp', 'full')
                    artObj.art_dict['img_min_path'] = img_path + 'min/' + artObj.art_dict['invno'] + '.png'
                    artObj.art_dict['img_max_path'] = img_path + 'max/' + artObj.art_dict['invno'] + '.png'
                artObj.art_dict['page_url'] = in_response.url
                if artObj.art_dict['data_url'] != '':
                    artObj = parser_data(artObj)
                yield artObj
    except Exception as e:
        mylogObj.logger.warning(in_response.url)
        mylogObj.logger.warning(e)


def parser_data(artObj):
    try:
        # 请求详情页
        da_response = request(artObj.art_dict['data_url'])
        if da_response:
            description = re.search('<span class="toggleContent">(.*?)<', da_response.text)
            if description:
                artObj.art_dict['description'] = description[1]
            classification_list = re.findall('eognl:current.type.type.*?<span>(.*?)</span>', da_response.text)
            if classification_list != []:
                artObj.art_dict['classification'] = classification_list[1]
    except Exception as e:
        mylogObj.logger.warning(artObj.art_dict['data_url'])
        mylogObj.logger.warning(e)
    return artObj


def save_img(artObj):
    try:
        # 保存缩略图
        if artObj.art_dict['img_min_url'] != '':
            if not os.path.exists(artObj.art_dict['img_min_path']):
                img_response = request(artObj.art_dict['img_min_url'])
                if img_response:
                    if not os.path.exists(img_path + 'min/'):
                        os.makedirs(img_path + 'min/')
                    with open(artObj.art_dict['img_min_path'], 'wb') as f:
                        f.write(img_response.content)
                        print('保存图片成功：' + artObj.art_dict['img_min_path'])
        # 保存大图
        if artObj.art_dict['img_max_url'] != '':
            max_url_list = eval(artObj.art_dict['img_max_url'])
            max_path_list= eval(artObj.art_dict['img_max_path'])
            for url,path in zip(max_url_list,max_path_list):
                if not os.path.exists(path):
                    img_response = request(url)
                    if img_response:
                        if not os.path.exists(img_path + 'max/'):
                            os.makedirs(img_path + 'max/')
                        with open(path, 'wb') as f:
                            f.write(img_response.content)
                            print('保存图片成功：' + path)
    except Exception as e:
        mylogObj.logger.warning('保存图片失败：' + artObj.art_dict['museum_number'])
        mylogObj.logger.warning(e)


# 多线程任务
def run_thread(i):
    try:
        # 请求索引页
        print('请求：' + url + page_url.format(i))
        run_response = request(url + page_url.format(i))
        # 得到索引
        if run_response:
            # 得到数据生成器
            artObj_generator = parser_index(run_response)

            for artObj in artObj_generator:
                # 保存数据库
                try:
                    mysqlObj = MysqlClass()
                    mysqlObj.my_insert(table_name, artObj)
                    mylogObj.logger.info('保存数据成功：' + artObj.art_dict['invno'])
                except Exception as e:
                    mylogObj.logger.warning('保存数据失败：' + artObj.art_dict['invno'])
                    mylogObj.logger.warning(e)
                finally:
                    mysqlObj.close()
                # 保存图片
                save_img(artObj)
    except Exception as e:
        mylogObj.logger.warning(url + page_url.format(i))
        mylogObj.logger.warning(e)


def main():
    with ThreadPoolExecutor(max_workers=200) as executor:
        future_list = []
        for i in range(start_page, end_page):
            time.sleep(1)
            # 创建任务
            obj = executor.submit(run_thread, i)
            # 添加任务列表
            future_list.append(obj)
        # 得到任务的返回结果
        for future in as_completed(future_list):
            future.result()


# 得到全部字段及内容长度
def getall_key():
    all_attr = {}
    for n in range(1, 113):
        k_response = requests.get(url.format(1), headers=headers)
        for result in k_response.json()['es_apiResponse']['es_result']:
            for field in result['ibmsc_field']:
                text = re.sub('<.*?>', '', field['#text'])
                if field['id'] not in all_attr.keys():
                    all_attr[field['id']] = len(text)
                else:
                    if len(text) > all_attr[field['id']]:
                        all_attr[field['id']] = len(text)

    all_attr_sorted = sorted(all_attr.items(), key=lambda x: x[1])
    print(all_attr_sorted)
    with open('all_attr.txt', 'w', encoding='utf-8') as f:
        f.write(str(all_attr_sorted))


if __name__ == '__main__':
    main()
