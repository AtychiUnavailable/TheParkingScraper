"""Configuration for TheParking scraper."""

# ScrapingAnt API
SCRAPINGANT_API_URL = "https://api.scrapingant.com/v2/general"

# TheParking URLs
BASE_URL = "https://www.theparking.eu"
LISTINGS_URL = f"{BASE_URL}/used-cars"

# Request settings
DEFAULT_TIMEOUT = 60
BROWSER_RENDERING = True

# CSS Selectors
SELECTORS = {
    # Listing container - each listing is in a listitem within the main list
    "listings_container": "ul.resultats",
    "listing_items": "ul.resultats > li",

    # Alternative selector for listing items
    "listing_items_alt": ".resultats li.item_car",

    # Link to detail page (contains listing ID like /tools/MENYRBAM/)
    "detail_link": "a[href*='/tools/']",

    # Title elements
    "title": "h2",
    "make": "h2 span:first-child",
    "model": "h2 span:nth-child(2)",
    "trim": "h2 span:nth-child(3)",

    # Price
    "price": ".prix, .price",

    # Specs list
    "specs_list": "ul.attributes li, ul li",

    # Image
    "image": "img[src*='theparking'], img[data-src*='theparking']",

    # Photo count
    "photo_count": ".nb_photos, .camera_icon + span",
}

# Output settings
OUTPUT_DIR = "output"
CSV_FILENAME_TEMPLATE = "theparking_{keyword}_{timestamp}.csv"
JSON_FILENAME_TEMPLATE = "theparking_{keyword}_{timestamp}.json"
