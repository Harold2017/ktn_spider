import os
import asyncio
import logging
from aiohttp import ClientSession
import aiofiles

from multithread_downloader import get_page, find_prev_next_page_url, set_storage_path, USER_AGENT, PROXIES


DELAY_TIME = 0.3  # request delay in secs
MAX_PARALLEL = 10  # max processes in parallel
MAX_PAGES = 5  # max pages
LOG_LEVEL = logging.INFO


def get_logger():
    formatter = logging.Formatter('%(asctime)s >>> %(message)s')
    logger = logging.getLogger(__name__)
    logger.setLevel(LOG_LEVEL)
    handler = logging.StreamHandler()
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    return logger


LOGGER = get_logger()


def get_final_line():
    i = -1
    with open('url_lists.txt', 'r') as f:
        # for few lines
        return f.readlines()[-1]
        '''
        while True:
            i -= 1
            f.seek(i, 2)  # 0: from beginning, 1: from current, 2: from end
            if f.read(1) == '\n':
                break
        return f.readline().strip()
        '''


def save_urls(urls):
    with open('url_lists.txt', 'a+') as f:
        urls = [url + '\n' for url in urls]
        f.writelines(urls)


def get_urls():
    start_url = get_final_line()
    urls = []
    # decide how many pages to collect
    for i in range(0, MAX_PAGES):
        urls.append(find_prev_next_page_url(get_page(start_url))[0])

    # save urls into url_lists file
    save_urls(urls)
    return urls


def get_img_urls():
    page_url = url_generator()
    bs = get_page(page_url)
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

    for img in zip(img_name_list, img_link_list):
        yield img


def url_generator():
    with open('url_lists.txt', 'r') as f:
        for url in f.readlines():
            yield url.strip()


async def downloader(sema, filename, url, session):
    try:
        filepath = os.path.join(set_storage_path(), filename)
        if os.path.exists(filepath):
            LOGGER.info("Ignored same image: {}".format(filename))
            return
        await asyncio.sleep(DELAY_TIME)
        async with sema:
            async with session.get(url, proxies=PROXIES, headers={'User-Agent': USER_AGENT}) as response:
                img_data = await response.read()
            async with aiofiles.open(filepath, mode='ab') as f:
                await f.write(img_data)
                LOGGER.info('Save image: {}'.format(filename))
    except Exception:
        LOGGER.error('Failed downloading URL: {}'.format(url))


async def run():
    sema = asyncio.Semaphore(MAX_PARALLEL)
    async with ClientSession() as session:
        tasks = [asyncio.ensure_future(downloader(sema, filename, url, session)) for filename, url in get_img_urls()]
        await asyncio.wait(tasks)


if __name__ == '__main__':
    get_urls()
    loop = asyncio.get_event_loop()
    loop.run_until_complete(
        asyncio.wait(run())
    )
