import httpx
import requests
import asyncio
import json
import pandas as pd
from parsel import Selector
from loguru import logger as log
from urllib.parse import urljoin

search_query_1 = 'Refrigerator'.replace(' ', '+')
search_query_2 = 't-shirt women'.replace(' ', '+')  # --> 't-shirt+women'
search_query_3 = 'lego'.replace(' ', '+')  # --> 't-shirt+women'
query_list = [search_query_1, search_query_2, search_query_3]
HEADERS = {
    "accept-language": "en-US,en;q=0.9",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36",
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
    "accept-encoding": "gzip, deflate, br",
}


def parse_search(resp):
    """Parse search result page for product previews"""
    previews = []
    sel = Selector(text=resp.text)
    product_boxes = sel.css("div.s-result-item[data-component-type=s-search-result]")
    for box in product_boxes:
        # get the url of every search item in the search result
        url = urljoin(str(resp.url), box.css("h2>a::attr(href)").get()).split("?")[0]
        if len(urljoin(str(resp.url), box.css("h2>a::attr(href)").get()).split(
                "/")) != 6 and "/slredirect/" not in url and "sspa" not in url:  # skip ads etc.
            previews.append(
                {
                    "url": url,
                    "title": box.css("h2>a>span::text").get(),
                }
            )
    log.debug(f"found {len(previews)} product listings in {resp.url}")  # formulates the summery and debug log report
    return previews


async def search(query, session):
    log.info(f"{query}: scraping the first page")
    search_url = f"https://www.amazon.com/s?k={query}&page=1"
    first_page = requests.get(search_url, headers=HEADERS)
    sel = Selector(text=first_page.text)
    last_page = sel.xpath('//span[has-class("s-pagination-disabled")][not(has-class("s-pagination-previous"))]/text()')
    total_pages = int(last_page.getall()[0])  # the wrong solution was max(int(number) for number in _page_numbers)
    log.info(f"{query}: found {total_pages} pages, scraping them concurrently")
    other_pages = await asyncio.gather(*[session.get(f"https://www.amazon.com/s?k={query}&page={page}") for page in range(2, total_pages + 1)])
    previews = []
    for response in [first_page, *other_pages]:
        previews.extend(parse_search(response))

    log.info(f"{query}: found total of {len(previews)} product previews")
    return previews


# write the data to some json or Excel file
async def get_product_search_list(query):
    limits = httpx.Limits(max_connections=5)
    async with httpx.AsyncClient(limits=limits, timeout=httpx.Timeout(15.5), headers=HEADERS) as session:
        data = await search(query, session=session)
        for item in data:
            item["item_name"] = query
            item["acin"] = item["url"].split('/')[5]
    return data

if __name__ == '__main__':
    results = []
    for query in query_list:
        data = asyncio.run(get_product_search_list(query))
        results.append(data)

    i = int(input("Enter the file number four the output: "))
    
    with open(f'Data/json/query_results_{i}.json', 'w') as file:
        json.dump(results, file, indent=2)

    # todo check why we can not write through panda dataframe after I try to loop over the query list and how to fix it
    # with open(f'/Data/query_results_{i}.json', 'r') as f:
    #     results =json.load(f)
    # df = pd.DataFrame(results, columns=['item_name', 'acin', 'title', 'url'])
    # df.to_excel(f"query_results_{i}.xlsx", index=False)



