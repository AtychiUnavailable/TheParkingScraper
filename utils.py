"""Utility functions for TheParking scraper."""

import re
from typing import Optional
from urllib.parse import urljoin

from config import BASE_URL, LISTINGS_URL


def build_search_url(make: Optional[str] = None, model: Optional[str] = None, page: int = 1) -> str:
    """Build search URL with optional make/model and pagination."""
    if make and model:
        url = f"{LISTINGS_URL}/{make.lower()}-{model.lower()}.html"
    elif make:
        url = f"{LISTINGS_URL}/{make.lower()}.html"
    else:
        url = f"{LISTINGS_URL}/"

    if page > 1:
        url = f"{url}?page={page}"

    return url


def build_full_url(path: str) -> str:
    """Build full URL from relative path."""
    if path.startswith("http"):
        return path
    return urljoin(BASE_URL, path)


def extract_listing_id(url: str) -> Optional[str]:
    """Extract listing ID from detail URL.

    URL pattern: /tools/MENYRBAM/0/P/PL.html
    """
    match = re.search(r'/tools/([A-Z0-9]+)/', url)
    if match:
        return match.group(1)
    return None


def parse_price(text: str) -> Optional[str]:
    """Parse and clean price text."""
    if not text:
        return None

    # Remove extra whitespace
    text = " ".join(text.split())

    # Look for price pattern with euro symbol
    match = re.search(r'[\d,.\s]+\s*€', text)
    if match:
        return match.group(0).strip()

    return text.strip() if text.strip() else None


def parse_mileage(text: str) -> Optional[str]:
    """Parse mileage text."""
    if not text:
        return None

    # Look for pattern like "49,693 Km" or "49693 km"
    match = re.search(r'[\d,.\s]+\s*[Kk]m', text)
    if match:
        return match.group(0).strip()

    return None


def parse_year(text: str) -> Optional[str]:
    """Extract year from text."""
    if not text:
        return None

    # Look for 4-digit year in quotes or standalone (2000-2029)
    match = re.search(r'"?(20[0-2]\d)"?', text)
    if match:
        return match.group(1)

    # Also try 19xx years for older cars
    match = re.search(r'"?(19[89]\d)"?', text)
    if match:
        return match.group(1)

    return None


def clean_text(text: str) -> str:
    """Clean and normalize text."""
    if not text:
        return ""

    # Remove extra whitespace and newlines
    text = " ".join(text.split())
    return text.strip()


def extract_fuel_type(text: str) -> Optional[str]:
    """Extract fuel type from text."""
    if not text:
        return None

    text_lower = text.lower()

    fuel_types = {
        'gasoline': 'Gasoline',
        'petrol': 'Gasoline',
        'diesel': 'Diesel',
        'electric': 'Electric',
        'hybrid': 'Hybrid',
        'lpg': 'LPG',
        'cng': 'CNG',
        'hydrogen': 'Hydrogen',
    }

    for key, value in fuel_types.items():
        if key in text_lower:
            return value

    # Return original if it looks like a fuel type
    if text in ['Gasoline', 'Diesel', 'Electric', 'Hybrid', 'LPG', 'CNG']:
        return text

    return None
