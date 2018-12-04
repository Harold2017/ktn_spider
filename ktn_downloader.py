import os
import re
import requests


def get_html(url, encoding='utf-8'):
    if not url.startswith('http://') or not url.startswith('https://'):
        url = 'http://' + url
    try:
        r = requests.get(url, timeout=20)
    except requests.exceptions.ConnectTimeout:
        print('Connection Timeout, Please Check Page URL')
    else:
        if r.status_code == 200:
            r.encoding = encoding
            content = r.text

    return content


def get_img_url(html_content):
    pattern = re.compile('(https?)?//([\w\/\-\.]+)(bmp|jpg|gif|png)')
    list_raw = re.findall(pattern, html_content)

    list_img_url = ['https://' + ''.join(i) for i in list_raw]

    return list_img_url


def save_img(img_url, filename=''):
    try:
        r = requests.get(img_url)
    except requests.exceptions.ConnectTimeout:
        print('Connection Timeout, Please Check Img URL')
    else:
        r.encoding = 'UTF-8'
        if filename == '':
            filename = img_url.split('/').pop()
            print(filename)
        if r.status_code == 200:
            with open(filename, 'wb') as f:
                for chunk in r:
                    f.write(chunk)


def set_storage_path(img_path='~/PycharmProjects/ktn_spider/img'):
    if not os.path.isdir(img_path):
        os.makedirs(img_path)
    os.chdir(img_path)
