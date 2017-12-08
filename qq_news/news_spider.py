__author__ = 'HuaHua'


import requests
from lxml import etree
from pymongo import MongoClient
from selenium import webdriver
from lxml import etree
# client = MongoClient('localhost', 27017)
# db = client.zhongwei
# collection = db.li


def get_urls():
    host = 'http://roll.news.qq.com/'
    driver = webdriver.PhantomJS(executable_path='//Users/lizhongwei/phantomjs-2.1.1-macosx/bin/phantomjs')
    driver.get(host)
    leibie_list = etree.HTML(driver.page_source).xpath('//*[@id="artContainer"]/ul/li/span[2]/text()')
    url_list = etree.HTML(driver.page_source).xpath('//*[@id="artContainer"]/ul/li/a/@href')
    data_list = []
    for i in range(len(leibie_list)):
        data = {
            'leibie': leibie_list[i],
            'url': url_list[i]
        }
        data_list.append(data)
    return data_list


def guize_1(url):
    r = requests.get(url)
    selector = etree.HTML(r.text)
    title1 = selector.xpath('//*[@id="Main-Article-QQ"]/div/div[1]/div[1]/div[1]/h1/text()')[0]
    author1 = selector.xpath('//*[@id="Main-Article-QQ"]/div/div[1]/div[1]/div[1]/div/div[1]/span[2]/a/text()')[0]
    time1 = selector.xpath('//*[@id="Main-Article-QQ"]/div/div[1]/div[1]/div[1]/div/div[1]/span[3]/text()')[0]
    article1 = ""
    for single_article1 in selector.xpath('///*[@id="Cnt-Main-Article-QQ"]/p/text()'):
        article1 += single_article1
    data = {
        'title': title1,
        'time': time1,
        'author': author1,
        'article': article1
    }
    return data


def guize_2(url):
    r = requests.get(url)
    selector = etree.HTML(r.text)
    title2 = selector.xpath('//*[@id="C-Main-Article-QQ"]/div[1]/h1/text()')[0]
    author2 = selector.xpath('//*[@id="C-Main-Article-QQ"]/div[1]/div[1]/div[1]/span[3]/text()')[0]
    time2 = selector.xpath('//*[@id="C-Main-Article-QQ"]/div[1]/div[1]/div[1]/span[5]/text()')[0]
    article2 = ""
    for single_article2 in selector.xpath('//*[@id="Cnt-Main-Article-QQ"]/p[@class="text"]/text()'):
        article2 += single_article2
    data = {
        'title': title2,
        'time': time2,
        'author': author2,
        'article': article2
    }
    return data


url_list = [
    'http://news.qq.com/a/20170529/002034.htm',
    'http://news.qq.com/a/20170528/008649.htm',
    'http://news.qq.com/a/20170529/001449.htm',
    'http://mil.qq.com/a/20170529/005491.htm'
]


if __name__ == '__main__':
    for url in get_urls():
        print (url)
        try:
            # collection.insert(guize_1(url['url']))
            print("1cheng gong")
        except Exception as e:
            print ('guize1 cant catch data :', e, 'try guize2')
            try:
                # collection.insert(guize_2(url['url']))
                print ('2cheng gong')
            except Exception as e:
                print ('finally cant catch data :', e)