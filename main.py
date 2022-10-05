import json
from scrap_search import *
from scraping_reviews_trial2 import *

# This is a draft of what is still needed it should be checked and fixed
# try to set sleep time for 7 days to run the scraper automatically and check the new results

# try to call the function from the scrape-search.py file to fetch the asin and pass it through a loop to the scrap review function
time = 7 * 24 * 60 * 60 # 7 days in seconds
for i in range(10):
    with open(f"query_results_{i}.json", "r") as query_file:
        search_results = json.load(query_file) # todo check here
    for item in search_results:
        asin = search_results["asin"]
        reviews = asyncio.run(get_review_details(asin))
    with open(f"query_results_{i+1}.json", "w") as review_file:
        json.dump(reviews, review_file) # todo check the writing process
