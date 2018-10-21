# -*- coding: utf-8 -*-

from selenium import webdriver
from scrapy.selector import Selector
import time


#browser = webdriver.Firefox()


#完成微博的模拟登录
#browser.get("https://www.oschina.net/blog")
#time.sleep(5)
#browser.find_element_by_css_selector("#loginname").send_keys("18868307401")
#browser.find_element_by_css_selector(".info_list.password input[node-type='password']").send_keys("lzj5566")
#browser.find_element_by_css_selector(".info_list.login_btn a[node-type='submitBtn']").click()

#for i in range(3):
#    browser.execute_script("window.scrollTo(0,document.body.scrollHeight); var lenOfPage=document.body.scrollHeight; return lenOfPage;")
#    time.sleep(3)

#设置不加载图片
#chrome_opt = webdriver.ChromeOptions()
#prefs = {'profile.managed_default_content_settings.images':2}
#chrome_opt.add_experimental_option("prefs",prefs)
#browser = webdriver.Chrome()#chrome版本不同,无法使用
#browser.get("https://www.taobao.com")

#phantomjs,无界面的浏览器,多进程情况下性能会严重下降
#browser = webdriver.PhantomJS()
#browser.get("https://www.taobao.com")
#print(browser.page_source)
#
#time.sleep(10)
#browser.quit()