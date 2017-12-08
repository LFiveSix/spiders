__author__ = 'HuaHua'

import requests
from bs4 import BeautifulSoup
from lxml import etree
import re
from pymongo import MongoClient
client = MongoClient('localhost', 27017)
db = client.lianjia


def scrach_lianjia_for_location(page_begin, page_end):
    """从链家爬取每个小区的经纬度，保存到mongodb"""
    # 从二手房页面，得到 若干 page 形如 p1-p100
    urls_index_page = get_urls_for_page_index(page_begin, page_end)

    for url_index_page in urls_index_page:
        # 对每个index_page ，爬出页面中每个房源link_house  典型数量 每页30个
        links_house_index_page1 = get_link_house_from_page1(url_index_page)
        for link_house1 in links_house_index_page1:
            # 访问每个房源link_house1，爬出该房源的{小区名,经纬读坐标}
            name_location = get_location_house1(link_house1)
            # 保存
            save_location_to_mongodb(name_location)


def get_urls_for_page_index(page_begin, page_end):
    """构造 链家索引页面 p100 - p200"""
    urls = ['https://bj.lianjia.com/ershoufang/pg{}/'.format(str(i)) for i in range(page_begin, page_end)]
    return urls


def get_link_from_title(title_link):
    """从标题里得到1个房子详情页的link"""
    try:
        link = title_link.get("href")
    except:
        link = ''
    return link


def get_link_house_from_page1(url_page1):
    """链家每页30个link"""
    links_list = []
    wbdata = requests.get(url_page1).text
    soup = BeautifulSoup(wbdata, 'lxml')
    # 30个link
    news_titles = soup.select("div.content > div.leftContent > ul.sellListContent > li.clear > div.info > div.title > a")
    for title_link in news_titles:
        #  从标题里得到1个房子详情页的link
        link = get_link_from_title(title_link)
        links_list.append(link)
    return links_list


def get_location_house1(link):
    """爬取1个房源的小区和经纬度 """
    r = requests.get(link)
    selector = etree.HTML(r.text)
    script_str = selector.xpath('/html/body/script[20]/text()').pop()
    regex = '''resblockPosition(.+)'''
    name = '''resblockName(.+)'''
    location_items = re.search(regex, script_str)
    name_item = re.search(name, script_str)
    content = location_items.group()[:-1]  # 经纬度
    n_ame = name_item.group()[:-1]
    # 注意单引号问题 切出来字符形如 "'116.469221,40.000762'"
    longitude_latitude = eval(content.split(':')[1])
    # 注意单引号问题 切出来字符形如 "resblockName:'天通苑北三区'"
    resblockName = eval(n_ame.split(':')[1])
    data = {
        'name': resblockName,
        'location': longitude_latitude
    }
    return data


def save_location_to_mongodb(name_location):
    """保存  如果数据中有 就不保存"""
    resblockName = name_location['name']
    #  按小区名查询
    res_list = list(db.location.find({"name": resblockName}))
    if not res_list:
        pass
        # db.ershoufang_location.insert(name_location)


def main():
    page_begin, page_end = 1, 500
    scrach_lianjia_for_location(page_begin, page_end)


if __name__ == '__main__':
    main()















