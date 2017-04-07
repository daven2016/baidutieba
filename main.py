# -*-coding: utf-8 -*-
from scrapy import cmdline

tieba = ['戒赌', '现金巴士',  '闪银', '宜信', '手机贷', '信用贷', '飞贷']

for item in tieba:
    print('scrapy crawl jieduba -a tieba={0} -a num={1}'.format(item, 5))
    cmdline.execute('scrapy crawl jieduba -a tieba={0} -a num={1}'.format(item, 10001).split())
