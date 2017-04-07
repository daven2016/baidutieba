# -*- coding: utf-8 -*-
import scrapy
import json
#import re
from baidutieba.items import BaidutiebaItem

class JiedubaSpider(scrapy.Spider):
    name = "jieduba"
    allowed_domains = ["baidu.com"]
    start_urls = ['http://tieba.baidu.com/f?kw=戒赌&ie=utf-8&pn=0']

    def start_requests(self):
        reqs = []
        for i in range(0, 10001, 50):
            #req = scrapy.Request('http://tieba.baidu.com/f?kw=戒赌&ie=utf-8&pn=%s' % i)
            req = scrapy.Request('http://tieba.baidu.com/f?kw=闪银&ie=utf-8&pn=%s' % i)
            reqs.append(req)

        return reqs

    def parse(self, response):

        lis = response.xpath('//*[@id="thread_list"]/li')
        if not lis:
            self.logger.info("Post Page error--%s" % response.url)
            return

        for li in lis[1:]:
            i = BaidutiebaItem()
            data_field = li.xpath('./@data-field').extract()[0]
            data = json.loads(data_field)
            if 'id' in data:
                i['id'] = data['id']
            i['post_detail'] = data_field
            i['subject'] = li.xpath('div/div[2]/div[1]/div[1]/a/text()').extract()[0]
            i['reply_count'] = li.xpath('div/div[1]/span/text()').extract()[0]
            i['author'] = li.xpath('div/div[2]/div[1]/div[2]/span[1]').re(r'title=".*?:(.*?)"')[0]
            i['create_time'] = li.xpath('div/div[2]/div[1]/div[2]/span[2]/text()').extract()[0]
            i['last_reply'] = li.xpath('div/div[2]/div[2]/div[2]/span[1]').re(r'title=".*?:(.*?)"')[0]
            i['last_reply_time'] = li.xpath('div/div[2]/div[2]/div[2]/span[2]/text()').extract()[0].strip()

            post_url = li.xpath('div/div[2]/div[1]/div[1]/a/@href').extract()
            i['url'] = 'https://tieba.baidu.com' + post_url[0]

            yield scrapy.Request(url=i['url'], meta={'item': i}, callback=self.parse_detail, dont_filter=True)


    def parse_detail(self, response):

        item = response.meta['item']
        reply_detail = []

        div = response.xpath('//*[@class="left_section"]')
        if not div:
            # 网页不存在
            self.logger.info('Post Detail Page error--%s' % response.url)
            with open('badurl.txt', 'a') as f:
                f.write(response.url + '\n')
            return

        # 取出所有楼层
        plays = div.xpath('div[2]/div')
        for play in plays:
            one_play = {}
            one_play['play_detail'] = play.xpath('./@data-field').extract_first(default='not found')

            one_play['content'] = play.xpath('string(div[2]/div[1]/cc/div)').extract_first(default='no content')
            one_play['user_name'] = play.xpath('div[1]//li[@class="d_name"]/a/text()').extract_first(default='no name')
            one_play['vip'] = play.xpath('div[1]//li[@class="l_badge"]/div/a/div[2]/text()').extract_first(default=-1)

            floor = play.xpath('.//div[@class="core_reply_tail clearfix"]')
            one_play['play_time'] = floor.re(r'>(\d{4}.*?\d)<')[0]
            client = floor.re(r'blank">(.*?)</a>')
            if client:
                one_play['client'] = client[0]
            one_play['play_no'] = floor.re(r'>(\d+)楼')[0]

            if one_play:
                reply_detail.append(one_play)

        item['reply_detail'] = reply_detail

        # 取出总页数
        pages = response.xpath('//div[@class="l_thread_info"]/ul/li[2]/span[2]/text()').extract_first()
        pages = int(pages)
        if pages == 1: # 如果只有1页则返回item 给 pipelines
            yield item
        else:          # 多页则继续取下一页
            # https://tieba.baidu.com/p/5039992267?pn=2
            # https://tieba.baidu.com/p/5039992267  若只有1页则是这个格式
            url = response.url
            new_url = url + '?pn=2'
            yield scrapy.Request(url=new_url, meta={'item': item, 'pages': pages}, callback=self.sub_parse_detail, dont_filter=True)



    def sub_parse_detail(self, response):
        self.logger.info("SUB_APRSE_DETAIL IS RUNNING\n")
        item = response.meta['item']
        reply_detail = []
        # 取出所有楼层
        plays = response.xpath('//*[@class="left_section"]/div[2]/div')
        for play in plays:
            one_play = {}
            one_play['play_detail'] = play.xpath('./@data-field').extract_first(default='not found')

            one_play['content'] = play.xpath('string(div[2]/div[1]/cc/div)').extract_first(default='no content')
            one_play['user_name'] = play.xpath('div[1]//li[@class="d_name"]/a/text()').extract_first(default='no name')
            one_play['vip'] = play.xpath('div[1]//li[@class="l_badge"]/div/a/div[2]/text()').extract_first(default=-1)

            floor = play.xpath('.//div[@class="core_reply_tail clearfix"]')
            one_play['play_time'] = floor.re(r'>(\d{4}.*?\d)<')[0]
            client = floor.re(r'blank">(.*?)</a>')
            if client:
                one_play['client'] = client[0]
            one_play['play_no'] = floor.re(r'>(\d+)楼')
            if one_play:
                reply_detail.append(one_play)

        item['reply_detail'].extend(reply_detail)

        pages = response.meta['pages']
        url = response.url
        pn = url.split('=')
        page = int(pn[1])

        if page < pages:
            new_url = pn[0] + '=' + str(page + 1)
            yield scrapy.Request(url=new_url, meta={'item': item, 'pages': pages}, callback=self.sub_parse_detail,
                                 dont_filter=True)
        else:
            yield item



