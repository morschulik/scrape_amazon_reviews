# scrape amazon search results
To analyze the reviews of some products on amazon we need the ASIN of the product.

The URL of a search list after giving the search keyword (query) has the form:
`url=f"https://www.amazon.com/s?k={query}&page={page}"`

The URL of every product will have the form:
`url = f"https://www.amazon.com/{Optional_part}/dp/{asin}/"`

And the URL of the reviews is 
`url = f"https://www.amazon.com/product-reviews/{asin}/"`

So we need the asin of an object to scrap its review
We will have 3 search queries to test the search results of those products.

The scraper for the search results is in `scrap_search.py`
(Its explanation and comments on it can be found in the Jupiter notebook `scrap_search.ipynb`)
The scraper of the reviews is in the file `scrap_reviews.py` it scrapes the reviews of one product and is explained in the notebook.
In the `main.py` file we connect them together to scrape the reviews of all possible many products.

The results data can be found in the `data` folder
# scrape_amazon_reviews
the aim is to get reviews from amazon, it is interesting to analyze such with NLP.\n This is a student project within the ReDI School Data Circle program.

## Installation

you need to [create and activate your virtual environment](https://realpython.com/python-virtual-environments-a-primer/) and inside it, you need to run
```bash
pip install -r requirements.txt
```

## Usage

Scrapes all pages reviews by product searched 

## Contributing
Please open an issue first to discuss what you would like to change.
