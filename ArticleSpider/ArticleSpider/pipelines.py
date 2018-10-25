# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html

import codecs
import json
import MySQLdb
import MySQLdb.cursors

#    scrapy.pipelines.images.       ImagesPipeline':1,
from scrapy.pipelines.images import ImagesPipeline 
from scrapy.exporters import JsonItemExporter
from ArticleSpider.MySQLHelp import DBHelper
from twisted .enterprise import adbapi  
from w3lib.html import remove_tags
from models.es_types import ArticleType


class ArticlespiderPipeline(object):
    def process_item(self, item, spider):
        return item


class JsonWithEncodingPipeline(object):
    #自定义json文件的导出
    def __init__(self):
        self.file = codecs.open('article.json','w',encoding='utf-8') # 使用codecs打开文件
    
    def process_item(self,item,spider): # 处理item
        lines = json.dumps(dict(item),ensure_ascii=False) + '\n' # 使用json编码,设置编码格式
        self.file.write(lines) # 写入文件
        return item
    
    def spider_closed(self,spider): # 使用信号量关闭文件
        self.file.close()


class JsonExporterPipeline(object):
    #调用scrapy提供的json export导出json文件
    def __init__(self):
        self.file = open('articleexport.json','wb') # 打开文件
        self.exporter = JsonItemExporter(self.file,encoding='utf-8',ensure_ascii=False) # 实例化JsonItemExporter
        self.exporter.start_exporting()
    
    def close_spider(self,spider): # 信号关闭文件
        self.exporter.finish_exporting() # 停止导出
        self.file.close() # 关闭文件
    
    def process_item(self,item,spider): # 处理item
        self.exporter.export_item(item)
        return item
    
    
class JobboleDataToMysql(object):
    
    def process_item(self,item,spider):
        count = 0
        dbhelper = DBHelper()
        title = item['title']
        url = item['url']
        create_date = item['create_date']
        fav_nums = item['fav_nums']
        url_object_id = item['url_object_id']
        front_image_url = item['front_image_url']
        front_image_path = item['front_image_path']
        praise_number = item['praise_number']
        comment_nums = item['comment_nums']
        content = item['content']
        tags = item['tags']
        sql = 'INSERT INTO jobbole_article(title,url,create_date,fav_nums,url_object_id,front_image_url,praise_number,comment_nums,content,tags) VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)'
        params = (title,url,create_date,fav_nums,url_object_id,front_image_url,praise_number,comment_nums,content,tags)
        result = dbhelper.execute(sql,params)
        if result == True:
            count += 1
            print('Insert done!,',count)
        else:
            print('Insert Failed!')

        return item

class LagouDataToMysql(object):
    def process_item(self,item,spider):
        dbhelper = DBHelper()
        insert_sql,params = item.get_insert_sql()
        print(insert_sql,params)
        result = dbhelper.execute(insert_sql,params)
        if result == True:
            print('Insert done!')
        else:
            print('Insert Failed!')

class MysqlPipeline(object):
#     采用同步机制写入mysql
    def __init__(self):
        self.conn = MySQLdb.connect('127.0.0.1','root','123456','article_spider',charset='utf8',use_unicode=True)
        self.cursor = self.conn.cursor()
    
    def process_item(self,item,spider):
        insert_sql = '''
            insert into jobbole_article(title,url,create_date,fav_nums)
            VALUES(%s,%s,%s,%s)
        '''
        self.cursor.execute(insert_sql,(item['title'],item['url'],item['create_date'],item['fav_nums']))
        self.conn.commit()



# 异步写入数据库
class MysqlTwistedPipeline(object):
    def __init__(self,dbpool):
        self.dbpool = dbpool


    @classmethod
    def from_settings(cls,settings): # 导入settings
        dbparms = dict(
            host = settings['MYSQL_HOST'],# 获取settings里面的值
            db = settings['MYSQL_DBNAME'],
            user = settings['MYSQL_USER'],
            passwd = settings['MYSQL_PASSWORD'],
            charset = 'utf8',
            cursorclass = MySQLdb.cursors.DictCursor,
            use_unicode = True,
        )
        dbpool = adbapi.ConnectionPool('MySQLdb',**dbparms) # **IMAGES_URLS_FIFLD = 'front_imdpparms-->拆包操作

        return cls(dbpool)

    def process_item(self,item,spider):
        #使用twisted将mysql插入变成异步执行
        query = self.dbpool.runInteraction(self.do_insert,item)
        query.addErrback(self.handle_error,item,spider) # 处理异常

    def handle_error(self,failure,item,spider):
        #处理异步插入的异常
        print(failure)

    def do_insert(self,cursor,item):
        #执行具体的插入
        # 根据不同的item 构建不同的sql语句并插入到mysql中
        insert_sql,params = item.get_insert_sql()
        cursor.execute(insert_sql,params)
        print('insert done!')

    

#自定义一个图片下载函数,继承自官方的    
class ArticleImagePipeline(ImagesPipeline):
    def item_completed(self,results,item,info):
        if "front_image_url" in item: # 传递进来的是一个list
            for ok,value in results:
                image_file_path = value['path'] # 获取图片路径
            item['front_image_path'] = image_file_path # 有问题,赋值前被引用
            print("download done!")
        return item
    
    
    
class ElasticsearchPipeline(object):
    #将数据写入到es中
    def process_item(self,item,spider):
        #将item转换为es的数据
        item.save_to_es()

        return item
 