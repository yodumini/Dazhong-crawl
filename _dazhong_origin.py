#!/usr/bin/env python
# -*- coding : utf-8 -*-

from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.expected_conditions import element_to_be_clickable
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from lxml import html
from lxml import etree
import lxml.etree
import re
#import xlsxwriter
import requests
import csv
from crawl import SpiderBase
import time
import os
from user_agent import *
import random


"""
__version__ = 1.0
__application__ = '爬取有家酸菜鱼上海地区在大众点评上的数据'
__future__ = '增加多城市爬取，定时爬取'
__author__ = 'DevinChang'
__data__ = '2017/10/11'
"""

"""
__version__ = 1.1
__application__ = '爬取有家酸菜鱼在大众点评上的数据'
__modify__ = '解决大部分ip被限制问题, 增加多城市爬取功能'
__future__ = '定时爬取'
__author__ = 'DevinChang'
__data__ = '2017/11/15'
"""

"""
__version__ = 2.0
__application__ = '爬取德克士在大众点评上的数据'
__bug__ = '采用selenium爬取速度会慢很多，且吃资源严重。反爬虫问题还好，爬取多个城市时同样会被限制ip。
__future__ = '考虑多线程来工作，或者用分布式爬虫'
__author__ = 'DevinChang'
__data__ = '2018/1/21'
"""


