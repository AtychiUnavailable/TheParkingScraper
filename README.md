# TheParking Scraper

A Python scraper for [TheParking.eu](https://www.theparking.eu) car listings using [ScrapingAnt](https://scrapingant.com/) API.

> **Note**: The ScrapingAnt free plan has concurrency limited to 1 thread.

## Features

- Scrapes car listings from TheParking.eu (European car search engine)
- Aggregates listings from 900+ registered car websites
- Supports pagination for bulk data collection
- Filter by make and model
- Exports to CSV or JSON format
- Automatic deduplication of listings

## Scraped Fields

| Field | Description |
|-------|-------------|
| title | Full listing title |
| make | Car manufacturer |
| model | Car model |
| trim | Trim level/variant |
| price | Listed price in EUR |
| year | Vehicle year |
| mileage | Odometer reading |
| fuel_type | Fuel type (Gasoline, Diesel, etc.) |
| listing_id | Unique listing identifier |
| detail_url | Full URL to listing detail page |
| image_url | Main listing image URL |
| photo_count | Number of photos available |
| is_dealer | Whether listing is from a dealer |
| scraped_at | Timestamp of scrape |

## Installation

```bash
pip install -r requirements.txt
```

## Usage

```bash
# Scrape Volkswagen listings (1 page)
python main.py volkswagen --api-key YOUR_SCRAPINGANT_API_KEY

# Scrape specific model
python main.py volkswagen golf --api-key YOUR_SCRAPINGANT_API_KEY

# Scrape multiple pages
python main.py bmw --api-key YOUR_SCRAPINGANT_API_KEY -p 3

# Export as JSON
python main.py mercedes classe-c --api-key YOUR_SCRAPINGANT_API_KEY --format json

# Using environment variable
export SCRAPINGANT_API_KEY=your_key_here
python main.py audi -p 2
```

## Output

Results are saved to the `output/` directory:
- CSV: `theparking_{search}_{timestamp}.csv`
- JSON: `theparking_{search}_{timestamp}.json`

## Supported Makes

TheParking aggregates listings for all major car manufacturers including:
- Volkswagen, BMW, Mercedes, Audi, Opel
- Renault, Peugeot, Citroën, Ford, Fiat
- Toyota, Honda, Mazda, Nissan, Hyundai
- And many more...

## Requirements

- Python 3.7+
- ScrapingAnt API key ([Get one here](https://scrapingant.com/))

## License

MIT
