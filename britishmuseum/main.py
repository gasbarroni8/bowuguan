# -*- coding: utf-8 -*-
import requests
import re
import time
from artworkclass import ArtworkClass
import os
from mysqlclass import MysqlClass
from setting import url, page_url, img_path, start_page, end_page, table_name, headers
from mylogclass import MyLogClass
from concurrent.futures import ThreadPoolExecutor, as_completed

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


def parser_index(index_response):
    try:
        item_list = re.findall('class="grid_2.*?>(.*?)</div>', index_response.text, re.S)
        if item_list != []:
            for item in item_list:
                artObj = ArtworkClass()
                img_min_url = re.search('src="(.*?)\?', item, re.S)
                if img_min_url:
                    artObj.art_dict['img_min_url'] = url + img_min_url[1]
                data_url = re.search('class="imageCaption.*?href="(.*?)"', item, re.S)
                if data_url:
                    artObj.art_dict['data_url'] = url + data_url[1].replace('amp;', '')
                artObj.art_dict['page_url'] = index_response.url
                if artObj.art_dict['data_url'] != '':
                    artObj = parser_data(artObj)
                yield artObj
    except Exception as e:
        mylogObj.logger.warning(index_response.url)
        mylogObj.logger.warning(e)


def parser_data(artObj):
    try:
        # 请求详情页
        data_response = request(artObj.art_dict['data_url'])
        if data_response:
            title = re.search('property="og:title" content="(.*?)"', data_response.text)
            if title:
                artObj.art_dict['title'] = title[1]
            img_max_url = re.search('property="og:image" content="(.*?)"', data_response.text)
            if img_max_url:
                artObj.art_dict['img_max_url'] = img_max_url[1].replace('http', 'https')
            type = re.search('Object type.*?<ul>(.*?)</ul>', data_response.text, re.S)
            if type:
                classification = re.findall('<a.*?title="See all objects">(.*?)</a>', type[1], re.S)
                artObj.art_dict['classification'] = ','.join(classification)
            museum_number = re.search('Museum number.*?<p>(.*?)</p>', data_response.text, re.S)
            if museum_number:
                artObj.art_dict['museum_number'] = museum_number[1]
            description = re.search('<h3>Description</h3>.*?<p>(.*?)</p>', data_response.text, re.S)
            if description:
                artObj.art_dict['description'] = description[1]
            date = re.search('<h3>Date</h3>.*?<li>(.*?)</li>', data_response.text, re.S)
            if date:
                artObj.art_dict['date'] = date[1]
            medium = re.search('<h3>Materials</h3>.*?<li>(.*?)</li>', data_response.text, re.S)
            if medium:
                medium1 = re.sub('<.*?>', '', medium[1])
                artObj.art_dict['medium'] = medium1
            creditline = re.search('<h3>Acquisition name</h3>.*?<li>(.*?)</li>', data_response.text, re.S)
            if creditline:
                creditline1 = re.sub('<.*?>', '', creditline[1])
                artObj.art_dict['creditline'] = creditline1
            primaryMaker = re.search('<h3>Producer name</h3>.*?<li>(.*?)</li>', data_response.text, re.S)
            if primaryMaker:
                primaryMaker1 = re.sub('<.*?>', '', primaryMaker[1])
                artObj.art_dict['primaryMaker'] = primaryMaker1
            dimensions = re.search('<h3>Dimensions</h3>.*?<li>(.*?)</li>', data_response.text, re.S)
            if dimensions:
                dimensions1 = re.sub('<.*?>', '', dimensions[1])
                artObj.art_dict['dimensions'] = dimensions1
            artObj.art_dict['img_min_path'] = img_path + 'min/' + artObj.art_dict['museum_number'] + '.jpg'
            artObj.art_dict['img_max_path'] = img_path + 'max/' + artObj.art_dict['museum_number'] + '.jpg'
    except Exception as e:
        mylogObj.logger.warning(artObj.art_dict['data_url'])
        mylogObj.logger.warning(e)
    finally:
        return artObj


def save_img(artObj):
    try:
        if artObj.art_dict['museum_number'] != '':
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
                if not os.path.exists(artObj.art_dict['img_max_path']):
                    img_response = request(artObj.art_dict['img_max_url'])
                    if img_response:
                        if not os.path.exists(img_path + 'max/'):
                            os.makedirs(img_path + 'max/')
                        with open(artObj.art_dict['img_max_path'], 'wb') as f:
                            f.write(img_response.content)
                            print('保存图片成功：' + artObj.art_dict['img_max_path'])
    except Exception as e:
        mylogObj.logger.warning('保存图片失败：' + artObj.art_dict['museum_number'])
        mylogObj.logger.warning(e)


# 多线程任务
def run_thread(i):
    try:
        # 请求索引页
        print('请求：' + url + page_url.format(i))
        main_response = request(url + page_url.format(i))
        # 得到索引
        if main_response:
            # 得到数据生成器
            artObj_generator = parser_index(main_response)

            for artObj in artObj_generator:
                # 保存数据库
                try:
                    mysqlObj = MysqlClass()
                    mysqlObj.my_insert(table_name, artObj)
                    mylogObj.logger.info('保存数据成功：' + artObj.art_dict['museum_number'])
                except Exception as e:
                    mylogObj.logger.warning('保存数据失败：' + artObj.art_dict['museum_number'])
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
