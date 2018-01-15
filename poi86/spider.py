import requests
from bs4 import BeautifulSoup
import re
import json
from lxml import etree
from pymongo import MongoClient
client = MongoClient('localhost', 27017)
db = client.location


def get_urls():
    urls = ["http://www.poi86.com/poi/district/2898/{}.html".format(str(i)) for i in range(1, 3041)]
    return urls


def get_url(url):
    list = []
    wbdata = requests.get(url).text
    soup = BeautifulSoup(wbdata, 'lxml')
    l = soup.find_all("a", string=re.compile("号楼"))
    for n in l:
        link = n.get("href")
        l = "http://www.poi86.com" + link
        list.append(l)
    for coordinate_url in list:
        get_coordinate(coordinate_url)
    return list


def convert_coordinate_from_str2float(coordinate_str):
    '''把 ‘116.357715,40.013527’转为[116.357715,40.013527] '''
    return [float(x) for x in coordinate_str.split(',')]


def get_coordinate(url):
    r = requests.get(url)
    selector = etree.HTML(r.text)
    wbdata = requests.get(url).text
    soup = BeautifulSoup(wbdata, 'lxml')
    i = soup.find_all("h1")
    news_titles = soup.select("div.panel > div.panel-heading > h1")
    for n in news_titles:
        title = n.get_text()
        link = n.get("href")
        大地坐标 = selector.xpath('/html/body/div[2]/div[1]/div[2]/ul/li[7]/text()')[0]
        火星坐标 = selector.xpath('/html/body/div[2]/div[1]/div[2]/ul/li[8]/text()')[0]
        百度坐标 = selector.xpath('/html/body/div[2]/div[1]/div[2]/ul/li[9]/text()')[0]
    data = {
        '楼': title,
        '大地坐标': 大地坐标,
        '火星坐标': 火星坐标,
        '百度坐标': 百度坐标
    }
    print(data)
    大地 = {
            'location': {
                "type": "Point",
                'coordinates':convert_coordinate_from_str2float(大地坐标)
            },
            'name': title
    }
    火星 = {
            'location': {
                "type": "Point",
                'coordinates':convert_coordinate_from_str2float(火星坐标)
            },
            'name': title
    }
    百度 = {
            'location': {
                "type": "Point",
                'coordinates':convert_coordinate_from_str2float(百度坐标)
            },
            'name': title
    }
    # db.dadi.insert(大地)
    # db.huoxing.insert(火星)
    # db.baidu.insert(百度)


if __name__ == '__main__':
    for url in get_urls():
        get_url(url)



