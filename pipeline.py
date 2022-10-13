from typing_extensions import TypedDict

# store the data in classes to be able to send it to a database, but we can create the database directly
# from the json file

class SearchData(TypedDict):
    pass


class ProductReviewData(TypedDict):
    """storage type hint for amazons review object"""
    title: str
    text: str
    location_and_date: str
    verified: bool
    rating: float


class ReviewsByKeyword(TypedDict):
    pass