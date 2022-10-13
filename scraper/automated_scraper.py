import re
import time
from main import *

# trial to automate the scraper
if __name__ == '__main__':
    search_keyword = 'Refrigerator'
    reviews_by_keyword_1 = asyncio.run(get_reviews_by_keyword(search_keyword))
    period = 3 # 7 * 24 * 60 * 60  # 7 days in seconds
    # initializing file suffix string
    i = '000000'
    j = 1
    while j != 2000000:
        # increasing the file suffix by one
        i = re.sub(r'[0-9]+$', lambda x: f"{str(int(x.group()) + 1).zfill(len(x.group()))}", i)
        print("Incremented numeric String : " + str(i))
        with open(f'Data/json/combined_results_{i}.json', 'r') as end_results_file:
            reviews_by_keyword = json.load(end_results_file)
        reviews_by_keyword_1 = asyncio.run(get_reviews_by_keyword(search_keyword))
        if reviews_by_keyword != reviews_by_keyword_1:
            reviews_by_keyword = reviews_by_keyword_1
            with open(f'Data/json/combined_results_{i}.json', 'w') as file:
                json.dump(reviews_by_keyword, file, indent=2)
            # write the data to Excel file
            df = pd.DataFrame(reviews_by_keyword,
                              columns=["search keyword", "Product_asin", "Product_title", "Product_url", "review_title",
                                       "review_rating", "review_verified", "review_location", "review_date",
                                       "review_body", ])
            df.to_excel(f"Data/xlsx/combined_results_{i}.xlsx", index=False)
            time.sleep(period)  # sleep for 7 days before rechecking the data
        j += 1
