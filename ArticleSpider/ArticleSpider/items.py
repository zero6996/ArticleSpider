# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import re
from datetime import datetime,timedelta
import scrapy
from scrapy.loader import ItemLoader
from scrapy.loader.processors import MapCompose,TakeFirst,Join
from w3lib.html import remove_tags
from settings import SQL_DATETIME_FORMAT,SQL_DATE_FORMAT
from models.es_types import ArticleType,ArticleType_Lagou

from elasticsearch_dsl.connections import connections
es = connections.create_connection(ArticleType._doc_type.using) # es_PythonAPI接口
# job_es = connections.create_connection(ArticleType_Lagou._doc_type.using)



def date_convert(value):
    try:
        create_date = datetime.strptime(value,"%Y/%m/%d").date()
    except Exception as e:
        create_date = datetime.now().date()
    return create_date


def get_nums(value):
    try:
        match_re = re.match(".*?(\d+).*",value)
        if match_re:
            nums = int(match_re.group(1))
        else:
            nums = 0
    except:
        nums = 0
    return nums


def remove_comment_tags(value):
    #去掉tag中提取的评论
    if "评论" in value:
        return ""
    else:
        return value


def return_value(value):
    return value


def extract_content(value):
    cont_re = re.findall(r'[\s\S]*?>([\s\S]*?)<[\s\S]*?',value)
    return str(cont_re).replace('\\n','').replace('\\t','').replace('\\r','').replace(' ','').replace('\\xa0','')


def gen_suggests(index,info_tuple):
    #根据字符串生成搜索建议数组
    used_words = set() # 去重
    suggests = []
    for text,weight in info_tuple:
        if text:
            # 调用es的analyze接口分析字符串
            words = es.indices.analyze(index=index,analyzer='ik_max_word',params={'filter':['lowercase']},body=text)
            analyzed_words = set(r["token"] for r in words['tokens'] if len(r['token'])>1) 
            new_words = analyzed_words - used_words # 已存在的过滤掉
        else:
            new_words = set()

        if new_words:
            suggests.append({"input":list(new_words),"weight":weight})
    return suggests


class ArticleItemLoader(ItemLoader):
    #自定义itemloader
    default_output_processor = TakeFirst()


#jobbole item
class JobboleArticleItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    
    title = scrapy.Field() # 标题
    create_date = scrapy.Field(
            input_processor = MapCompose(date_convert), # MapCompose(function1,function2,...)
#            output_processor = TakeFirst()
            ) # 创建时间
    url = scrapy.Field() # 文章链接
    url_object_id = scrapy.Field() # md5后链接
    front_image_url = scrapy.Field(
            output_processor = MapCompose(return_value)
            ) # 图片链接
    front_image_path = scrapy.Field() # 图片存放路径
    praise_number = scrapy.Field(
                input_processor = MapCompose(get_nums)
            )
    fav_nums = scrapy.Field(
            input_processor = MapCompose(get_nums)
            )
    comment_nums = scrapy.Field(
            input_processor = MapCompose(get_nums)
            )
    tags = scrapy.Field(
            input_processor = MapCompose(remove_comment_tags),
            output_processor=Join(',')
            )
    content = scrapy.Field()


    def save_to_es(self):
        article = ArticleType()
        article.title = self['title']
        article.create_date = self['create_date']
        article.content = remove_tags(self['content'])
        article.front_image_url = self['front_image_url']
        if 'front_image_path' in self:
            article.front_image_path = self['front_image_path']
        try:
            article.praise_number = self["praise_number"]
        except:
            print("items出错")
            article.praise_number = 99999
        article.comment_nums = self['comment_nums']
        article.content = self['content']
        article.tags = self['tags']
        article.fav_nums = self['fav_nums']
        article.url = self['url']
        article.meta.id = self['url_object_id']

        article.suggest = gen_suggests(ArticleType._doc_type.index,((article.title,10),(article.tags,7))) #分词

        article.save()

        return 




# lagou items
def remove_splash(value):
    #去掉城市的斜线
    return value.replace('/','')

def handle_jobaddr(value):
    addr_list = value.split('\n')
    addr_list = [item.strip() for item in addr_list if item.strip()!="查看地图"]
    return "".join(addr_list)


class LagouJobItemLoader(ItemLoader):
    #自定义item_loader
    default_output_processor = TakeFirst()


