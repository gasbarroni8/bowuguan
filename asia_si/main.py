# -*- coding: utf-8 -*-
import requests
import re
import time
from artworkclass import ArtworkClass
import os
from mysqlclass import MysqlClass
from setting import url, img_path, start_page, end_page, table_name, headers, img_min_url
from mylogclass import MyLogClass
from concurrent.futures import ThreadPoolExecutor, as_completed

mylogObj = MyLogClass()


def request(url):
    try:
        rq_response = requests.get(url, headers=headers, timeout=10)
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
        item_list = re.findall('<div class="search-thumbnail">(.*?)</article>', index_response.text, re.S)
        if item_list != []:
            for item in item_list:
                artObj = ArtworkClass()
                artObj.art_dict['page_url'] = index_response.url
                data_url = re.search('class="entry-title"><a href="(.*?)"', item, re.S)
                if data_url:
                    artObj.art_dict['data_url'] = data_url[1]
                museum_number = re.search('<span class="accession-number">(.*?)</span>', item, re.S)
                if museum_number:
                    artObj.art_dict['museum_number'] = museum_number[1].replace('/', '_').strip()
                title = re.search('class="entry-title"><a.*?>(.*?)</a>', item, re.S)
                if title:
                    artObj.art_dict['title'] = title[1].strip()
                img_url = re.search('<img src="(.*?)&', item, re.S)
                if img_url:
                    artObj.art_dict['img_min_url'] = img_url[1] + img_min_url
                    artObj.art_dict['img_min_path'] = img_path + 'min/' + artObj.art_dict['museum_number'] + '.jpg'
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
            max_list = re.findall('<img class="thumb swap ids-image".*?src="(.*?)[&"]', data_response.text, re.S)
            if max_list != []:
                artObj.art_dict['img_max_url'] = str(max_list)
                artObj.art_dict['img_max_path'] = str(
                    [img_path + 'max/' + artObj.art_dict['museum_number'] + '_' + str(i) + '.jpg' for i in
                     range(len(max_list))])
            Maker_list = re.findall('<dd class="Maker">(.*?)</dd>', data_response.text, re.S)
            if Maker_list != []:
                primaryMaker_list = []
                for maker in Maker_list:
                    primaryMaker_list.append(re.sub('<.*?>', '', maker))
                artObj.art_dict['primaryMaker'] = str(primaryMaker_list)
            date = re.search('<dd class="TimePeriod".*?>(.*?)</dd>', data_response.text, re.S)
            if date:
                artObj.art_dict['date'] = date[1].strip()
            medium = re.search('<dd class="Medium".*?>(.*?)</dd>', data_response.text, re.S)
            if medium:
                artObj.art_dict['medium'] = medium[1].strip()
            dimensions = re.search('<dd class="Dimensions".*?>(.*?)</dd>', data_response.text, re.S)
            if dimensions:
                artObj.art_dict['dimensions'] = dimensions[1].strip()
            creditline = re.search('<dd class="CreditLine".*?>(.*?)</dd>', data_response.text, re.S)
            if creditline:
                artObj.art_dict['creditline'] = creditline[1].strip()

            type = re.search('<dd class="inline">(.*?)</dd>', data_response.text, re.S)
            if type:
                classification = re.sub('<.*?>', '', type[1])
                artObj.art_dict['classification'] = classification

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
                max_url_list = eval(artObj.art_dict['img_max_url'])
                max_path_list = eval(artObj.art_dict['img_max_path'])
                for url, path in zip(max_url_list, max_path_list):
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
        print('请求：' + url.format(i))
        main_response = request(url.format(i))
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
        mylogObj.logger.warning(url.format(i))
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


if __name__ == '__main__':
    main()
