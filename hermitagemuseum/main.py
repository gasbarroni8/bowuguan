# -*- coding: utf-8 -*-
import requests
import re
import time
from artworkclass import ArtworkClass
import os
from mysqlclass import MysqlClass
from setting import headers, url, min_url, max_url, img_path, data_url, start_page, end_page, table_name
from mylogclass import MyLogClass
from concurrent.futures import ThreadPoolExecutor, as_completed
import json

mylogObj = MyLogClass()


def request(url):
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            mylogObj.logger.info(url + "请求成功！")
            return response
        else:
            mylogObj.logger.warning(url + "请求失败！code:" + str(response.status_code))
            return None
    except Exception as e:
        mylogObj.logger.warning(url + "请求失败！code:" + str(response.status_code))
        mylogObj.logger.warning(e)
        return None


def parser_index(response):
    try:
        for es_result in json.loads(response.text)['es_apiResponse']['es_result']:
            # 生成每条数据
            artObj = ArtworkClass()
            for field in es_result['ibmsc_field']:
                if field['id'] in artObj.art_dict.keys():
                    text = re.sub('<.*?>', '', field['#text'])
                    artObj.art_dict[field['id']] = text
            # 得到详情页
            try:
                new_data_url = data_url + artObj.art_dict['meta_contentpath'].split('/')[-2] + '/' + \
                               artObj.art_dict['meta_contentpath'].split('/')[-1]
            except Exception as e:
                new_data_url = None
                mylogObj.logger.warning(artObj.art_dict['meta_contentpath'])
                mylogObj.logger.warning(e)

            artObj.art_dict['page_url'] = response.url
            artObj.art_dict['data_url'] = new_data_url
            artObj.art_dict['img_min_url'] = min_url + artObj.art_dict['title'][0] + '/' + artObj.art_dict['title'][
                1] + '/' + artObj.art_dict['title'] + '.s.jpg'
            artObj.art_dict['img_min_path'] = img_path + 'min/' + artObj.art_dict['title'] + '.s.jpg'

            # 请求详情页得到大图url
            if artObj.art_dict['data_url']:
                artObj = parser_data(artObj)
            yield artObj

    except Exception as e:
        mylogObj.logger.warning(response.url)
        mylogObj.logger.warning(e)


def parser_data(artObj):
    try:
        # 请求详情页
        response = request(artObj.art_dict['data_url'])
        if response:
            # 得到大图url
            max_url_result = re.search('class="her-zoomable" src="(.*?)"', response.text)
            artObj.art_dict['img_max_url'] = max_url + max_url_result[1]
            artObj.art_dict['img_max_path'] = img_path + 'max/' + artObj.art_dict['title'] + '.s.jpg'
    except Exception as e:
        mylogObj.logger.warning(artObj.art_dict['data_url'])
        mylogObj.logger.warning(e)
    return artObj


def save_img(artObj):
    try:
        # 保存缩略图
        if artObj.art_dict['img_min_url'] != '':
            if not os.path.exists(artObj.art_dict['img_min_path']):
                response = request(artObj.art_dict['img_min_url'])
                if response:
                    if not os.path.exists(img_path + 'min/'):
                        os.makedirs(img_path + 'min/')
                    with open(artObj.art_dict['img_min_path'], 'wb') as f:
                        f.write(response.content)
                        print('保存图片成功：' + artObj.art_dict['img_min_path'])
        # 保存大图
        if artObj.art_dict['img_max_url'] != '':
            if not os.path.exists(artObj.art_dict['img_max_path']):
                response = request(artObj.art_dict['img_max_url'])
                if response:
                    if not os.path.exists(img_path + 'max/'):
                        os.makedirs(img_path + 'max/')
                    with open(artObj.art_dict['img_max_path'], 'wb') as f:
                        f.write(response.content)
                        print('保存图片成功：' + artObj.art_dict['img_max_path'])
    except Exception as e:
        mylogObj.logger.warning('保存图片失败：' + artObj.art_dict['title'])
        mylogObj.logger.warning(e)


# 多线程任务
def run_thread(i):
    try:
        # 请求索引页
        print('请求：' + url.format(i))
        response = request(url.format(i))
        # 得到索引
        if response:
            # 得到数据生成器
            artObj_generator = parser_index(response)
            for artObj in artObj_generator:
                # 保存数据库
                try:
                    mysqlObj = MysqlClass()
                    mysqlObj.my_insert(table_name, artObj)
                    mylogObj.logger.info('保存数据成功：' + artObj.art_dict['title'])
                except Exception as e:
                    mylogObj.logger.warning('保存数据失败：' + artObj.art_dict['title'])
                    mylogObj.logger.warning(e)
                finally:
                    mysqlObj.close()
                # 保存图片
                save_img(artObj)
    except Exception as e:
        mylogObj.logger.warning(url.format(i))
        mylogObj.logger.warning(e)


def main():
    with ThreadPoolExecutor(max_workers=50) as executor:
        future_list = []
        for i in range(start_page, end_page):
            time.sleep(2)
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
        response = requests.get(url.format(1), headers=headers)
        for result in response.json()['es_apiResponse']['es_result']:
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
