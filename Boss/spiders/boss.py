import scrapy
from ..items import BossItem
import csv


class BossSpider(scrapy.Spider):
    name = "boss"
    allowed_domains = ["www.zhipin.com"]
    start_urls = ["https://www.zhipin.com/"]
    max_pages = 10  # 最大页码

    # 定义职位和城市列表
    positions = ['人力资源', '人事', '行政', '招聘', '薪酬绩效', 'HRBP', '财务', '会计', '测试', '开发', '前端', '后端',
                 '系统运维', '数据管理', 'UI', '项目管理', '产品', '产品架构师', '市场分析师', '项目经理', '算法架构师',
                 '算法工程师', '方案专家', '硬件工程师', '运营', '运维', '商务', '通路行销', '招投标', '法务',
                 '电催/催收', '外访/催收外访', '设计师', '策划师', '大客户经理', '销售', '供应链', '仓库管理专员',
                 '客服', '车务专员']  # 职位
    cities = ["100010000"]  # 城市列表

    def start_requests(self):
        for position in self.positions:
            for city in self.cities:
                url = f"https://www.zhipin.com/web/geek/job?query={position}&city={city}&page=1"
                yield scrapy.Request(url=url, callback=self.parse, meta={'position': position, 'city': city, 'page': 1})

    def parse(self, response):
        position = response.meta['position']
        city = response.meta['city']
        current_page = response.meta['page']
        filename = f"./files/BOSS_{position}_全国.csv"

        # 创建文件并写入表头
        if current_page == 1:
            with open(filename, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(['职位', '公司', '薪资', '经验', '教育', '技能'])

        li_list = response.xpath('//li[@class="job-card-wrapper"]')
        print(f"Number of items found on page {current_page}: {len(li_list)}")

        if not li_list:
            print(f"No more data found for position '{position}' in city '{city}'.")
            return  # 如果没有数据，则停止请求

        for li in li_list:
            title = li.xpath(".//span[@class='job-name']/text()").extract_first() or ''
            salary = li.xpath(".//span[@class='salary']/text()").extract_first() or ''
            area = li.xpath(".//span[@class='job-area']/text()").extract_first() or ''

            job_label_list = li.xpath(".//ul[@class='tag-list']//text()").extract()
            if len(job_label_list) >= 2:
                experience = job_label_list[0] or ''
                education = job_label_list[1] or ''
            else:
                experience = ''
                education = ''

            company = li.xpath(".//h3[@class='company-name']/a/text()").extract_first() or ''
            company_message = li.xpath(".//ul[@class='company-tag-list']//text()").extract()
            company_type = company_message[0] if company_message else ''
            boon = li.xpath('.//div[@class="job_card_footer"]//div[@class="info-desc"]/text()').extract()
            boon = boon[0] if boon else None
            skill_list = li.xpath('.//div[@class="job-card-footer clearfix"]//ul[@class="tag-list"]/li/text()').extract() or []
            skill = "|".join(skill_list)

            # 将数据写入 CSV 文件
            with open(filename, 'a', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow([title, company, salary, experience, education, skill])

            book = BossItem(
                title=title,
                address=area,
                salary=salary,
                experience=experience,
                education=education,
                company=company,
                companyType=company_type,
                skill_list=skill,
            )
            yield book

        # 处理下一页
        if current_page < self.max_pages:  # 检查是否超过最大页码
            next_page = current_page + 1
            next_url = response.urljoin(f"https://www.zhipin.com/web/geek/job?query={position}&city={city}&page={next_page}")
            yield scrapy.Request(url=next_url, callback=self.parse, meta={'position': position, 'city': city, 'page': next_page})
