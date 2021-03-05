import scrapy
from scrapy.loader import ItemLoader
from itemloaders.processors import TakeFirst
from datetime import datetime
from bdees.items import Article


class BdeesSpider(scrapy.Spider):
    name = 'bdees'
    allowed_domains = ['bde.es']
    start_urls = ['https://www.bde.es/bde/es/Home/Noticias/index6.html']

    def parse(self, response):
        articles = response.xpath('//ul[@class="listados"]//li')
        for article in articles:
            link = article.xpath('./a/@href').get()
            date = article.xpath('./span/span/text()').get()
            if date:
                date = date.strip()

            yield response.follow(link, self.parse_article, cb_kwargs=dict(date=date))

        next_page = response.xpath('//a[@class="next"]/@href').get()
        if next_page:
            yield response.follow(next_page, self.parse)

    def parse_article(self, response, date):
        if 'pdf' in response.url:
            return

        item = ItemLoader(Article())
        item.default_output_processor = TakeFirst()

        title = response.xpath('//h2[@class="tituloCentro"]/text()').get()
        if title:
            title = title.strip()

        content = response.xpath('//div[contains(@class, "content clearfix")]//text()').getall()
        content = [text for text in content if text.strip()]
        content = "\n".join(content[1:]).strip()

        item.add_value('title', title)
        item.add_value('date', date)
        item.add_value('link', response.url)
        item.add_value('content', content)

        return item.load_item()
