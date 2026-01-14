"""TheParking scraper using ScrapingAnt API."""

import json
import csv
import os
import re
from datetime import datetime
from typing import List, Optional

import requests
from bs4 import BeautifulSoup

from config import (
    SCRAPINGANT_API_URL,
    BASE_URL,
    DEFAULT_TIMEOUT,
    BROWSER_RENDERING,
    OUTPUT_DIR,
    CSV_FILENAME_TEMPLATE,
    JSON_FILENAME_TEMPLATE,
)
from models import CarListing, ListingCollection
from utils import (
    build_search_url,
    build_full_url,
    extract_listing_id,
    parse_price,
    parse_mileage,
    parse_year,
    clean_text,
    extract_fuel_type,
)


class TheParkingScraper:
    """Scraper for TheParking.eu car listings."""

    def __init__(self, api_key: str):
        """Initialize scraper with ScrapingAnt API key."""
        self.api_key = api_key
        self.collection = ListingCollection()

    def _make_request(self, url: str) -> Optional[str]:
        """Make request through ScrapingAnt API."""
        params = {
            "url": url,
            "x-api-key": self.api_key,
            "browser": str(BROWSER_RENDERING).lower(),
        }

        try:
            response = requests.get(
                SCRAPINGANT_API_URL,
                params=params,
                timeout=DEFAULT_TIMEOUT,
            )
            response.raise_for_status()
            return response.text
        except requests.RequestException as e:
            print(f"Request error for {url}: {e}")
            return None

    def _parse_listings(self, html: str) -> List[CarListing]:
        """Parse car listings from HTML."""
        soup = BeautifulSoup(html, "html.parser")
        listings = []

        # Find all listing items - they're in list items with links to /tools/
        # Look for all links that contain /tools/ which are detail links
        detail_links = soup.find_all("a", href=re.compile(r'/tools/[A-Z0-9]+/'))

        # Group by listing ID to avoid duplicates within parsing
        seen_ids = set()
        processed_elements = set()

        for link in detail_links:
            href = link.get("href", "")
            listing_id = extract_listing_id(href)

            if not listing_id or listing_id in seen_ids:
                continue

            # Find the parent container that holds all listing info
            # Navigate up to find the listitem or container element
            container = link
            for _ in range(10):  # Go up max 10 levels
                parent = container.parent
                if parent is None:
                    break
                if parent.name == "li" or (parent.name == "div" and "item" in str(parent.get("class", []))):
                    container = parent
                    break
                container = parent

            # Skip if we've already processed this container
            container_id = id(container)
            if container_id in processed_elements:
                continue
            processed_elements.add(container_id)

            try:
                listing = self._parse_listing_container(container, listing_id, href)
                if listing:
                    seen_ids.add(listing_id)
                    listings.append(listing)
            except Exception as e:
                print(f"Error parsing listing {listing_id}: {e}")
                continue

        return listings

    def _parse_listing_container(self, container, listing_id: str, detail_href: str) -> Optional[CarListing]:
        """Parse a single listing container into CarListing."""
        detail_url = build_full_url(detail_href)

        # Get title from h2 or link text
        title = ""
        make = None
        model = None
        trim = None

        h2 = container.find("h2")
        if h2:
            title = clean_text(h2.get_text())
            # Remove "See the listing" suffix if present
            title = re.sub(r'\s*See the listing\s*$', '', title, flags=re.IGNORECASE)
            # Try to extract make/model/trim from spans
            spans = h2.find_all("span")
            if len(spans) >= 1:
                make = clean_text(spans[0].get_text())
            if len(spans) >= 2:
                model = clean_text(spans[1].get_text())
            if len(spans) >= 3:
                trim = clean_text(spans[2].get_text())

        if not title:
            # Try getting from link text
            title_link = container.find("a", href=re.compile(r'/tools/'))
            if title_link:
                title = clean_text(title_link.get_text())
                # Remove "See the listing" suffix if present
                title = re.sub(r'\s*See the listing\s*$', '', title, flags=re.IGNORECASE)

        # Get price - look for text containing € symbol
        price = None
        price_elem = container.find(string=re.compile(r'[\d,.\s]+\s*€'))
        if price_elem:
            price = parse_price(price_elem)
        else:
            # Try finding in any element
            for elem in container.find_all(True):
                text = elem.get_text()
                if '€' in text and re.search(r'\d', text):
                    price = parse_price(text)
                    if price:
                        break

        # Get specs from text content
        year = None
        mileage = None
        fuel_type = None

        # Look through all text strings in container
        for string in container.stripped_strings:
            text = clean_text(string)
            if not text:
                continue

            # Year - look for 4-digit year in quotes
            if not year and re.match(r'^"?20[0-2]\d"?$', text):
                year = parse_year(text)

            # Mileage - pattern like "49,693 Km"
            if not mileage and re.search(r'[\d,]+\s*[Kk]m$', text):
                mileage = parse_mileage(text)

            # Fuel type
            if not fuel_type:
                fuel = extract_fuel_type(text)
                if fuel:
                    fuel_type = fuel

        # Check for dealer indicator
        is_dealer = bool(container.find(string=re.compile(r'Dealer', re.IGNORECASE)))

        # Get image URL
        image_url = None
        img = container.find("img")
        if img:
            image_url = img.get("src") or img.get("data-src")
            if image_url and not image_url.startswith("http"):
                image_url = build_full_url(image_url)

        # Get photo count
        photo_count = None
        photo_elem = container.find(string=re.compile(r'^\d+$'))
        if photo_elem:
            # Check if it's near a camera icon
            parent = photo_elem.parent
            if parent and "camera" in str(parent).lower():
                photo_count = clean_text(photo_elem)

        return CarListing(
            title=title,
            make=make,
            model=model,
            trim=trim,
            price=price,
            year=year,
            mileage=mileage,
            fuel_type=fuel_type,
            listing_id=listing_id,
            detail_url=detail_url,
            image_url=image_url,
            photo_count=photo_count,
            is_dealer=is_dealer,
        )

    def scrape(
        self,
        make: Optional[str] = None,
        model: Optional[str] = None,
        pages: int = 1,
        output_format: str = "csv",
    ) -> ListingCollection:
        """Scrape car listings.

        Args:
            make: Car make (e.g., "volkswagen")
            model: Car model (e.g., "golf")
            pages: Number of pages to scrape
            output_format: Output format ("csv" or "json")

        Returns:
            ListingCollection with all scraped listings
        """
        search_term = f"{make or 'all'}" + (f"-{model}" if model else "")
        print(f"Starting scrape: {search_term}, pages={pages}")

        for page in range(1, pages + 1):
            url = build_search_url(make, model, page)
            print(f"Scraping page {page}: {url}")

            html = self._make_request(url)
            if not html:
                print(f"Failed to fetch page {page}")
                continue

            listings = self._parse_listings(html)
            added = self.collection.add_many(listings)
            print(f"Page {page}: Found {len(listings)} listings, {added} new")

        # Save results
        if len(self.collection) > 0:
            self._save_results(search_term, output_format)

        print(f"Total: {len(self.collection)} unique listings")
        return self.collection

    def _save_results(self, search_term: str, output_format: str):
        """Save scraped results to file."""
        os.makedirs(OUTPUT_DIR, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        if output_format == "json":
            filename = JSON_FILENAME_TEMPLATE.format(
                keyword=search_term.replace(" ", "_"),
                timestamp=timestamp,
            )
            filepath = os.path.join(OUTPUT_DIR, filename)

            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(self.collection.to_dicts(), f, ensure_ascii=False, indent=2)
        else:
            filename = CSV_FILENAME_TEMPLATE.format(
                keyword=search_term.replace(" ", "_"),
                timestamp=timestamp,
            )
            filepath = os.path.join(OUTPUT_DIR, filename)

            if self.collection.listings:
                fieldnames = list(self.collection.listings[0].to_dict().keys())

                with open(filepath, "w", newline="", encoding="utf-8") as f:
                    writer = csv.DictWriter(f, fieldnames=fieldnames)
                    writer.writeheader()
                    writer.writerows(self.collection.to_dicts())

        print(f"Saved results to {filepath}")
