# -*- coding: utf-8 -*-
import requests
#import MySQLdb
import pymysql
from scrapy.selector import Selector
from time import sleep

conn = pymysql.connect(host="127.0.0.1",user="root",passwd="123456",db="article_spider",charset="utf8")
cursor = conn.cursor()

def crawl_ips():
    #爬取西刺免费IP代理
    headers = {"User-Agent":"Mozilla/5.0 (X11; Ubuntu; Linux i686; rv:58.0) Gecko/20100101 Firefox/58.0"}
    count = 0
    for i in range(100):    
        re = requests.get('http://www.xicidaili.com/wn/{0}'.format(i),headers = headers)
        selector = Selector(text = re.text)
        all_trs = selector.css("#ip_list tr")
        ip_list = []
        for tr in all_trs[1:]:
            speed_str = tr.css(".bar::attr(title)").extract()[0]
            if speed_str:
                speed = float(speed_str.split("秒")[0])
            all_texts = tr.css("td::text").extract()
            ip = all_texts[0]
            port = all_texts[1]
            proxy_type = all_texts[5]
            
            ip_list.append((ip,port,proxy_type,speed))
        
        for ip_info in ip_list:
            print(ip_info[0],ip_info[1],ip_info[3])
            sleep(0.1)
            cursor.execute(
                    "insert proxy_ip(ip,port,speed,proxy_type) VALUES('{0}','{1}',{2},'HTTPS')".format(ip_info[0],ip_info[1],ip_info[3])
                    )
            conn.commit()
            count += 1
            print("Inster done!",count)

class GetIP(object):
    def delete_ip(self,ip):
        #从数据库中删除无效IP
        delete_sql = """
            delete from proxy_ip where ip='{0}'
        """.format(ip)
        cursor.execute(delete_sql)
        conn.commit()
        return True
    
    def check_ip(self,ip,port):
        #判断ip可用
        http_url = "https://www.baidu.com"
        proxy_url = "https://{0}:{1}".format(ip,port)
        try:
            proxy_dict = {
                    "https":proxy_url,
                    }
            response = requests.get(http_url,proxies=proxy_dict)
        except Exception as e:
            print("无效IP")
            self.delete_ip(ip)
            return False
        else:
            code = response.status_code
            if code >= 200 and code < 300:
                print("可用IP")
                return True
            else:
                print("无效IP")
                self.delete_ip(ip)
                return False
    def get_random_ip(self):
        #从数据库中随机获取一个IP
        random_sql = "SELECT ip,port from proxy_ip ORDER BY RAND() LIMIT 1"
        result = cursor.execute(random_sql)
        for ip_info in cursor.fetchall():
            ip = ip_info[0]
            port = ip_info[1]
            check_re = self.check_ip(ip,port)
            if check_re:
                proxyIP = "https://{0}:{1}".format(ip,port)
#                print(proxyIP)
                return proxyIP
            else:
                return self.get_random_ip()
#print(crawl_ips())

if __name__ == '__main__':
#    crawl_ips()
    get_ip = GetIP()
    get_ip.get_random_ip()

