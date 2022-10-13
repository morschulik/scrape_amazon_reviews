import math
from urllib.parse import urlencode, urljoin
import scrapy
from parsel import Selector
from scrapy import signals
from scrapy.http import TextResponse
import httpx
from typing_extensions import TypedDict
import asyncio
import json
from loguru import logger as log


# We need to use browser-like headers for our requests to avoid being blocked
# here we set headers of Chrome browser on Windows:
BASE_HEADERS = {
    "accept-language": "en-US,en;q=0.9",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36",
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
    "accept-encoding": "gzip, deflate, br",
}
queries = ["fridge"]


class AmazonSpider(scrapy.Spider):
    def __init__(self, name=None, **kwargs):
        super().__init__(name, kwargs)
        self.parse_product_page = None

    def start_requests(self):
        for query in queries:
            url = 'https://www.amazon.com/s?' + urlencode({'k': query})
            yield scrapy.Request(url=url, callback=self.parse_keyword_response)

    def parse_keyword_response(self, response):
        products = response.xpath('//*[@data-asin]')
        for product in products:
            asin = product.xpath('@data-asin').extract_first()
            product_url = f"https://www.amazon.com/dp/{asin}"
            yield scrapy.Request(url=product_url, callback=self.parse_product_page, meta={'asin': asin})
        next_page = response.xpath('//li[@class="a-last"]/a/@href').extract_first()
        if next_page:
            url = urljoin("https://www.amazon.com", next_page)
            yield scrapy.Request(url=url, callback=self.parse_keyword_response)


class ReviewData(TypedDict):
    """storage type hint for amazons review object"""
    title: str
    text: str
    location_and_date: str
    verified: bool
    rating: float


def parse_reviews(response): #-> ReviewData:
    """parse review from single review page"""
    sel = Selector(text=response.text)
    review_boxes = sel.css("#cm_cr-review_list div.review")
    parsed = []
    for box in review_boxes:
        parsed.append({
                "text": "".join(box.css("span[data-hook=review-body] ::text").getall()).strip(),
                "title": box.css("*[data-hook=review-title]>span::text").get(),
                "location_and_date": box.css("span[data-hook=review-date] ::text").get(),
                "verified": bool(box.css("span[data-hook=avp-badge] ::text").get()),
                "rating": box.css("*[data-hook*=review-star-rating] ::text").re(r"(\d+\.*\d*) out")[0],
        })
    return parsed


async def scrape_reviews(asin, session: httpx.AsyncClient):  # -> ReviewData:
    """scrape all reviews of a given ASIN of an amazon product"""
    url = f"https://www.amazon.com/product-reviews/{asin}/"
    log.info(f"scraping review page: {url}")
    # find first page
    first_page = await session.get(url)
    sel = Selector(text=first_page.text)
    # find total amount of pages
    total_reviews = sel.css("div[data-hook=cr-filter-info-review-rating-count] ::text").re(r"(\d+,*\d*)")[1]
    total_reviews = int(total_reviews.replace(",", ""))
    total_pages = int(math.ceil(total_reviews / 10.0))

    log.info(f"found total {total_reviews} reviews across {total_pages} pages -> scraping")
    _next_page = urljoin(url, sel.css(".a-pagination .a-last>a::attr(href)").get())
    if _next_page:
        next_page_urls = [_next_page.replace("pageNumber=2", f"pageNumber={i}") for i in range(2, total_pages + 1)]
        assert len(set(next_page_urls)) == len(next_page_urls)
        other_pages = await asyncio.gather(*[session.get(url) for url in next_page_urls])
    else:
        other_pages = []
    reviews = []
    for response in [first_page, *other_pages]:
        reviews.extend(parse_reviews(response))
    log.info(f"scraped total {len(reviews)} reviews")
    return reviews


async def run():
    limits = httpx.Limits(max_connections=5)
    async with httpx.AsyncClient(limits=limits, timeout=httpx.Timeout(15.0), headers=BASE_HEADERS) as session:
        data = await scrape_reviews("B08QVPBFCS", session=session)

    print(json.dumps(data, indent=2))


# async def main():
#     print(1)

# https://stackoverflow.com/questions/55409641/asyncio-run-cannot-be-called-from-a-running-event-loop-when-using-jupyter-no
# https://ipython.readthedocs.io/en/stable/interactive/autoawait.html#difference-between-terminal-ipython-and-ipykernel
if __name__ == '__main__':

    asyncio.run(run())
