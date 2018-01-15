import requests
from bs4 import BeautifulSoup
import re
import json
from itertools import groupby
from lxml import etree
from pymongo import MongoClient
client = MongoClient('localhost', 27017)
db = client.location
i = 0
li = []


def get_urls():
    urls = ["http://www.poi86.com/poi/district/2304/{}.html".format(str(i)) for i in range(1, 495
                                                                                           )]
    return urls


def get_links(url):
    ''' 
    :param url: 
    :return: links
    保存含有“号楼” 从列表中过滤出来
    '''
    proxies = {
        "http": "http://101.68.73.54:53281"
    }
    links = []
    wbdata = requests.get(url,proxies).text
    soup = BeautifulSoup(wbdata, 'lxml')
    l = soup.find_all("a", string=re.compile("号楼"))
    for n in l:
        link = n.get("href")
        l = "http://www.poi86.com" + link
        links.append(l)

    return links


def get_coordinate_from_links(links):
    results = []
    for coordinate_url in links:
        result1 = get_coordinate(coordinate_url)
        if result1 is None:
            continue
        else:
            results.append(result1)

    return results


def fix_甲XX号楼(区,楼号):
    '''如果是"安慧北里逸园甲16号楼" '''
    tail_区 = 区[-1]
    if tail_区 in ['甲', '乙', '丙']:
        区 = 区[:-1]
        楼号 = tail_区 + 楼号
    return 区, 楼号


def get_coordinate(url):
    '''  爬取每个coordinate_url 中的坐标'''
    r = requests.get(url)
    selector = etree.HTML(r.text)
    wbdata = requests.get(url).text
    soup = BeautifulSoup(wbdata, 'lxml')
    i = soup.find_all("h1")
    news_titles = soup.select("div.panel > div.panel-heading > h1")
    assert 1 == len(news_titles), '{0}不等于1'.format(news_titles)
    title = news_titles[0].text
    print(title)
    # / html / body / div[2] / div[1] / div[2] / ul / li[3] / text()
    location = selector.xpath('/html/body/div[2]/div[1]/div[2]/ul/li[2]/a/text()')[0]
    pattern = re.compile(r'[\u4e00-\u9fa5]+')
    区 = pattern.search(title).group()

    pattern = re.compile(r'[A-Z\d]+[\D]+')
    # 如果是 紫玉山庄H号楼 http://www.poi86.com/poi/11299321.html
    try:
        楼号 = pattern.search(title).group()
    except AttributeError as e:
        return None

    #如果是"安慧北里逸园甲16号楼
    区, 楼号 = fix_甲XX号楼(区, 楼号)

    return (区, 楼号)


if __name__ == '__main__':
    urls = get_urls()
    results = []
    for url in urls:
    #url = 'http://www.poi86.com/poi/district/2898/152.html'
    # url = 'http://www.poi86.com/poi/district/2898/1718.html'
        links = get_links(url)
        print(url)
        results_page1 = get_coordinate_from_links(links)
        results.extend(results_page1)
    print(results)


    # str1 = '紫玉山庄H号楼'
    # pattern = re.compile(r'[\u4e00-\u9fa5]+')
    # 区 = pattern.search(str1).group()
    # print(区)

    # 区, 楼号 = '安慧北里逸园甲', '16号楼'
    # print(区, 楼号)
    # 区, 楼号 = fix_甲XX号楼(区, 楼号)
    # print(区, 楼号)
