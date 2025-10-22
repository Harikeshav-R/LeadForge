import time
from typing import Set, List, Optional
from urllib.parse import urljoin, urlparse, urlunparse

import requests
from bs4 import BeautifulSoup
from langchain.tools import tool
from loguru import logger
from pydantic import ValidationError

from app.schemas import PageScrapedData, InformationScraperInput, InformationScraperOutput


class WebsiteScraper:
    """
    A class to encapsulate the website crawling and scraping logic.

    Attributes:
        start_url (str): The initial URL to begin the crawl.
        limit (int): The maximum number of pages to scrape.
        base_netloc (str): The domain name (netloc) of the start_url, used
                           to ensure the crawler stays on the same site.
        urls_to_visit (List[str]): A queue of URLs to be scraped.
        visited_urls (Set[str]): A set of URLs that have already been visited.
        all_scraped_data (List[PageScrapedData]): A list of validated
                                                  data from all scraped pages.
    """

    def __init__(self, start_url: str, limit: int = 10):
        """
        Initializes the WebsiteScraper.

        Args:
            start_url: The URL to begin crawling.
            limit: The total number of pages to scrape.
        """
        self.start_url = self.normalize_url(start_url)
        self.limit = limit

        # Get the "netloc" (e.g., 'books.toscrape.com') to stay on the same site
        try:
            self.base_netloc = urlparse(self.start_url).netloc
            if not self.base_netloc:
                raise ValueError(f"Invalid start URL: '{start_url}'. Could not determine domain.")
        except Exception as e:
            logger.error(f"Could not parse start URL '{start_url}': {e}")
            raise  # Re-raise the exception to stop initialization

        # --- Crawler State ---
        self.urls_to_visit: List[str] = [self.start_url]
        self.visited_urls: Set[str] = set()
        self.all_scraped_data: List[PageScrapedData] = []

        logger.info(f"Scraper initialized for: {self.start_url}")
        logger.info(f"Staying on domain: {self.base_netloc}")
        logger.info(f"Scrape limit: {self.limit} pages")

    @staticmethod
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

    def scrape_page_data(self, url: str) -> Optional[PageScrapedData]:
        """Scrapes a single page and returns validated Pydantic model.

        Fetches the HTML for the given URL, parses it, extracts data,
        and validates it against the PageData schema.

        Args:
            url: The URL of the page to scrape.

        Returns:
            A validated PageData object, or None if the request,
            parsing, or validation fails.
        """
        # Define a user-agent header to mimic a browser, which is good practice
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/5.37.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
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

            # Initialize a plain dictionary to hold raw data
            page_dict_data = {}

            # --- Step 3: Extract Data into the Dictionary ---

            # Get URL (from the input arg, as it's the reliable source)
            page_dict_data["url"] = url

            # Get Title
            page_dict_data["title"] = soup.title.string.strip() if soup.title and soup.title.string else None

            # Get Meta Description
            meta_desc = soup.find('meta', attrs={'name': 'description'})
            page_dict_data["meta_description"] = meta_desc['content'].strip() if meta_desc and meta_desc.get(
                'content') else None

            # Get all Headings (h1-h6)
            page_dict_data["headings"] = {
                f'h{i}': [h.get_text(strip=True) for h in soup.find_all(f'h{i}')]
                for i in range(1, 7)
            }

            # Get all Paragraphs
            page_dict_data["paragraphs"] = [p.get_text(strip=True) for p in soup.find_all('p') if
                                            p.get_text(strip=True)]

            # Get all Links
            links_data = []
            for a in soup.find_all('a', href=True):
                href = a['href']
                # Resolve relative URLs (e.g., "/about") to absolute URLs
                absolute_href = self.normalize_url(urljoin(url, href))
                link_text = a.get_text(strip=True)

                # Only add links that have text and a valid href
                if link_text and absolute_href:
                    links_data.append({
                        "text": link_text,
                        "href": absolute_href
                    })
            page_dict_data["links"] = links_data

            # Get all Images
            images_data = []
            for img in soup.find_all('img'):
                src = img.get('src')
                if src:
                    # Resolve relative image URLs
                    absolute_src = urljoin(url, src)
                    images_data.append({
                        "src": absolute_src,
                        "alt": img.get('alt', '').strip()  # Get alt text, default to empty string
                    })
            page_dict_data["images"] = images_data

            # --- Step 4: Validate and Instantiate Pydantic Model ---
            try:
                validated_page_data = PageScrapedData(**page_dict_data)
                return validated_page_data
            except ValidationError as e:
                # Log validation errors (e.g., invalid URL format)
                logger.error(f"Pydantic validation error for {url}: {e}")
                return None

        except Exception as e:
            # Catch errors during BeautifulSoup parsing or data extraction
            logger.error(f"Error parsing HTML from {url}: {e}")
            return None

    def crawl(self) -> InformationScraperOutput:
        """Crawls a website recursively up to the instance's limit.

        Performs a breadth-first search (BFS) starting from the instance's
        `start_url`.

        Returns:
            An InformationScraperOutput Pydantic object containing a list of
            all successfully scraped and validated PageData objects.
        """

        page_count = 0

        # --- Main Crawling Loop ---
        # Continue as long as there are URLs in the queue AND we haven't hit our limit
        while self.urls_to_visit and page_count < self.limit:

            try:
                # Get the next URL from the front of the queue
                current_url = self.urls_to_visit.pop(0)

                # --- Check 1: Have we already visited this URL? ---
                if current_url in self.visited_urls:
                    continue

                # --- Check 2: Is this URL on the same domain? ---
                current_netloc = urlparse(current_url).netloc
                if current_netloc != self.base_netloc:
                    # logger.debug(f"Skipping external link: {current_url}")
                    continue

                # --- Mark as visited *before* scraping to prevent re-queuing
                self.visited_urls.add(current_url)

                # --- Scrape the Page ---
                logger.info(f"[{page_count + 1}/{self.limit}] Scraping: {current_url}")
                page_data = self.scrape_page_data(current_url)

                if page_data:
                    # Successfully scraped and validated, add Pydantic object to our list
                    self.all_scraped_data.append(page_data)
                    page_count += 1

                    # --- Add new, valid links to the queue ---
                    # We can safely use .links here because page_data is a validated Pydantic model
                    for link_info in page_data.links:
                        new_url = str(link_info.href)  # Convert Pydantic URL back to string

                        # Check if it's new and on the same domain
                        if (new_url not in self.visited_urls and
                                new_url not in self.urls_to_visit and
                                urlparse(new_url).netloc == self.base_netloc):
                            self.urls_to_visit.append(new_url)
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
        # Return the final list wrapped in our InformationScraperOutput model
        return InformationScraperOutput(pages=self.all_scraped_data)


