"""Data models for TheParking scraper."""

from dataclasses import dataclass, field, asdict
from typing import Optional, List
from datetime import datetime


@dataclass
class CarListing:
    """Represents a car listing from TheParking."""

    title: str
    make: Optional[str] = None
    model: Optional[str] = None
    trim: Optional[str] = None
    price: Optional[str] = None
    year: Optional[str] = None
    mileage: Optional[str] = None
    fuel_type: Optional[str] = None
    listing_id: Optional[str] = None
    detail_url: Optional[str] = None
    image_url: Optional[str] = None
    photo_count: Optional[str] = None
    is_dealer: bool = False
    scraped_at: str = field(default_factory=lambda: datetime.now().isoformat())

    def to_dict(self) -> dict:
        """Convert listing to dictionary."""
        return asdict(self)


@dataclass
class ListingCollection:
    """Collection of car listings with deduplication."""

    listings: List[CarListing] = field(default_factory=list)
    seen_ids: set = field(default_factory=set)

    def add(self, listing: CarListing) -> bool:
        """Add listing if not duplicate. Returns True if added."""
        if listing.listing_id and listing.listing_id in self.seen_ids:
            return False

        if listing.listing_id:
            self.seen_ids.add(listing.listing_id)

        self.listings.append(listing)
        return True

    def add_many(self, listings: List[CarListing]) -> int:
        """Add multiple listings. Returns count of new listings added."""
        added = 0
        for listing in listings:
            if self.add(listing):
                added += 1
        return added

    def to_dicts(self) -> List[dict]:
        """Convert all listings to dictionaries."""
        return [listing.to_dict() for listing in self.listings]

    def __len__(self) -> int:
        return len(self.listings)
