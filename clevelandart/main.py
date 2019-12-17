# -*- coding: utf-8 -*-
import requests
import re
import time
from artworkclass import ArtworkClass
import os
from mysqlclass import MysqlClass
from setting import headers, url, url_search, img_path, start_page, end_page
from mylogclass import MyLogClass
from concurrent.futures import ThreadPoolExecutor, as_completed

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
    text = re.sub('<span class="search-artist-qualifier">attributed to </span>', '', response.text)
    page_list = re.findall(
        '<div class="search-result.*?"><div class="thumbnail"><a href="(.*?)"><img(.*?)/>.*?<div class="artwork-title"><a.*?>(.*?)</a></div><div class="artists">(.*?)</div>.*?<span class="accession-number">(.*?)</span>',
        text)
    return page_list


def parser_data(response, home_url, data_url, img_min_url):
    artworkObj = ArtworkClass()
    if 'data-src' in img_min_url:
        artworkObj.img_min_url = re.search('data-src="(.*?)"', img_min_url)[1]
    else:
        artworkObj.img_min_url = ''
    artworkObj.home_url = home_url
    artworkObj.data_url = data_url
    artworkObj.imgurl_list = []

    primary_title = re.search('class="field field-name-field-primary-title field-type-text field-label-hidden">(.*?)<',
                              response.text)  # primary-title英文名
    if primary_title:
        artworkObj.primary_title = primary_title[1].strip()
    translated = re.search('class="field-primary-title-translated">(.*?)<', response.text)  # translated 中文名
    if translated:
        artworkObj.translated = translated[1].strip()
    creation_time = re.search('class="field field-name-field-date-text field-type-text field-label-hidden">(.*?)<',
                              response.text)  # creation time 创作时间
    if creation_time:
        artworkObj.creation_time = creation_time[1].strip()
    artists = re.search('<div class="field field-name-art-object-artists">(.*?)</div>', response.text)  # artists 作者 删标签
    if artists:
        artworkObj.artists = re.sub('<.*?>', '', artists[1]).strip()
    creation_year = re.search('<p class="field field_name_field_creation_text">(.*?)</p>',
                              response.text)  # creation year年代 删标签
    if creation_year:
        artworkObj.creation_year = re.sub('<.*?>', '', creation_year[1]).strip()
    year_time = re.search('<div class="field field_name_field_creation_date">(.*?)</div>',
                          response.text)  # year time年代时间
    if year_time:
        artworkObj.year_time = year_time[1].strip()
    medium = re.search('<p class="field field-name-art-object-medium field-type-ds field-label-hidden">(.*?)</p>',
                       response.text)  # medium 材质
    if medium:
        artworkObj.medium = medium[1].strip()
    dimensions = re.search('<p class="field field-name-field-dimensions field-type-text field-label-hidden">(.*?)</p>',
                           response.text)  # dimensions 尺寸
    if dimensions:
        artworkObj.dimensions = dimensions[1].strip()
    credit_line = re.search('<span class="field field-name-field-credit-line">(.*?)</span>',
                            response.text)  # credit-line 来源
    if credit_line:
        artworkObj.credit_line = credit_line[1].strip()
    accession_number = re.search('<span class="field field-name-field-accession-number">(.*?)</span>',
                                 response.text)  # accession-number 加入时间
    if accession_number:
        artworkObj.accession_number = accession_number[1].strip()
    location = re.search(
        '<div class="field field-name-field-gallery-id field-type-text field-label-above">.*?<p>(.*?)</p>',
        response.text)  # LOCATION 位置
    if location:
        artworkObj.location = re.sub('<.*?>', '', location[1]).strip()
    description = re.search(
        '<div class="field field-name-field-description field-type-text-long field-label-above">.*?<p>(.*?)</p>',
        response.text)  # Description 描述
    if description:
        artworkObj.description = description[1].strip()
    artist_biography = re.search('<div class="field field-name-field-artist-biography">(.*?)<',
                                 response.text)  # ARTIST BIOGRAPHY 艺术家传记
    if artist_biography:
        artworkObj.artist_biography = artist_biography[1].strip()
    inscriptions_list = re.findall('Inscription</h3><p >(.*?)</p>', response.text, re.S)  # INSCRIPTIONS 题词  list
    if inscriptions_list != []:
        artworkObj.inscriptions = str(inscriptions_list)
    provenance_list = re.findall(
        '<div class="field field-name-field-provenance-date">(.*?)</div><div class="field field-name-field-provenance-description">(.*?)</div>',
        response.text, re.S)  # PROVENANCE 出处  list
    if provenance_list != []:
        artworkObj.provenance = str(provenance_list)
    classification = re.search(
        '<div class="field field-name-field-classification-text"><div class="label-inline">.*?</div><a.*?>(.*?)</a>',
        response.text)  # classification 分类
    if classification:
        artworkObj.classification = classification[1].strip()
    imgurl_list_old = re.findall('<div class="field-item even">.*?src="(.*?)"', response.text)  # img 图片url 替换 amp; list
    if imgurl_list_old != []:
        for url in imgurl_list_old:
            artworkObj.imgurl_list.append(re.sub('amp;', '', url))
    artworkObj.img_path = img_path + artworkObj.primary_title
    return artworkObj