@tool(args_schema=InformationScraperInput)
def information_scraper(url: str, limit: int = 10) -> InformationScraperOutput:
    """
    Initializes and runs a new WebsiteScraper instance.

    This is the main entry point function to start a crawl.

    Args:
        url: The URL to begin crawling.
        limit: The total number of pages to scrape.

    Returns:
        An InformationScraperOutput object with the results of the crawl.
    """
    try:
        scraper = WebsiteScraper(start_url=url, limit=limit)
        results = scraper.crawl()
        return results
    except ValueError as e:
        logger.critical(f"Failed to initialize scraper: {e}")
        return InformationScraperOutput(pages=[])  # Return empty result on init failure
    except Exception as e:
        logger.critical(f"An unexpected error occurred during the crawl: {e}")
        return InformationScraperOutput(pages=[])  # Return empty result


# --- Example Usage ---
if __name__ == "__main__":
    # --- Scraper Configuration ---
    # 'books.toscrape.com' is a static site built for scraping practice
    START_URL = "http://books.toscrape.com"
    SCRAPE_LIMIT = 5

    # --- Run the Scraper using the global function ---
    logger.info("--- Starting Scraper ---")
    crawled_data = information_scraper.invoke(InformationScraperInput(url=START_URL, limit=SCRAPE_LIMIT).model_dump())

    if crawled_data.pages:
        # Convert the Pydantic model to a JSON string
        json_output = crawled_data.model_dump_json(indent=2)

        # Save the JSON to a file
        output_filename = "crawled_website_data.json"
        try:
            with open(output_filename, 'w', encoding='utf-8') as f:
                f.write(json_output)
            logger.info(f"Successfully saved all data to {output_filename}")
        except IOError as e:
            logger.error(f"Failed to write output file: {e}")

    else:
        logger.warning("Crawling finished, but no data was returned.")

    logger.info("--- Scraper Finished ---")
