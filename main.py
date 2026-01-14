#!/usr/bin/env python3
"""CLI entry point for TheParking scraper."""

import argparse
import sys
import os

from scraper import TheParkingScraper


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Scrape car listings from TheParking.eu",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py volkswagen --api-key YOUR_KEY
  python main.py volkswagen golf --api-key YOUR_KEY -p 2
  python main.py bmw serie-3 --api-key YOUR_KEY --format json
  python main.py --api-key YOUR_KEY -p 3
        """,
    )

    parser.add_argument(
        "make",
        nargs="?",
        default=None,
        help="Car make (e.g., volkswagen, bmw, mercedes)",
    )

    parser.add_argument(
        "model",
        nargs="?",
        default=None,
        help="Car model (e.g., golf, serie-3, classe-c)",
    )

    parser.add_argument(
        "-p", "--pages",
        type=int,
        default=1,
        help="Number of pages to scrape (default: 1)",
    )

    parser.add_argument(
        "--api-key",
        default=os.environ.get("SCRAPINGANT_API_KEY"),
        help="ScrapingAnt API key (or set SCRAPINGANT_API_KEY env var)",
    )

    parser.add_argument(
        "--format",
        choices=["csv", "json"],
        default="csv",
        help="Output format (default: csv)",
    )

    args = parser.parse_args()

    if not args.api_key:
        print("Error: API key required. Use --api-key or set SCRAPINGANT_API_KEY env var")
        sys.exit(1)

    scraper = TheParkingScraper(args.api_key)
    collection = scraper.scrape(
        make=args.make,
        model=args.model,
        pages=args.pages,
        output_format=args.format,
    )

    print(f"\nScraped {len(collection)} listings")

    if collection.listings:
        print("\nSample listing:")
        sample = collection.listings[0]
        print(f"  Title: {sample.title}")
        print(f"  Make: {sample.make}")
        print(f"  Model: {sample.model}")
        print(f"  Price: {sample.price}")
        print(f"  Year: {sample.year}")
        print(f"  Mileage: {sample.mileage}")
        print(f"  URL: {sample.detail_url}")


if __name__ == "__main__":
    main()
