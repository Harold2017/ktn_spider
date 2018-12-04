import requests
import urllib.request
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor, wait, ALL_COMPLETED
import os
import time


# deal with "urllib.error.URLError: <urlopen error [SSL: CERTIFICATE_VERIFY_FAILED]
# certificate verify failed (_ssl.c:749)>"
# stackoverflow
# cd "/Applications/Python\ 3.6/"  # python path
# sudo "./Install\ Certificates.command"


USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36"
)

PROXIES = {
    "http": "http://127.0.0.1:1087",
    "https": "http://127.0.0.1:1087"
}


def get_page(url):
    """
    get page content by bs4 from url string and return this content
    :param url: str
    :return: bs4 object
    """
    r = requests.get(url, proxies=PROXIES, headers={'User-Agent': USER_AGENT})
    bs = BeautifulSoup(r.text, 'html.parser')
    return bs


def download_img(bs, save_path):
    """
    download images and save them in right place
    :param bs: bs4 object
    :param save_path: path for saving those downloaded images
    :return: none
    """
    # this site has two kinds of formats for displaying images
    # one is presented in div and the other one is in table, they both have a class named t_f
    if not bs.find('div', class_='t_f'):
        content = bs.find('td', class_='t_f')
        images = content.find_all('img')
        img_name_list = [image['file'].split('/').pop().split('.')[0] for image in images]
        img_link_list = [image['file'] for image in images]
    else:
        content = bs.find('div', class_='t_f')
        images = content.find_all('img')
        img_name_list = [image['src'].split('/').pop().split('.')[0] for image in images]
        img_link_list = [image['src'] for image in images]

    for img_name, img_link in zip(img_name_list, img_link_list):
        urllib.request.urlretrieve(img_link, save_path + img_name + '.jpg')


def set_storage_path(img_path='/Users/dupeixin/PycharmProjects/ktn_spider/img/'):
    """
    set storage path
    :param img_path: path to save images
    :return: path str
    """
    if not os.path.isdir(img_path):
        os.makedirs(img_path)
    # os.chdir(img_path)
    return img_path


def find_prev_next_page_url(bs):
    """
    find previous and next pages on current page
    :param bs: bs object
    :return: a tuple of previous page url and next page url
    """
    urls = bs.find('div', class_='sideToolBox').find('div', class_='prevNext').find_all('a', class_='iconTip')
    pre_url = urls[0]['href']
    next_url = urls[1]['href']
    return pre_url, next_url


if __name__ == '__main__':
    start_urls = ['https://ck101.com/thread-4736501-1-1.html']
    # decide how many pages to collect
    for i in range(1, 10):
        start_urls.append(find_prev_next_page_url(get_page(start_urls[-1]))[0])

    # save urls into url_lists file
    with open('url_lists.txt', 'w+') as f:
        urls = [url + '\n' for url in start_urls]
        f.writelines(urls)

    path = set_storage_path()

    '''
    # executed without multiple threads
    print('*' * 20)
    t1 = time.time()

    for url in start_urls:
        download_img(get_page(url), path)

    t2 = time.time()
    print('Time consumed: %s' % (t2 - t1))
    print('*' * 20)
    # 283.62s
    '''

    # executed with thread pool
    print('*' * 20)
    t1 = time.time()

    executor = ThreadPoolExecutor(max_workers=3)
    future_tasks = [executor.submit(download_img, get_page(url), path) for url in start_urls]
    wait(future_tasks, return_when=ALL_COMPLETED)

    t2 = time.time()
    print('Time consumed: %s' % (t2 - t1))
    print('*' * 20)
    # 115.39s
