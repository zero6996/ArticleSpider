# -*- coding: utf-8 -*-

from elasticsearch_dsl import DocType,Date,analyzer,Completion,Keyword,Text,Integer

from elasticsearch_dsl.analysis import CustomAnalyzer as _CustomAnalyzer

from elasticsearch_dsl.connections import connections
connections.create_connection(hosts=["localhost"]) # 设置连接服务器,允许连接多个服务器

# 自定义分析器
class CustomAnalyzer(_CustomAnalyzer):
    def get_analysis_definition(self):
        return {}

ik_analyzer = CustomAnalyzer('ik_max_word',filter=['lowercase']) # filter，大小写转换

class ArticleType(DocType):
    #伯乐在线文章类型
    suggest = Completion(analyzer=ik_analyzer)
    title = Text(analyzer="ik_max_word") #定义存储类型,分析器
    create_date = Date()
    url = Keyword() # 文章链接
    url_object_id = Keyword() # md5后链接
    front_image_url = Keyword() # 图片链接
    front_image_path = Keyword() # 图片存放路径
    praise_number = Integer()
    fav_nums = Integer()
    comment_nums = Integer()
    tags = Text(analyzer="ik_max_word")
    content = Text(analyzer="ik_max_word")
    
    class Meta:
        index = "jobbole" # 设置index名
        doc_type = "article" # 设置表名

my_analyzer = analyzer('ik_smart')

class ArticleType_Lagou(DocType):
    '''拉勾 类型'''
    suggest = Completion(analyzer=my_analyzer)
    title = Text(analyzer='ik_max_word') # 标题
    url = Keyword() 
    url_object_id = Keyword()
    salary_min = Integer() # 最低工资
    salary_max = Integer() # 最高工资
    job_city = Keyword() # 工作城市
    work_years_min = Integer() # 工作年限
    work_years_max = Integer()
    degree_need = Text(analyzer='ik_max_word') # 学历需求
    job_type = Keyword() # 工作类型
    publish_time = Date() # 发布时间
    job_advantage = Text(analyzer='ik_max_word') # 职位诱惑
    job_desc = Text(analyzer='ik_smart') # 职位描述
    job_addr = Text(analyzer='ik_max_word') # 工作地址
    company_name = Keyword() # 公司名称
    company_url = Keyword() # 公司链接
    tags = Text(analyzer='ik_max_word') # 标签
    crawl_time = Date() # 爬取时间

    class Meta:
        index = "lagou_job"
        doc_type = "job"


if __name__ == "__main__":
    ArticleType_Lagou.init()
