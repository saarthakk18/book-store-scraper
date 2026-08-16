"""
Book Store Scraper
-------------------
Scrapes book data (title, price, rating, availability, category)
from books.toscrape.com — a public sandbox site built for practicing
web scraping — and saves the results to a clean CSV file.

Author: Sarthak Ambi
"""

import csv
import time
import requests
from bs4 import BeautifulSoup

BASE_URL = "http://books.toscrape.com/catalogue/page-{}.html"
OUTPUT_FILE = "books_data.csv"

RATING_MAP = {
    "One": 1, "Two": 2, "Three": 3, "Four": 4, "Five": 5
}


def get_soup(url):
    """Fetch a page and return a BeautifulSoup object."""
    response = requests.get(url, timeout=10)
    response.raise_for_status()
    response.encoding = "utf-8"  # avoid mis-detected encoding breaking £ symbols
    return BeautifulSoup(response.text, "html.parser")


def parse_book(book_tag):
    """Extract structured data from a single book listing."""
    title = book_tag.h3.a["title"].strip()

    price_text = book_tag.find("p", class_="price_color").text
    price_clean = "".join(ch for ch in price_text if ch.isdigit() or ch == ".")
    price = float(price_clean)

    rating_class = book_tag.find("p", class_="star-rating")["class"]
    rating_word = [c for c in rating_class if c != "star-rating"][0]
    rating = RATING_MAP.get(rating_word, None)

    availability = book_tag.find("p", class_="instock availability").text.strip()

    return {
        "title": title,
        "price_gbp": price,
        "rating": rating,
        "availability": availability,
    }


def scrape_all_pages(max_pages=5):
    """Loop through paginated listing pages and collect all book data."""
    all_books = []

    for page_num in range(1, max_pages + 1):
        url = BASE_URL.format(page_num)
        print(f"Scraping page {page_num}: {url}")

        try:
            soup = get_soup(url)
        except requests.exceptions.HTTPError:
            print("No more pages found. Stopping.")
            break

        book_tags = soup.find_all("article", class_="product_pod")
        if not book_tags:
            break

        for book_tag in book_tags:
            all_books.append(parse_book(book_tag))

        time.sleep(1)  # polite delay between requests

    return all_books


def save_to_csv(data, filename):
    """Write scraped data to a CSV file."""
    if not data:
        print("No data to save.")
        return

    with open(filename, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=data[0].keys())
        writer.writeheader()
        writer.writerows(data)

    print(f"Saved {len(data)} records to {filename}")


if __name__ == "__main__":
    books = scrape_all_pages(max_pages=5)
    save_to_csv(books, OUTPUT_FILE)