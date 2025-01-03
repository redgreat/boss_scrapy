# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class BossItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    title = scrapy.Field()
    address = scrapy.Field()
    salary = scrapy.Field()
    experience = scrapy.Field()
    education = scrapy.Field()
    company = scrapy.Field()
    companyType = scrapy.Field()
    skill_list = scrapy.Field()
    pass


class ZhilianItem(scrapy.Item):
    # define the fields for your item here like:
    # 职位名称
    poname = scrapy.Field()
    # 公司名称
    coname = scrapy.Field()
    # 工作城市
    city = scrapy.Field()
    # 薪资范围
    providesalary = scrapy.Field()
    # 学历要求
    degree = scrapy.Field()
    # 公司类型
    coattr = scrapy.Field()
    # 公司规模
    cosize = scrapy.Field()
    # 工作经验
    worktime = scrapy.Field()
    # 福利待遇
    welfare = scrapy.Field()
