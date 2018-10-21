# -*- coding: utf-8 -*-

# Scrapy settings for ArticleSpider project
#
# For simplicity, this file contains only settings considered important or
# commonly used. You can find more settings consulting the documentation:
#
#     https://doc.scrapy.org/en/latest/topics/settings.html
#     https://doc.scrapy.org/en/latest/topics/downloader-middleware.html
#     https://doc.scrapy.org/en/latest/topics/spider-middleware.html

import os


BOT_NAME = 'ArticleSpider'

SPIDER_MODULES = ['ArticleSpider.spiders']
NEWSPIDER_MODULE = 'ArticleSpider.spiders'


# Crawl responsibly by identifying yourself (and your website) on the user-agent
#USER_AGENT = 'ArticleSpider (+http://www.yourdomain.com)'

# Obey robots.txt rules
ROBOTSTXT_OBEY = False

# Configure maximum concurrent requests performed by Scrapy (default: 16)
#CONCURRENT_REQUESTS = 32

# Configure a delay for requests for the same website (default: 0)
# See https://doc.scrapy.org/en/latest/topics/settings.html#download-delay
# See also autothrottle settings and docs
# DOWNLOAD_DELAY = 1
# The download delay setting will honor only one of:
#CONCURRENT_REQUESTS_PER_DOMAIN = 16
#CONCURRENT_REQUESTS_PER_IP = 16

# Disable cookies (enabled by default)
COOKIES_ENABLED = False

# Disable Telnet Console (enabled by default)
#TELNETCONSOLE_ENABLED = False

# Override the default request headers:
#DEFAULT_REQUEST_HEADERS = {
#   'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
#   'Accept-Language': 'en',
#}

# Enable or disable spider middlewares
# See https://doc.scrapy.org/en/latest/topics/spider-middleware.html
#SPIDER_MIDDLEWARES = {
#    'ArticleSpider.middlewares.RandomProxyMiddlware': 543,
##    'ArticleSpider.middlewares.RandomUserAgentMiddlware': 544,
#}

# Enable or disable downloader middlewares
# See https://doc.scrapy.org/en/latest/topics/downloader-middleware.html
#DOWNLOADER_MIDDLEWARES = {
#    'ArticleSpider.middlewares.ArticlespiderDownloaderMiddleware': 543,
#    'ArticleSpider.middlewares.RandomUserAgentMiddlware':543,
#    'ArticleSpider.middlewares.JSPageMiddleware':1,
#    'scrapy.downloadermiddlewares.useragent.UserAgentMiddlewares':None,
#}

# Enable or disable extensions
# See https://doc.scrapy.org/en/latest/topics/extensions.html
#EXTENSIONS = {
#    'scrapy.extensions.telnet.TelnetConsole': None,
#}

# Configure item pipelines
# See https://doc.scrapy.org/en/latest/topics/item-pipeline.html
ITEM_PIPELINES = {
   # 'ArticleSpider.pipelines.JsonWithEncodingPipeline':2, # 使用自定义的导出json,ERROR!
   # 'ArticleSpider.pipelines.JsonExporterPipeline':2, # 使用scrapy定义的json导出
#    'scrapy.pipelines.images.ImagesPipeline':1, # 调用scrapy的图片下载函数
#    'ArticleSpider.pipelines.ArticleImagePipeline':1, # 使用自己重写的图片下载函数
#    'ArticleSpider.pipelines.MysqlPipeline':3, 
      'ArticleSpider.pipelines.ElasticsearchPipeline':1, #存入es中
#     'ArticleSpider.pipelines.MysqlTwistedPipeline':3, # 使用异步的方式将数据存入数据库
}

IMAGES_URLS_FIFLD = 'front_image_url'
project_dir = os.path.abspath(os.path.dirname(__file__))
#print(project_dir)
IMAGES_STORE = os.path.join(project_dir,'images') # 图片存储本地位置
#print(IMAGES_STORE)
import sys
BASE_DIR = os.path.dirname(os.path.abspath(os.path.dirname(__file__)))
#print(BASE_DIR)
sys.path.insert(0,os.path.join(BASE_DIR,'ArticleSpider')) # 插入Python路径

USER_AGENT = "Mozilla/5.0 (X11; Ubuntu; Linu…) Gecko/20100101 Firefox/58.0"

RANDOM_UA_TYPE = 'random'
IMAGES_MIN_HEIGHT = 100
IMAGES_MIN_WIDTH = 100


# Enable and configure the AutoThrottle extension (disabled by default)
# See https://doc.scrapy.org/en/latest/topics/autothrottle.html
# AUTOTHROTTLE_ENABLED = True
# The initial download delay
#AUTOTHROTTLE_START_DELAY = 5
# The maximum download delay to be set in case of high latencies
#AUTOTHROTTLE_MAX_DELAY = 60
# The average number of requests Scrapy should be sending in parallel to
# each remote server
#AUTOTHROTTLE_TARGET_CONCURRENCY = 1.0
# Enable showing throttling stats for every response received:
#AUTOTHROTTLE_DEBUG = False

# Enable and configure HTTP caching (disabled by default)
# See https://doc.scrapy.org/en/latest/topics/downloader-middleware.html#httpcache-middleware-settings
#HTTPCACHE_ENABLED = True
#HTTPCACHE_EXPIRATION_SECS = 0
#HTTPCACHE_DIR = 'httpcache'
#HTTPCACHE_IGNORE_HTTP_CODES = []
#HTTPCACHE_STORAGE = 'scrapy.extensions.httpcache.FilesystemCacheStorage'

MYSQL_HOST = '127.0.0.1'
MYSQL_DBNAME = 'article_spider'
MYSQL_USER = 'root'
MYSQL_PASSWORD = '123456'

#数据库时间格式
SQL_DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"
SQL_DATE_FORMAT = "%Y-%m-%d"



