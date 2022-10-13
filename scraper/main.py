from scrap_search import search
from scrap_reviews import *

# combine the scrap_search and the scrap_reviews


async def get_reviews_by_keyword(keyword):
    limits = httpx.Limits(max_connections=5)
    async with httpx.AsyncClient(limits=limits, timeout=httpx.Timeout(20.0), headers=BASE_HEADERS) as session:

        products_list = await search(keyword, session=session)
        # asins_list = [product["asin"] for product in products_list]
        end_results_list = []
        for product in products_list:
            product_reviews = await scrape_reviews(product["asin"], session=session)
            for review in product_reviews:
                end_results = {
                    "search keyword": keyword,
                    "Product_asin": product["asin"],
                    "Product_title": product["title"],
                    "Product_url": product["url"],
                    "review_title": review["title"],
                    "review_rating": review["star_rating"],
                    "review_verified": review["verified"],
                    "review_location": review["location"],
                    "review_date": review["date"],
                    "review_body": review["body"],
                }
                end_results_list.append(end_results)
    return end_results_list


if __name__ == '__main__':
    # pass
    search_keyword = 'Refrigerator'
    search_query = search_keyword.replace(' ', '+')
    reviews_by_keyword = asyncio.run(get_reviews_by_keyword(search_query))
    i = int(input("Enter the file number four the output: "))

    # write the data to json file
    with open(f'Data/json/combined_results_{i}.json', 'w') as file:
        json.dump(reviews_by_keyword, file, indent=2)
    # write the data to Excel file
    df = pd.DataFrame(reviews_by_keyword,
                      columns=["search keyword", "Product_asin", "Product_title", "Product_url", "review_title",
                               "review_rating", "review_verified", "review_location", "review_date", "review_body", ])
    df.to_excel(f"Data/xlsx/combined_results_{i}.xlsx", index=False)

