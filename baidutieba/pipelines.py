# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
import codecs
import json
from pymongo import MongoClient
from scrapy.conf import settings as st
#import baidutieba.settings as st
from scrapy.exceptions import DropItem
import logging
import datetime


class NormPipeline(object):
    def process_item(self, item, spider):
        creat_time = item['create_time']
        last_time = item['last_reply_time']

        ftime = self.norm_time(creat_time)
        if ftime != -1:
            item['create_time'] = ftime

        ftime = self.norm_time(last_time)
        if ftime != -1:
            item['last_reply_time'] = ftime

        reply_detail = item['reply_detail']
        for play in reply_detail:
            sdt = play['play_time']
            dt = datetime.datetime.strptime(sdt, '%Y-%m-%d %H:%M')
            dt_stamp = int(dt.timestamp())
            play['play_timestamp'] = dt_stamp

        return item

    def norm_time(self, stime):
        if stime.find(':') != -1:
            ts = stime.strip().split(':')
            t = datetime.time(int(ts[0]), int(ts[1]))

            d = datetime.date.today()
            dt = datetime.datetime.combine(d, t)
            #sdt = dt.strftime('%Y-%m-%d %H:%M')
            sdt = int(dt.timestamp())
            return sdt

        if stime.find('-') != -1:
            ds = stime.strip().split('-')
            d = datetime.date(2017, int(ds[0]), int(ds[1]))
            t = datetime.time(0, 0)
            dt = datetime.datetime.combine(d, t)
            #sdt = dt.strftime('%Y-%m-%d %H:%M')
            sdt = int(dt.timestamp())
            return sdt

        logging.debug('Norm_time: new time style {}'.format(stime))
        return -1


class BaidutiebaPipeline(object):
    def __init__(self):
        self.file = codecs.open('jieduba.json', 'w', encoding='utf-8')

    def process_item(self, item, spider):

        line = json.dumps(dict(item), ensure_ascii=False) + '\n'
        self.file.write(line)  #.decode('unicode_escape')
        return item

class MongodbPipeline(object):
    def __init__(self):
        client = MongoClient(st['MONGODB_SERVER'], st['MONGODB_PORT'])
        db = client[st['MONGODB_DB']]
        self.collection = db[st['MONGODB_COLLECTION']]

    def process_item(self, item, spider):  # 注意：这个函数的名字不能改
        valid = True
        for data in item:
            if not data:
                valid = False
                raise DropItem('Missing{0}！'.format(data))
        if valid:
            #self.collection.insert(dict(item))
            self.collection.update({'id': item['id']}, {'$set': dict(item)}, upsert=True)

            logging.debug("Save To Mongodb: success \n")

        return item


