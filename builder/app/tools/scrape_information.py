import json
import time
from typing import Any, Optional
from urllib.parse import urljoin, urlparse, urlunparse

import requests
from bs4 import BeautifulSoup
from loguru import logger


def normalize_url(url: str) -> str:
    """Normalizes a URL to a consistent format to avoid duplicates.

    This process includes:
    - Making the scheme and netloc lowercase.
    - Removing URL fragments (#).
    - Removing trailing slashes from the path.

    Args:
        url: The URL string to normalize.

    Returns:
        The normalized URL string.
    """
    try:
        parsed = urlparse(url)

        # Standardize: lowercase scheme and netloc
        scheme = parsed.scheme.lower()
        netloc = parsed.netloc.lower()

        # Remove trailing slash from path, unless it's just "/"
        path = parsed.path.rstrip('/')
        if not path:
            path = '/'  # Handle the root case (e.g., "http://example.com")

        # Reconstruct URL without the fragment
        return urlunparse((scheme, netloc, path, parsed.params, parsed.query, ''))

    except Exception as e:
        logger.error(f"Could not normalize URL '{url}': {e}")
        return url  # Return original URL on unexpected error


def scrape_page_data(url: str) -> Optional[dict[str, Any]]:
    """Scrapes a single page and extracts structured data.

    Fetches the HTML for the given URL and parses it using BeautifulSoup
    to extract the title, meta description, headings, paragraphs,
    links, and images.

    Args:
        url: The URL of the page to scrape.

    Returns:
        A dictionary containing the structured scraped data, or None if
        the request or parsing fails.
    """
    # Define a user-agent header to mimic a browser, which is good practice
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }

    # --- Step 1: Fetch the Page ---
    try:
        # Make the HTTP GET request with a 10-second timeout
        response = requests.get(url, headers=headers, timeout=10)

        # Raise an HTTPError for bad responses (4xx or 5xx)
        response.raise_for_status()

    # --- Robust Error Handling for Requests ---
    except requests.exceptions.HTTPError as e:
        logger.error(f"HTTP error for {url}: {e}")
        return None
    except requests.exceptions.ConnectionError as e:
        logger.error(f"Connection error for {url}: {e}")
        return None
    except requests.exceptions.Timeout as e:
        logger.error(f"Timeout error for {url}: {e}")
        return None
    except requests.exceptions.RequestException as e:
        # Catch any other requests-related errors
        logger.error(f"Request error for {url}: {e}")
        return None

    # --- Step 2: Parse the HTML ---
    try:
        # Parse the HTML content
        soup = BeautifulSoup(response.text, 'html.parser')

        # Initialize the data structure to store results
        scraped_data = {
            "url": url,
            "title": None,
            "meta_description": None,
            "headings": {"h1": [], "h2": [], "h3": [], "h4": [], "h5": [], "h6": []},
            "paragraphs": [],
            "links": [],
            "images": []
        }

        # --- Step 3: Extract Data ---

        # Get Title
        if soup.title and soup.title.string:
            scraped_data["title"] = soup.title.string.strip()

        # Get Meta Description
        meta_desc = soup.find('meta', attrs={'name': 'description'})
        if meta_desc and meta_desc.get('content'):
            scraped_data["meta_description"] = meta_desc['content'].strip()

        # Get all Headings (h1-h6)
        for i in range(1, 7):
            tag_name = f'h{i}'
            for h in soup.find_all(tag_name):
                scraped_data["headings"][tag_name].append(h.get_text(strip=True))

        # Get all Paragraphs
        for p in soup.find_all('p'):
            text = p.get_text(strip=True)
            if text:  # Only add non-empty paragraphs
                scraped_data["paragraphs"].append(text)

        # Get all Links
        for a in soup.find_all('a', href=True):
            href = a['href']
            # Resolve relative URLs (e.g., "/about") to absolute URLs
            absolute_href = normalize_url(urljoin(url, href))
            link_text = a.get_text(strip=True)

            # Only add links that have text and a valid href
            if link_text and absolute_href:
                scraped_data["links"].append({
                    "text": link_text,
                    "href": absolute_href
                })

        # Get all Images
        for img in soup.find_all('img'):
            src = img.get('src')
            if src:
                # Resolve relative image URLs
                absolute_src = urljoin(url, src)
                scraped_data["images"].append({
                    "src": absolute_src,
                    "alt": img.get('alt', '').strip()  # Get alt text, default to empty string
                })

        return scraped_data

    except Exception as e:
        # Catch errors during BeautifulSoup parsing or data extraction
        logger.error(f"Error parsing HTML from {url}: {e}")
        return None


