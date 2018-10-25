# -*- coding: utf-8 -*-
import scrapy
#import re
#import datetime
from scrapy.http import Request
from scrapy.loader import ItemLoader
from urllib import parse
from ArticleSpider.items import JobboleArticleItem,ArticleItemLoader
from ArticleSpider.common import get_md5

class JobboleSpider(scrapy.Spider):
    name = 'jobbole'
    allowed_domains = ['blog.jobbole.com']
    start_urls = ['http://blog.jobbole.com/all-posts/']

    def parse(self, response):
        '''
        1.获取文章列表页中的文章url并交给scrapy下载后交给解析函数进行具体的数据解析
        2.获取下一页的url交给scrapy进行下载,下载完后交给parse
        '''
        
        #解析列表页中的所有文章url并交给scrapy下载后进行解析
        post_nodes = response.css("#archive .floated-thumb .post-thumb a") # 获取a标签
        for post_node in post_nodes:
            image_url = post_node.css("img::attr(src)").extract_first("") # 获取a标签下的img属性的src值
            post_url = post_node.css("::attr(href)").extract_first("") # 获取a标签的href属性值
            yield Request(url=parse.urljoin(response.url,post_url), meta = {"front_image_url":image_url},callback=self.parse_detail)
        
        #提取下一页并交给scrapy下载
        next_url = response.css(".next.page-numbers::attr(href)").extract_first("")
        if next_url:
            url = parse.urljoin(response.url, next_url)
            yield Request(url=url,callback=self.parse)

        

    def parse_detail(self,response):
        article_item = JobboleArticleItem()
        
        #通过css选择器提取数据
        front_image_url = response.meta.get('front_image_url',"") # 获取文章封面图
        #通过ItemLoader加载Item
        item_loader = ArticleItemLoader(item=JobboleArticleItem(),response=response)
        item_loader.add_css("title",'.entry-header>h1::text')
        item_loader.add_value("url",response.url)
        item_loader.add_value('url_object_id',get_md5(response.url))
        item_loader.add_css('create_date','p.entry-meta-hide-on-mobile::text')
        item_loader.add_value('front_image_url',[front_image_url])

        if response.css('.vote-post-up>h10::text'):
            item_loader.add_css("praise_number",'.vote-post-up>h10::text')
        else:
            item_loader.add_value("praise_number","0")

        item_loader.add_css("comment_nums",'a[href="#article-comment"]>span::text')
        item_loader.add_css('fav_nums','.bookmark-btn::text')
        item_loader.add_css('tags','p.entry-meta-hide-on-mobile>a::text')
        item_loader.add_css('content','div.entry')
        
        article_item = item_loader.load_item()
        
        yield article_item
        
'''       
Traceback (most recent call last):
  File "/usr/local/lib/python3.5/dist-packages/twisted/internet/defer.py", line 654, in _runCallbacks
    current.result = callback(current.result, *args, **kw)
  File "/home/tarena/zero/project/爬虫项目/ArticleSpider/ArticleSpider/pipelines.py", line 165, in process_item
    item.save_to_es()
  File "/home/tarena/zero/project/爬虫项目/ArticleSpider/ArticleSpider/items.py", line 120, in save_to_es
    if self['praise_number']:
  File "/usr/local/lib/python3.5/dist-packages/scrapy/item.py", line 59, in __getitem__
    return self._values[key]
KeyError: 'praise_number'
'''
