# -*- coding: utf-8 -*-
# -*- coding: utf-8 -*-
import scrapy
from scrapy import Spider, Request
from urllib.parse import quote
from scrapysplashtest.items import ProductItem
from scrapy_splash import SplashRequest

#使用翻页脚本,''''''

script = """
function main(splash, args)
  splash.images_enabled = false
  assert(splash:go(args.url))
  assert(splash:wait(args.wait))
  js = string.format("document.querySelector('#J_waterfallPagination a.pageJump > input').value=%d;document.querySelector('#J_waterfallPagination a.pageConfirm').click()", 1)
  splash:evaljs(js)
  assert(splash:wait(args.wait))
  return splash:html()
end
"""

class TaobaoSpider(scrapy.Spider):
    name = 'taobao'
    allowed_domains = ['www.taobao.com']
    base_url = 'https://uland.taobao.com/sem/tbsearch?keyword='
    #'https://s.taobao.com/search?q='#该地址需要登录

    def start_requests(self):
        for keyword in self.settings.get('KEYWORDS'):
            for page in range(1, self.settings.get('MAX_PAGE') + 1):
                url = self.base_url + quote(keyword)
                yield SplashRequest(url, callback=self.parse, endpoint='execute',
                                    args={'lua_source': script, 'page': page, 'wait': 7})

    def parse(self, response):
        products = response.xpath(
            '//div[@id="searchResult"]//div[@id="ItemWrapper"]//div[contains(@class, "item")]')
        for product in products:
            item = ProductItem()
            item['price'] = ''.join(product.xpath('.//p[contains(@class, "price")]//text()').extract()).strip()
            item['title'] = ''.join(product.xpath('.//span[contains(@class, "title")]//text()').extract()).strip()
            item['shop'] = ''.join(product.xpath('.//p[contains(@class, "shopName")]/span[@class="shopNick"]//text()').extract()).strip()
            item['image'] = ''.join(
                product.xpath('.//div[@class="imgContainer"]//img[1]/@src').extract()).strip()
            item['deal'] = product.xpath('.//p[contains(@class, "shopName")]/span[@class="payNum"]//text()').extract_first()
            #item['location'] = product.xpath('.//div[contains(@class, "location")]//text()').extract_first()
            yield item