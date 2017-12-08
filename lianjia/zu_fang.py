__author__ = 'HuaHua'

import urllib.request
import urllib.parse
import re
import requests
from bs4 import BeautifulSoup
from multiprocessing import Pool
import random
from lxml import etree
from pymongo import MongoClient
client = MongoClient('localhost', 27017)
db = client.lianjia


def change_Agent():
    agents = [
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.94 Safari/537.36"]
    agent = random.choice(agents)
    return agent


def get_house1_location(link):
    # 抓取并存储每个小区的地理坐标及位置，
    agent = change_Agent()
    headers = {"User-Agent", agent}
    opener = urllib.request.build_opener()
    opener.addheaders = [headers]
    web_data = opener.open(link).read()
    selector = etree.HTML(web_data)
    xiao_qu = selector.xpath("/html/body/div[4]/div[2]/div[2]/div[2]/p[6]/a[1]/text()").pop()
    wei_zhi1 = selector.xpath('/html/body/div[4]/div[2]/div[2]/div[2]/p[7]/a[1]/text()').pop()
    wei_zhi2 = selector.xpath('/html/body/div[4]/div[2]/div[2]/div[2]/p[7]/a[2]/text()').pop()
    info_for_need = selector.xpath('/html/body/script[12]/text()').pop()
    regex = '''resblockPosition(.+)'''
    location_items = re.search(regex, info_for_need)
    location_content = location_items.group()[:-1]  # 经纬度
    longitude_latitude = eval(location_content.split(':')[1])
    location_infos = {
        "location": longitude_latitude,
        "xiao_qu": xiao_qu,
        "wei_zhi": wei_zhi1+"区"+wei_zhi2
    }
    return location_infos


def get_all_house_urls(url):
    # 抓取每个租房页面中所有房源的链接house_url,一个页面三十个房源链接
    title_links_list = []
    res = requests.get(url)
    soup = BeautifulSoup(res.text, 'lxml')
    titles = soup.select("ul.house-lst > li > div.info-panel > h2 > a")
    for title in titles:
        title_link =title.get("href")
        title_links_list.append(title_link)
    return title_links_list


def get_urls_for_page_index(page_begin, page_end):
    """构造 链家索引页面 p001 - p100"""
    urls = ['https://bj.lianjia.com/zufang/pg{}/'.format(str(i)) for i in range(page_begin, page_end)]
    return urls


def mul_get_verify_location(title_links_list):
    """
    多进程爬房源信息
    """
    pool = Pool(processes=3)
    fl_proxies = pool.map(get_house1_location, title_links_list)
    pool.close()
    pool.join()
    return fl_proxies


def save_location(fl_proxie):
    db.zufang_location.insert(fl_proxie)


def scrach_lianjia_for_location(page_begin, page_end):
    urls = get_urls_for_page_index(page_begin, page_end)
    for url in urls:
        title_links_list = get_all_house_urls(url)
        fl_proxies = mul_get_verify_location(title_links_list)
        for fl_proxie in fl_proxies:
            save_location(fl_proxie)


def main():
    page_begin, page_end = 1, 500
    scrach_lianjia_for_location(page_begin, page_end)


if __name__ == '__main__':
    main()