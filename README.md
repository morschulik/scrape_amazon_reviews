# scrape amazon search results
To analyze the reviews of some products on amazon we need the ASIN of the product.

The URL of a search list after giving the search keyword (query) has the form:
`url=f"https://www.amazon.com/s?k={query}&page={page}"`

The URL of every product will have the form:
`url = f"https://www.amazon.com/{Optional_part}/dp/{asin}/"`

And the URL of the reviews is 
`url = f"https://www.amazon.com/product-reviews/{asin}/"`

So we need the asin of an object to scrap its review
We will have 3 search queries to produce a list of search results of those products with their reviews
The scraper for the search results is in `scrap_search.py`
(Its explanation and comments on it can be found in the Jupiter notebook `scrap_search.ipynb`)
The scraper of the reviews is in the file `scraping_reviews.py` it scrapes the reviews of one product and is explained in the notebook.
In the `main.py` file we connect them together to crape the reviews of all possible many products
The `Fullscraper.py` file should be used if the other codes get blocked from amazon. It contains an API key from [Scrapfly](https://scrapfly.io/blog/how-to-scrape-amazon/) to overcome the scrape blocking
The data can be found in the `data` folder
# scrape_amazon_reviews
To get reviews from amazon is interesting to analyze such with NLP.\n This is a student project within the ReDI School Data Circle program.

## Installation

```bash
pip install -r requirements.txt
```

## Usage

Scrapes all pages reviews by product searched 

## Contributing
Please open an issue first to discuss what you would like to change.
