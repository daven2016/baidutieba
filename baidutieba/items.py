# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class BaidutiebaItem(scrapy.Item):
    # define the fields for your item here like:
    collection = scrapy.Field()
    id = scrapy.Field()
    subject = scrapy.Field()
    author = scrapy.Field()
    create_time = scrapy.Field()
    reply_count = scrapy.Field()
    url = scrapy.Field()
    post_detail = scrapy.Field()

    last_reply = scrapy.Field()
    last_reply_time = scrapy.Field()

    reply_detail = scrapy.Field()
