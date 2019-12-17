import requests
import re
import json
import math
import os
import PIL.Image as Image

img_path = './clevelandart/'

mw = 256  # 图片大小
toImage = Image.new('RGB', (2601, 3400))  # 构造图片的宽和高，如果图片不能填充完全会
# 出现黑色区域
for x in range(5):  # 0-46
    for y in range(6):  # 0-98
        fname = img_path + "test/4-%d-%d.jpg" % (x, y)
        fromImage = Image.open(fname)
        toImage.paste(fromImage, (x * mw, y * mw))
toImage.save(img_path + 'test/max.jpg')


def request(url):
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.120 Safari/537.36'
        }
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            return response
        else:
            return None
    except Exception as e:
        return None


def save_img(img_min_url, imgurl_list, primary_title):
    response = request(img_min_url)
    if response:
        if not os.path.exists(img_path + primary_title):
            os.makedirs(img_path + primary_title)
        with open(img_path + primary_title + '/min' + os.path.splitext(img_min_url)[1], 'wb') as f:
            f.write(response.content)
    for n, url in enumerate(imgurl_list):
        response = request(url)
        if response:
            if not os.path.exists(img_path + primary_title):
                os.makedirs(img_path + primary_title)
            with open(img_path + primary_title + '/' + url.split('/')[-1], 'wb') as f:
                print('保存：' + img_path + primary_title + '/' + url.split('/')[-1])
                f.write(response.content)

# url_list = []
# url = 'https://www.clevelandart.org/art/1955.665'
# response = request(url)
# xy = re.search('jQuery.extend\(Drupal.settings, (.*?)\);', response.text)
# cell = 256
# for i in json.loads(xy[1])['zoomifyImageField']:
#     x = math.ceil(int(json.loads(xy[1])['zoomifyImageField'][i]['width']) / cell)
#     y = math.ceil(int(json.loads(xy[1])['zoomifyImageField'][i]['height']) / cell)
#     for a in range(x):
#         for b in range(y):
#             url_list.append(
#                 json.loads(xy[1])['zoomifyImageField'][i]['tileSourceURL'] + 'TileGroup0/4-' + str(a) + '-' + str(
#                     b) + '.jpg')

# save_img(url_list[0], url_list, 'test')
