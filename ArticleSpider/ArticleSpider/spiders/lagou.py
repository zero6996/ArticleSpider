# -*- coding: utf-8 -*-
#import scrapy
from datetime import datetime
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule
#from ..settings import user_agent_list
from ..items import LagouJobItemLoader,LagouJobItem
from ..common import get_md5

class LagouSpider(CrawlSpider):
    '''拉勾招聘全站爬取'''
    name = 'lagou'
    allowed_domains = ['www.lagou.com']
    start_urls = ['https://www.lagou.com']

    rules = (
        Rule(LinkExtractor(allow=("zhaopin/.*",)),follow=True),
        Rule(LinkExtractor(allow=("gongsi/j\d+.html",)),follow=True),
        Rule(LinkExtractor(allow=r'jobs/\d+.html'), callback='parse_job', follow=True), # 添加子域名
    )
    
#    def parse_start_url(self,response):
#        return []
#    
#    def process_results(self, response, results):
#        return results
    
    def parse_job(self, response):
        #解析拉勾网的职位
        item_loader = LagouJobItemLoader(item = LagouJobItem(),response=response)
        item_loader.add_css("title",".job-name::attr(title)")
        item_loader.add_value('url',response.url)
        item_loader.add_value('url_object_id',get_md5(response.url))
        item_loader.add_css('salary_min','.job_request .salary::text')
        item_loader.add_css('job_city','.job_request span:nth-child(2)::text')
        item_loader.add_css('work_years_min','.job_request span:nth-child(3)::text')
        item_loader.add_css('degree_need','.job_request span:nth-child(4)::text')
        item_loader.add_css('job_type','.job_request span:nth-child(5)::text')
        
        item_loader.add_css('tags','.position-label li::text')
        item_loader.add_css('publish_time','.publish_time::text')
        item_loader.add_css('job_advantage','.job-advantage>p::text')
        item_loader.add_css('job_desc','.job_bt>div')
        item_loader.add_css('job_addr','.work_addr')
        item_loader.add_css('company_name','#job_company>dt>a>img::attr(alt)')
        item_loader.add_css('company_url','#job_company>dt>a::attr(href)')
        item_loader.add_value("crawl_time",datetime.now())
        
        job_item = item_loader.load_item()
        
        return job_item