def scrape_information(start_url: str, limit: int = 10) -> list[dict[str, Any]]:
    """Crawls a website recursively up to a specified limit.

    Starts from the `start_url` and performs a breadth-first search (BFS)
    to find and scrape new pages. It only crawls pages on the same
    domain (netloc) as the `start_url`.

    Args:
        start_url: The URL to begin crawling.
        limit: The total number of pages to scrape.

    Returns:
        A list of dictionaries, where each dictionary is the
        scraped data from a single page.
    """

    # Ensure the starting URL is in our normalized format
    start_url = normalize_url(start_url)

    # --- Initialization ---
    urls_to_visit: list[str] = [start_url]  # A queue for BFS
    visited_urls: set[str] = set()  # A set for fast lookups of visited URLs
    all_scraped_data: list[dict[str, Any]] = []  # The final list of results
    page_count = 0

    # Get the "netloc" (e.g., 'books.toscrape.com') to stay on the same site
    try:
        base_netloc = urlparse(start_url).netloc
        if not base_netloc:
            logger.error(f"Invalid start URL: '{start_url}'. Could not determine domain.")
            return []
    except Exception as e:
        logger.error(f"Could not parse start URL '{start_url}': {e}")
        return []

    logger.info(f"Starting crawl at: {start_url}")
    logger.info(f"Staying on domain: {base_netloc}")
    logger.info(f"Scrape limit: {limit} pages")

    # --- Main Crawling Loop ---
    # Continue as long as there are URLs in the queue AND we haven't hit our limit
    while urls_to_visit and page_count < limit:

        try:
            # Get the next URL from the front of the queue
            current_url = urls_to_visit.pop(0)

            # --- Check 1: Have we already visited this URL? ---
            if current_url in visited_urls:
                continue

            # --- Check 2: Is this URL on the same domain? ---
            current_netloc = urlparse(current_url).netloc
            if current_netloc != base_netloc:
                logger.debug(f"Skipping external link: {current_url}")
                continue

            # --- Mark as visited *before* scraping to prevent re-queuing
            visited_urls.add(current_url)

            # --- Scrape the Page ---
            logger.info(f"[{page_count + 1}/{limit}] Scraping: {current_url}")
            page_data = scrape_page_data(current_url)

            if page_data:
                # Successfully scraped, add data to our list
                all_scraped_data.append(page_data)
                page_count += 1

                # --- Add new, valid links to the queue ---
                for link_info in page_data.get('links', []):
                    new_url = link_info['href']

                    # Check if it's new and on the same domain
                    if (new_url not in visited_urls and
                            new_url not in urls_to_visit and
                            urlparse(new_url).netloc == base_netloc):
                        urls_to_visit.append(new_url)
            else:
                # scrape_page_data failed and already logged the error
                logger.warning(f"Failed to scrape or parse {current_url}, moving on.")

            # --- Be polite: add a small delay to not overwhelm the server ---
            time.sleep(0.1)  # 100ms delay between requests

        except Exception as e:
            # Catch any unexpected errors during the loop
            logger.error(f"Unexpected error in crawl loop for {current_url}: {e}")
            continue  # Try to continue with the next URL

    logger.info(f"\nCrawl finished. Scraped {page_count} pages.")
    return all_scraped_data


# --- Example Usage ---
if __name__ == "__main__":
    # --- Scraper Configuration ---
    # 'books.toscrape.com' is a static site built for scraping practice
    START_URL = "https://books.toscrape.com"
    SCRAPE_LIMIT = 5

    # --- Run the Crawler ---
    try:
        crawled_data = scrape_information(START_URL, limit=SCRAPE_LIMIT)

        if crawled_data:
            # Convert the list of dictionaries to a JSON string
            json_output = json.dumps(crawled_data, indent=2)

            logger.success(f"{json_output}")

            # Uncomment to print the first page's data to console
            # print("\n--- First Page Data (Sample) ---")
            # print(json.dumps(crawled_data[0], indent=2))
        else:
            logger.warning("Crawling failed or no data was returned.")

    except Exception as e:
        logger.critical(f"A critical error occurred in the main execution: {e}")
