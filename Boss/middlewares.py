import os

from scrapy import signals
from scrapy.http import HtmlResponse
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import json


def process_spider_output(response, result, spider):
    for i in result:
        yield i


def process_spider_input(response, spider):
    return None


def process_start_requests(start_requests, spider):
    for r in start_requests:
        yield r


def spider_opened(spider):
    spider.logger.info("Spider opened: %s" % spider.name)


class BossSpiderMiddleware:
    @classmethod
    def from_crawler(cls, crawler):
        s = cls()
        crawler.signals.connect(spider_opened, signal=signals.spider_opened)
        return s

    def process_spider_exception(self, response, exception, spider):
        pass


def get_cookies(url, cookies):
    driver = webdriver.Chrome()
    driver.get(url)
    time.sleep(6)
    dict_cookies = driver.get_cookies()
    json_cookies = json.dumps(dict_cookies)
    with open(cookies, "w") as fp:
        fp.write(json_cookies)
        print('Cookies保存成功！')
    driver.quit()


class SeleniumMiddleware:

    def __init__(self):
        self.cookie_file = 'boss_cookies.json'
        if not os.path.exists(self.cookie_file):
            with open(self.cookie_file, 'w') as f:
                pass
        get_cookies('https://www.zhipin.com/web/geek/job-recommend', self.cookie_file)
        self.driver = webdriver.Chrome()

    def load_cookies(self):
        # 先访问主域名
        self.driver.get("https://www.zhipin.com")
        with open(self.cookie_file, "r") as fp:
            cookies = json.load(fp)
        for cookie in cookies:
            if 'domain' in cookie:
                del cookie['domain']  # 删除 domain 键，避免 invalid cookie domain
            self.driver.add_cookie(cookie)

    def process_request(self, request, spider):
        try:
            self.load_cookies()
            target_url = request.url
            print(f"Fetching URL: {target_url}")
            self.driver.get(target_url)
            self.driver.refresh()

            # 等待元素加载完成
            WebDriverWait(self.driver, 20).until(EC.presence_of_element_located((By.CLASS_NAME, "job-card-wrapper")))

            data = self.driver.page_source
            return HtmlResponse(url=request.url, body=data, encoding='utf-8', request=request)
        except Exception as e:
            print(f"An error occurred: {e}")
            return HtmlResponse(url=request.url, status=500, request=request)

    def __del__(self):
        if self.driver:
            self.driver.quit()
