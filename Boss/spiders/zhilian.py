import scrapy
from ..items import BossItem
from ..items import ZhilianItem
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
                 '客服', '车务专员', 'DBA']  # 职位
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
                writer.writerow(['位置', '公司名', '公司行业', '学历要求', '经验要求', '薪资', '技能要求', '职位'])

        li_list = response.xpath('//li[@class="job-card-wrapper"]')
        print(f"Number of items found on page {current_page}: {len(li_list)}")

        if not li_list:
            print(f"No more data found for position '{position}' in city '{city}'.")
            return  # 如果没有数据，则停止请求

        for li in li_list:
            title = li.xpath(".//span[@class='job-name']/text()").extract_first() or ''
            salary = li.xpath(".//span[@class='salary']/text()").extract_first() or ''
            area = li.xpath(".//span[@class='job-area']/text()").extract_first() or ''

            # 确保提取job_lable_list的正确性
            job_lable_list = li.xpath(".//ul[@class='tag-list']//text()").extract()
            if len(job_lable_list) >= 2:
                experience = job_lable_list[0] or ''
                education = job_lable_list[1] or ''
            else:
                experience = ''
                education = ''

            company = li.xpath(".//h3[@class='company-name']/a/text()").extract_first() or ''

            # 确保提取company_message的正确性
            company_message = li.xpath(".//ul[@class='company-tag-list']//text()").extract()
            company_type = company_message[0] if company_message else ''

            # 提取boon字段
            boon = li.xpath('.//div[@class="job_card_footer"]//div[@class="info-desc"]/text()').extract()
            boon = boon[0] if boon else None
            # 技能
            skill_list = li.xpath(
                ".//div[@class='job-card-footer clearfix']//ul[@class='tag-list']/li/text()").extract() or []
            skill = "|".join(skill_list)

            # 将数据写入 CSV 文件
            with open(filename, 'a', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow([title, area, salary, experience, education, company, company_type, skill])

            # 创建BossItem对象并传递数据
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
            next_url = response.urljoin(
                f"https://www.zhipin.com/web/geek/job?query={position}&city={city}&page={next_page}")
            yield scrapy.Request(url=next_url, callback=self.parse,
                                 meta={'position': position, 'city': city, 'page': next_page})


class ZhilianSpider(scrapy.Spider):
    name = "zhilian"
    allowed_domains = ["zhaopin.com"]
    max_pages = 10  # 最大页码

    edu_id = input(
        " 初中及以下: 9  高中:  7  中专/中技: 12 大专:  5  本科: 4  硕士: 3 博士: 1  MBA/EMBA: 10 -- 请输入学历类型ID: ")

    # 拼接初始化Url
    start_urls = [
        "https://fe-api.zhaopin.com/c/i/jobs/searched-jobs?pageNo=1&pageSize=90&cityId=682&workExperience=-1&jobType=-1&education=" + edu_id + "&companyType=-1"]

    cotype_list = ['国企: 1', '外商独资: 2', '代表处: 3', '合资: 4', '民营: 5', '股份制企业: 8', '上市公司: 9',
                   '国家机关: 6', '事业单位: 10',
                   '银行: 11',
                   '医院: 12', '学校/下级学院: 13', '律师事务所: 14', '社会团体: 15', '港澳台公司: 16', '其它: 7']
    cosize_list = ['20人以下: 1', '20-99人: 2', '100-299人: 3', '300-499人: 8', '500-999人: 4', '1000-9999人: 5',
                   '10000人以上: 6']
    custom_settings = {
        'LOG_LEVEL': 'INFO',
        'CONCURRENT_REQUESTS': 64
    }

    # 定义职位和城市列表
    positions = ['人力资源', '人事', '行政', '招聘', '薪酬绩效', 'HRBP', '财务', '会计', '测试', '开发', '前端', '后端',
                 '系统运维', '数据管理', 'UI', '项目管理', '产品', '产品架构师', '市场分析师', '项目经理', '算法架构师',
                 '算法工程师', '方案专家', '硬件工程师', '运营', '运维', '商务', '通路行销', '招投标', '法务',
                 '电催/催收', '外访/催收外访', '设计师', '策划师', '大客户经理', '销售', '供应链', '仓库管理专员',
                 '客服', '车务专员', 'DBA']  # 职位
    cities = ["100010000"]  # 城市列表

    def start_requests(self):
        for position in self.positions:
            for city in self.cities:
                url = f"https://www.zhipin.com/web/geek/job?query={position}&city={city}&page=1"
                yield scrapy.Request(url=url, callback=self.parse, meta={'position': position, 'city': city, 'page': 1})

    def parse(self, response):
        # 对应json数据中的data
        datas = json.loads(response.text)
        try:
            totalcount = int(datas['data']['page']['total'])
        except Exception:
            totalcount = 0

        if totalcount == 0:
            # 没有数据
            pass
        elif totalcount <= 270:
            if totalcount <= 90:
                yield scrapy.Request(
                    url=response.url,
                    dont_filter=True,
                    callback=self.parse_result
                )
            elif 90 < totalcount <= 180:
                for page in range(1, 3):
                    yield scrapy.Request(
                        url=str(response.url).replace('pageNo=1', f'pageNo={page}'),
                        dont_filter=True,
                        callback=self.parse_result
                    )
            else:
                for page in range(1, 4):
                    yield scrapy.Request(
                        url=str(response.url).replace('pageNo=1', f'pageNo={page}'),
                        dont_filter=True,
                        callback=self.parse_result
                    )
        else:
            for cotype in self.cotype_list:
                yield scrapy.Request(
                    url=str(response.url).replace('companyType=-1', f'companyType={cotype.split(": ")[1]}'),
                    dont_filter=True,
                    callback=self.parse_cotype
                )

    # 按公司类型解析
    def parse_cotype(self, response):
        datas = json.loads(response.text)
        try:
            totalcount = int(datas['data']['page']['total'])
        except Exception:
            totalcount = 0

        if totalcount == 0:
            pass
        elif totalcount <= 270:
            if totalcount <= 90:
                yield scrapy.Request(
                    url=response.url,
                    dont_filter=True,
                    callback=self.parse_result
                )
            elif 90 < totalcount <= 180:
                for page in range(1, 3):
                    yield scrapy.Request(
                        url=str(response.url).replace('pageNo=1', f'pageNo={page}'),
                        dont_filter=True,
                        callback=self.parse_result
                    )
            else:
                for page in range(1, 4):
                    yield scrapy.Request(
                        url=str(response.url).replace('pageNo=1', f'pageNo={page}'),
                        dont_filter=True,
                        callback=self.parse_result
                    )
        else:
            for cosize in self.cosize_list:
                yield scrapy.Request(
                    url=str(response.url).replace('companySize=-1', f'companySize={cosize.split(": ")[1]}'),
                    dont_filter=True,
                    callback=self.parse_cosize
                )

    # 按公司规模解析
    def parse_cosize(self, response):
        datas = json.loads(response.text)
        try:
            totalcount = int(datas['data']['page']['total'])
        except Exception:
            totalcount = 0

        if totalcount == 0:
            pass
        elif totalcount <= 270:
            if totalcount <= 90:
                yield scrapy.Request(
                    url=response.url,
                    dont_filter=True,
                    callback=self.parse_result
                )
            elif 90 < totalcount <= 180:
                for page in range(1, 3):
                    yield scrapy.Request(
                        url=str(response.url).replace('pageNo=1', f'pageNo={page}'),
                        dont_filter=True,
                        callback=self.parse_result
                    )
            else:
                for page in range(1, 4):
                    yield scrapy.Request(
                        url=str(response.url).replace('pageNo=1', f'pageNo={page}'),
                        dont_filter=True,
                        callback=self.parse_result
                    )
        else:
            for page in range(1, 4):
                yield scrapy.Request(
                    url=str(response.url).replace('pageNo=1', f'pageNo={page}'),
                    dont_filter=True,
                    callback=self.parse_result
                )

    # 对最终的结果进行解析
    def parse_result(self, response):
        item = ZhilianItem()
        datas = json.loads(response.text)
        try:
            data_list = datas['data']['list']
        except Exception:
            data_list = []

        if len(data_list) > 0:
            for data in data_list:
                item = {}
                # 职位名称
                item['poname'] = data['name']
                # 公司名称
                item['coname'] = data['company']
                # 工作城市
                item['city'] = data['workCity']
                # 薪资范围
                item['providesalary'] = data['salary']
                # 学历要求
                item['degree'] = data['education']
                # 公司类型
                item['coattr'] = data['property']
                # 公司规模
                item['cosize'] = data['companySize']
                # 工作经验
                item['worktime'] = data['workingExp']
                # 福利待遇
                # 提取json数据中的value值，先转换为列表，再转换为字符串返回
                json_data = data['welfareLabel']
                json_list = []
                for i in json_data:
                    json_list.append(i['value'])
                temp_data = [str(k) for k in json_list]
                welfare_str = ','.join(temp_data)
                item['welfare'] = welfare_str
                print(item)
                yield item