class LagouJobItem(scrapy.Item):
    #拉勾网职位信息
    title = scrapy.Field()
    url = scrapy.Field()
    url_object_id = scrapy.Field()
    salary_min = scrapy.Field()
    salary_max = scrapy.Field()
    job_city = scrapy.Field(
            input_processor = MapCompose(remove_splash),
            )
    work_years_min = scrapy.Field(
            input_processor = MapCompose(remove_splash),
            )
    work_years_max = scrapy.Field(
        input_processor=MapCompose(remove_splash),
    )
    degree_need = scrapy.Field(
            input_processor = MapCompose(remove_splash),
            )
    job_type = scrapy.Field()
    publish_time = scrapy.Field()
    job_advantage = scrapy.Field()
    job_desc = scrapy.Field()
    job_addr = scrapy.Field(
            input_processor = MapCompose(remove_tags,handle_jobaddr),
            )
    company_name = scrapy.Field()
    company_url = scrapy.Field()
    tags = scrapy.Field(
            input_processor = Join(','),
            )
    crawl_time = scrapy.Field()
    crawl_update_time = scrapy.Field()


    def clean_data(self):

        #clean_work_years
        match_obj1 = re.match("经验(\d+)-(\d+)年",self['work_years_min'])
        match_obj2 = re.match("经验应届毕业生",self['work_years_min'])
        match_obj3 = re.match("经验不限",self['work_years_min'])
        match_obj4 = re.match("经验(\d+)年以下",self['work_years_min'])
        match_obj5 = re.match("经验(\d+)年以上",self['work_years_min'])

        if match_obj1:
            self["work_years_min"] = match_obj1.group(1)
            self["work_years_max"] = match_obj1.group(2)
        elif match_obj2:
            self["work_years_min"] = 0.5
            self["work_years_max"] = 0.5
        elif match_obj3:
            self["work_years_min"] = 0
            self["work_years_max"] = 0
        elif match_obj4:
            self["work_years_min"] = 0
            self["work_years_max"] = match_obj4.group(1)
        elif match_obj5:
            self["work_years_min"] = match_obj4.group(1)
            self["work_years_max"] = match_obj4.group(1) + 100
        else:
            self["work_years_min"] = 999
            self["work_years_max"] = 999

        #clean salary
        match_salary = re.match("(\d+)[Kk]-(\d+)[Kk]", self['salary_min']) # 使用正则获取最低最高工资
        if  match_salary:
            self['salary_min'] = match_salary.group(1)
            self['salary_max'] = match_salary.group(2)
        else:
            self['salary_min'] = 666
            self['salary_max'] = 666


        #clean_time
        match_time1 = re.match("(\d+):(\d+).",self["publish_time"])
        match_time2 = re.match("(\d+)天前.*",self["publish_time"])
        match_time3 = re.match("(\d+)-(\d+)-(\d+)",self["publish_time"])
        if match_time1:
            today = datetime.now()
            hour = int(match_time1.group(1))
            minutues = int(match_time1.group(2))
            time = datetime(today.year,today.month,today.day,hour,minutues)
            self["publish_time"] = time.strftime(SQL_DATETIME_FORMAT)
        elif match_time2:
            days_ago = int(match_time2.group(1))
            today = datetime.now() - timedelta(days=days_ago)
            self["publist_time"] = today.strftime(SQL_DATETIME_FORMAT)
        elif match_time3:
            year = int(match_time3.group(1))
            month = int(match_time3.group(2))
            day = int(match_time3.group(3))
            today = datetime(year,month,day)
            self["publist_time"] = today.strftime(SQL_DATETIME_FORMAT)
        else:
            self["publist_time"] = datetime.now().strftime(SQL_DATETIME_FORMAT)
        self["crawl_time"] = self["crawl_time"].strftime(SQL_DATETIME_FORMAT)

    def get_insert_sql(self):
        insert_sql = '''
            insert into lagou_job(title,url,url_object_id,salary_min,salary_max,job_city,work_years_min,work_years_max,degree_need,job_type,
            publish_time,job_advantage,job_desc,job_addr,company_name,company_url,tags,
            crawl_time) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
            ON DUPLICATE KEY UPDATE salary_min=VALUES(salary_min),salary_max=VALUES(salary_max),job_desc=VALUES(job_desc)
        '''
        self.clean_data()
        sql_params = (
                self['title'],self['url'],self['url_object_id'],self['salary_min'],self['salary_max'],self['job_city'],
                self['work_years_min'],self['work_years_max'],self['degree_need'],self['job_type'],
                self['publish_time'],self['job_advantage'],self['job_desc'],
                self['job_addr'],self['company_name'],self['company_url'],
                self['tags'],self['crawl_time']
                )
        return insert_sql,sql_params

    def save_to_es(self):
        self.clean_data()
        job = ArticleType_Lagou()
        job.title = self['title']
        job.url = self['url']
        job.url_object_id = self['url_object_id']
        job.salary_min = self['salary_min']
        job.salary_max = self['salary_max']
        job.job_city = self['job_city']
        job.work_years_min = self['work_years_min']
        job.work_years_max = self['work_years_max']
        job.degree_need = self['degree_need']
        job.job_type = self['job_type']
        job.publish_time = self['publish_time']
        job.job_advantage = self['job_advantage']
        job.job_desc = remove_tags(self["job_desc"]).strip().replace("\r\n","").replace("\t","")
        job.job_addr = self['job_addr']
        job.company_name = self['company_name']
        job.company_url = self['company_url']
        job.tags = self['tags']
        job.crawl_time = self['crawl_time']

        job.suggest = gen_suggests(ArticleType_Lagou._doc_type.index,((job.title,10),(job.tags,7),(job.job_advantage,6),
                                                                      (job.job_desc,3),(job.job_addr,5),(job.company_name,8),
                                                                      (job.degree_need,4),(job.job_city,9)))

        job.save()

        return
