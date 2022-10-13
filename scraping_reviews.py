from typing import List, Optional, Dict, Any
import asyncio, json, httpx, math
from urllib.parse import urljoin
import pandas as pd
from loguru import logger as log
from parsel import Selector

BASE_HEADERS = {
    "accept-language": "en-US,en;q=0.9",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36",
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
    "accept-encoding": "gzip, deflate, br",
}


def parse_reviews(response):  # -> list[dict[str, bool | str | Any]]:
    """parse review from single review page"""
    sel = Selector(text=response.text)
    review_boxes = sel.css("#cm_cr-review_list div.review")
    parsed = []
    for box in review_boxes:
        parsed.append({
                "body": "".join(box.css("span[data-hook=review-body] ::text").getall()).strip(),
                "title": box.css("*[data-hook=review-title]>span::text").get(),
                "location": box.css("span[data-hook=review-date] ::text").get().split(" on")[0].replace("Reviewed in ", ""),
                "date": box.css("span[data-hook=review-date] ::text").get().split(" on")[1],
                "verified": bool(box.css("span[data-hook=avp-badge] ::text").get()),
                "star_rating": box.css("*[data-hook*=review-star-rating] ::text").re(r"(\d+\.*\d*) out")[0],
        })
    return parsed


async def scrape_reviews(asin, session: httpx.AsyncClient): #  -> list[dict[str, bool | str | Any]]:
    """scrape all reviews of a given ASIN of an amazon product"""
    url = f"https://www.amazon.com/product-reviews/{asin}/"
    # "https://www.amazon.com/Galanz-GLR16FS2K16-Refrigerator-Adjustable-Electrical/product-reviews/B08QVPBFCS/ref=cm_cr_dp_d_show_all_btm?ie=UTF8&reviewerType=all_reviews"
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


async def get_reviews(some_asin):
    limits = httpx.Limits(max_connections=5)
    async with httpx.AsyncClient(limits=limits, timeout=httpx.Timeout(15.0), headers=BASE_HEADERS) as session:
        data = await scrape_reviews(some_asin, session=session)
    return data

if __name__ == '__main__':
    product_asin = 'B08QVPBFCS'
    reviews_by_product = asyncio.run(get_reviews(product_asin))

    i = int(input("Enter the file number four the output: "))

    # write the data to json file
    with open(f'Data/json/product_reviews_{i}.json', 'w') as file:
        json.dump(reviews_by_product, file, indent=2)
    # write the data to Excel file
    df = pd.DataFrame(reviews_by_product, columns=['title', 'star_rating', 'verified', 'location', 'date', 'body'])
    df.to_excel(f"Data/xlsx/product_reviews{i}.xlsx", index=False)