def save_img(img_min_url, imgurl_list, primary_title):
    try:
        response = request(img_min_url)
        if response:
            if not os.path.exists(img_path + primary_title):
                os.makedirs(img_path + primary_title)
            with open(img_path + primary_title + '/min' + os.path.splitext(img_min_url)[1], 'wb') as f:
                f.write(response.content)
                print('保存成功：' + img_path + primary_title + '/min' + os.path.splitext(img_min_url)[1])
        for n, url in enumerate(imgurl_list):
            response = request(url)
            if response:
                if not os.path.exists(img_path + primary_title):
                    os.makedirs(img_path + primary_title)
                with open(img_path + primary_title + '/' + str(n) + os.path.splitext(img_min_url)[1], 'wb') as f:
                    f.write(response.content)
                    print('保存成功：' + img_path + primary_title + '/' + str(n) + os.path.splitext(img_min_url)[1])
    except Exception as e:
        mylogObj.logger.warning(e)
        mylogObj.logger.warning('保存失败：' + img_path + primary_title + '/' + os.path.splitext(img_min_url)[1])


# 多线程任务
def run_thread(i):
    try:
        print('请求：' + url + url_search.format(i))
        response = request(url + url_search.format(i))
        # 得到索引
        if response:
            page_list = parser_index(response)
            if page_list != []:
                for li in page_list:
                    print('请求：' + url + li[0])
                    response = request(url + li[0])
                    # 解析详情
                    if response:
                        artworkObj = parser_data(response, url + url_search.format(i), url + li[0], li[1])
                        # 保存数据库
                        try:
                            mysqlObj = MysqlClass()
                            mysqlObj.my_insert(artworkObj)
                        except Exception as e:
                            mylogObj.logger.warning(e)
                        finally:
                            mysqlObj.close()
                        # 保存图片
                        try:
                            if artworkObj.img_min_url != '':
                                save_img(artworkObj.img_min_url, artworkObj.imgurl_list, li[0].split('/')[-1])
                        except Exception as e:
                            mylogObj.logger.warning(e)
    except Exception as e:
        mylogObj.logger.warning(e)



# 执行单线程
def run():
    mysqlObj = MysqlClass()
    try:
        for i in range(start_page, end_page, 48):
            time.sleep(1)
            print('请求：' + url + url_search.format(i))
            response = request(url + url_search.format(i))
            # 得到索引
            if response:
                page_list = parser_index(response)
                if page_list != []:
                    for li in page_list:
                        print('请求：' + url + li[0])
                        response = request(url + li[0])
                        # 解析详情
                        if response:
                            artworkObj = parser_data(response, url + url_search.format(i), url + li[0], li[1])
                            # 保存数据库
                            mysqlObj.my_insert(artworkObj)
                            # 保存图片
                            if artworkObj.img_min_url != '':
                                save_img(artworkObj.img_min_url, artworkObj.imgurl_list, li[0].split('/')[-1])
    except Exception as e:
        mylogObj.logger.warning(e)
    finally:
        mysqlObj.close()

#执行多线程
def main():
    with ThreadPoolExecutor(max_workers=200) as executor:
        future_list = []
        for i in range(start_page, end_page, 48):
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
