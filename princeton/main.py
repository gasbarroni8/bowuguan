# -*- coding: utf-8 -*-
import requests
import re
import time
from artworkclass import ArtworkClass
import os
from mysqlclass import MysqlClass
from setting import url, img_path, start_page, end_page, table_name, headers, img_min_url, img_max_url
from mylogclass import MyLogClass
from concurrent.futures import ThreadPoolExecutor, as_completed
import json

mylogObj = MyLogClass()


def index_request(url, i):
    try:
        data1 = {"preference": "results"}
        data2 = {"query": {"bool": {"must": [{"bool": {"must": [{"match": {"nowebuse": "False"}}, {"bool": {
            "must_not": [{"term": {"department.keyword": "(not assigned)"}},
                         {"term": {"department.keyword": "Exhibitions"}},
                         {"term": {"department.keyword": "Departmental Collections"}}]}}, {"bool": {
            "must": [{"term": {"cultureterms.culture.keyword": "Chinese"}}]}}, {"bool": {
            "should": [{"terms": {"classifications.classification.keyword": ["paintings"]}}]}}, {
                                                                    "bool": {"must": {"match_all": {}}, "should": {
                                                                        "term": {
                                                                            "packages.packageid": "167646"}}}}]}}]}},
                 "size": 8, "aggs": {"classifications.classification.keyword": {
                "terms": {"field": "classifications.classification.keyword", "size": 5, "order": {"_count": "desc"}}}},
                 "_source": {"includes": ["*"], "excludes": []}, "from": i, "sort": [{"_score": {"order": "desc"}}]}

        rq_response = requests.post(url, data=json.dumps(data1) + '\n' + json.dumps(data2) + '\n', headers=headers)
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


def request(url):
    try:
        response = requests.post(url, headers=headers)
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


def parser_index(index_response, i):
    try:
        for hit in index_response.json()['responses'][0]['hits']['hits']:
            artObj = ArtworkClass()
            artObj.art_dict['museum_number'] = hit['_id']
            artObj.art_dict['classification'] = hit['_source']['classification']
            artObj.art_dict['creditline'] = hit['_source']['creditline']
            artObj.art_dict['dimensions'] = hit['_source']['dimensions']
            artObj.art_dict['medium'] = hit['_source']['medium']
            artObj.art_dict['primaryMaker'] = hit['_source']['displaymaker']
            artObj.art_dict['title'] = hit['_source']['displaytitle']
            artObj.art_dict['date'] = hit['_source']['displaydate']
            try:
                if hit['_source']['texts'] != []:
                    if 'textentryhtml' in hit['_source']['texts'][0].keys():
                        text = re.sub('<.*?>', '', hit['_source']['texts'][0]['textentryhtml'])
                        artObj.art_dict['description'] = text
            except Exception as e:
                mylogObj.logger.warning(artObj.art_dict['museum_number'])
                mylogObj.logger.warning(e)
            artObj.art_dict['page_url'] = url + ':' + str(i)
            try:
                if hit['_source']['primaryimage'] != []:
                    artObj.art_dict['img_min_url'] = hit['_source']['primaryimage'][0] + img_min_url
                    artObj.art_dict['img_min_path'] = img_path + 'min/' + hit['_id'] + '.jpg'
                if hit['_source']['media'] != []:
                    artObj.art_dict['img_max_url'] = str([media['uri'] + img_max_url for media in hit['_source']['media']])
                    artObj.art_dict['img_max_path'] = str(
                        [img_path + 'max/' + hit['_id'] + '_' + str(i) + '.jpg' for i in
                         range(len(hit['_source']['media']))])
            except Exception as e:
                mylogObj.logger.warning(artObj.art_dict['museum_number'])
                mylogObj.logger.warning(e)
            yield artObj
    except Exception as e:
        mylogObj.logger.warning(index_response.url)
        mylogObj.logger.warning(e)


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
        print('请求：' + url + ':' + str(i))
        main_response = index_request(url, i)
        # 得到索引
        if main_response:
            # 得到数据生成器
            artObj_generator = parser_index(main_response, i)

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
        mylogObj.logger.warning(url + ':' + str(i))
        mylogObj.logger.warning(e)


def main():
    with ThreadPoolExecutor(max_workers=200) as executor:
        future_list = []
        for i in range(start_page, end_page, 8):
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
