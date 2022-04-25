import scrapy


class QuotesSpider(scrapy.Spider):
    name = "toscrape-xpath"

    def start_requests(self):
        start_urls = [
            'http://quotes.toscrape.com/page/1/'
        ]
        for url in start_urls:
            yield scrapy.Request(url=url, callback=self.parse)
    def parse(self, response):
        for quote in response.xpath("//div[@class='quote']"):
            yield {
                'text': quote.xpath(".//span/text()").get(),
                'author': quote.xpath(".//small[@class='author']/text()").get(),
                'tags': quote.xpath(".//div[@class='tags']//a[@class='tag']/text()").getall()
            }
  
        
        next_page_url = response.xpath('//li[@class="pager"]/a/@href').extract_first()
        print ("next page URL is :", next_page_url)
        x = input()
        if next_page_url is not None:
            yield response.follow(next_page_url, callback=self.parse)