class DaZhong(SpiderBase):
    def __init__(self, url, keywords, city):
        """
        @url: 大众点评的主页面,即www.dianping.com
        @keywords: 需要搜索的关键字
        @city: 需要爬取的城市拼音,如上海为shanghai
        """
        SpiderBase.__init__(self, url)
        # self.browser = webdriver.PhantomJS(service_args=['--load-images=false', '--disk-cache=true'])
        self.browser = webdriver.Chrome()
        self.wait = WebDriverWait(self.browser, 10)
        self.shopurl = []
        self.keywords = keywords
        self.shopdict = []
        self.commentsdict = []
        self.city = city

    def __del__(self):
        self.browser.quit()

    def __search(self, url, nextpage):
        """
        搜素门店信息
        """
        try:
            if nextpage:
                nextbutton = self.wait.until(EC.element_to_be_clickable(
                    (By.XPATH, '/html/body/div[2]/div[3]/div[1]/div[@class="page"]/a[@title="下一页"]'))) 
                nextbutton.click()
                return self.__getstoreinfo()
            else:
                self.browser.get(url)
                input = self.wait.until(
                    EC.presence_of_element_located(
                        (By.CSS_SELECTOR, '#J-search-input'))
                )
                submit = self.wait.until(EC.element_to_be_clickable(
                    (By.XPATH, '//*[@id="J-all-btn"]')))
                input.send_keys(self.keywords)
                submit.click()
                
                self.browser.close()
                self.browser.switch_to_window(self.browser.window_handles[0])
                return self.__getstoreinfo()
        except TimeoutException:
            print('连接超时，正在重新搜索....')

        
    
    
        
    def __getstoreinfo(self):
        """
        获取门店信息
        """
        tree = etree.HTML(self.browser.page_source)
        items = tree.xpath('/html/body/div[2]/div[3]/div/div/div[2]/ul/li')
        product = []
        foodlinks = []
        shopinfodict = []
        source = '大众点评'
        brand = self.keywords
        i = 1
        for item in items:
            link = tree.xpath(
                '//*[@id="shop-all-list"]/ul/li[{}]/div[1]/a/@href'.format(i))
            self.shopurl.append(link[0])
            shopid = re.findall(r'[1-9]\d*', link[0])
            shopname = tree.xpath(
                '//*[@id="shop-all-list"]/ul/li[{}]/div[2]/div[1]/a/h4/text()'.format(i))
            address = tree.xpath(
                '//*[@id="shop-all-list"]/ul/li[{}]/div[2]/div[3]/span/text()'.format(i))
            variety = tree.xpath(
                '//*[@id="shop-all-list"]/ul/li[{}]/div[2]/div[3]/a[1]/span/text()'.format(i))
            city = tree.xpath('//*[@id="logo-input"]/div[1]/a[2]/span/text()')
            avgprice = tree.xpath(
                '//*[@id="shop-all-list"]/ul/li[{}]/div[2]/div[2]/a[2]/b/text()'.format(i))
            score = tree.xpath(
                '//*[@id="shop-all-list"]/ul/li[{}]/div[2]/div[2]/span/@title'.format(i))
            counts = tree.xpath(
                '//*[@id="shop-all-list"]/ul/li[{}]/div[2]/div[2]/a[1]/b/text()'.format(i))
            # set_trace()file:/C:/Users/JDJQ001/PycharmProjects/JD_Crawler/
            if not avgprice:
                avgprice.append('None')
            elif len(avgprice) > 1:
                del avgprice[0]
            if not counts:
                counts.append('0')
            itemdict = {
                "source" : source,
                "brand" : brand,
                "shop_id" : shopid[0],
                "shop_name" : shopname[0],
                "region" : city[0],
                "addr" : address[0],
                "category" : variety[0],
                "counts" : counts[0],
                "shop_score" : score[0],
                "deliver_time" : 'NA',
                "lowest_price" : 'NA',
                "deliver_fee" : 'NA',
                "price" : avgprice[0]
            }
            product.append([source, brand, shopid[0], shopname[0], city[0],
                            address[0], variety[0], counts[0], score[0], avgprice[0]])
            self.shopdict.append(itemdict)
            i += 1
        page = tree.xpath('/html/body/div[2]/div[3]/div[1]/div[@class="page"]/a[@title="下一页"]')
        if page:
            return self.__search(url = None, nextpage=True)

    #shopcomments = [['分店编号', '使用者名称', '使用者等级', '日期',
    #                 '类型', '评论', '口味评分', '服务评分', '环境评分', '使用者评分']]




    def __get_user_agent(self):
        """
        随机获取请求头
        """
        agent = random.choice(agents)
        return {'User-Agent' : agent}

    def __get_random_proxy(self):  
        """随机从文件中读取proxy"""  
        while 1:  
            with open('C:\proxy.txt', 'r') as f:
                proxies = f.readlines()  
            if proxies:  
                break  
            else:  
                time.sleep(1)  
        proxy = random.choice(proxies).strip()  
        return proxy  
    
    def __get_proxy(self):
        """
        获取代理
        """
        proxy = self.__get_random_proxy()
        return {'http': 'http://' + str(proxy)}

    
    def __getcomments(self):
        """
        用request请求的方法获取页面源码
        @modify:此方法速度上较selenium有优势，但ip会比较容易受限制
        """
        i = 0
        for shopurl in self.shopurl:
            if int(self.shopdict[i]['counts']) > 10:
                url = shopurl + '/review_all' 
                #response = requests.get(url, headers = self.__get_user_agent())
                try:
                    response = requests.get(url, headers = self.__get_user_agent())
                except Exception:
                    sleep(1)
                    response = requests.get(url, headers = self.__get_user_agent())
                print(response.status_code)
                print(response.text)
                tree = etree.HTML(response.text)
                nextpage = tree.xpath('//*[@id="review-list"]/div[2]/div[1]/div[3]/div[4]/div[1]/a[@title="下一页"]')
                j = 2
                while(nextpage):
                    self.__reviewmore(response.text, self.shopdict[i]['shop_id'])
                    url = url + '/p{}'.format(j)
                    j += 1
                    try:
                        response = requests.get(url, headers = self.__get_user_agent())
                    except Exception:
                        time.sleep(1)
                        response = requests.get(url, headers = self.__get_user_agent())
    
    def __seleniumcomments(self):
        """
        selenium爬取评论
        """
        i = 0
        for shopurl in self.shopurl:
            if int(self.shopdict[i]['counts']) > 10:
                url = shopurl + '/review_all' 
                self.browser.get(url)
                tree = etree.HTML(self.browser.page_source)
                #nextpage = tree.xpath('//*[@id="review-list"]/div[2]/div[1]/div[3]/div[4]/div[1]/a[@title="下一页"]')
                #j = 2
                self.__reviewmore(self.browser.page_source, self.shopdict[i]['shop_id'])
                #url = url + '/p{}'.format(j)
                #j += 1
                #nextpage = True
                while(True):
                    try:
                        nextbutton = self.wait.until(EC.element_to_be_clickable(
                            (By.XPATH, '//*[@id="review-list"]/div[2]/div[1]/div[3]/div[4]/div[1]/a[@title="下一页"]')))
                        sleeptime = random.randint(1, 2)
                        time.sleep(sleeptime)
                        nextbutton.click()
                        self.__reviewmore(self.browser.page_source, self.shopdict[i]['shop_id'])
                    except Exception:
                        break
                    #self.browser.get(url)


    def __reviewmore(self, pagesource, shopid):
        """
        获取评论(评论数多于10条)
        """
        tree = etree.HTML(pagesource)
        ncomments = tree.xpath('//*[@id="review-list"]/div[2]/div[1]/div[3]/div[3]/ul/li')
        variety = tree.xpath('//*[@id="review-list"]/div[1]/div/a[2]/text()')
        i = 1
        for comment in ncomments:
            username = tree.xpath('//*[@id="review-list"]/div[2]/div[1]/div[3]/div[3]/ul/li[{}]/div/div[1]/a/text()'.format(i))
            rank = tree.xpath('//*[@id="review-list"]/div[2]/div[1]/div[3]/div[3]/ul/li[{}]/div/div[1]/span[1]/@class'.format(i))
            if not rank:
                rank.append('user-rank-rst urr-rank0 rank') 
            ranknumber = re.findall(r'[0-9]\d*', rank[0])
            if int(ranknumber[0]) <= 40:
                userrank = int(ranknumber[0]) / 10
            elif int(ranknumber[0]) == 45:
                userrank = 5
            else:
                userrank = int(ranknumber[0]) / 10 + 1
            hide = tree.xpath('//*[@id="review-list"]/div[2]/div[1]/div[3]/div[3]/ul/li[{}]/div/div[3]/div/a'.format(i))
            if hide:
                reviewtmp = tree.xpath('//*[@id="review-list"]/div[2]/div[1]/div[3]/div[3]/ul/li[{}]/div/div[4]/text()'.format(i))
            else:
                reviewtmp = tree.xpath('//*[@id="review-list"]/div[2]/div[1]/div[3]/div[3]/ul/li[{}]/div/div[3]/text()'.format(i))
            review = re.findall(r'[^\x00-\xff]', reviewtmp[0])
            reviewbody = "".join(review)
            date = tree.xpath('//*[@id="review-list"]/div[2]/div[1]/div[3]/div[3]/ul/li[{}]/div/div[@class="misc-info clearfix"]/span[1]/text()'.format(i))
            taste = tree.xpath(
                '//*[@id="review-list"]/div[2]/div[1]/div[3]/div[3]/ul/li[{}]/div/div[2]/span[2]/span[1]/text()'.format(i))
            service = tree.xpath(
                '//*[@id="review-list"]/div[2]/div[1]/div[3]/div[3]/ul/li[{}]/div/div[2]/span[2]/span[2]/text()'.format(
                    i))
            envir = tree.xpath(
                '//*[@id="review-list"]/div[2]/div[1]/div[3]/div[3]/ul/li[{}]/div/div[2]/span[2]/span[3]/text()'.format(
                    i))
            scoretmp = tree.xpath(
                '//*[@id="review-list"]/div[2]/div[1]/div[3]/div[3]/ul/li[{}]/div/div[2]/span[1]/@class'.format(
                    i))
            score = re.findall(r'[1-9]\d*', scoretmp[0])
            score = int(score[0]) / 10
            commentdict = {
               "shop_id" : shopid,
               "user_name" : username[0],
               "user_rank" : userrank,
               "date" : date[0],
               "type" : variety[0],
               "comment" : reviewbody, 
               "taste" : taste[0],
               "service" : service[0],
               "envir" : envir[0],
               "user_score" : score
            }
            self.commentsdict.append(commentdict)
            i += 1
        self.__savemongodb("DicosComments", self.commentsdict)
        self.commentsdict[:] = []
        

    def __storedata(self, filename, data):
        """
        存入数据到excel表中
        """
        with open(filename, 'a+', encoding='utf-8-sig', newline='') as f:
            f_csv = csv.writer(f, dialect='excel')
            for line in data:
                f_csv.writerow(line)

    def __savemongodb(self, db, datas):
        """
        存入数据至mongodb数据库
        """
        if not datas:
            return
        self.suancaiyudb.get_collection(db).insert_many(datas)


    def run(self):
        """
        主函数
        """
        for city in self.city:
            url = self.url + city
            self.__search(url, nextpage=False)
            self.__seleniumcomments()
            self.__savemongodb("DicosShopInfo", self.shopdict)
            self.shopdict[:] = []
        #将数据保存至excel表中
        #codepath = os.path.dirname(__file__)
        #datapath = codepath + '\data'
        #self.__storedata(
        #    datapath + '\comment.csv', self.shopcomments)

data = DaZhong('www.dianping.com','德克士','shanghai')
data.