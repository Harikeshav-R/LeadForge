import re
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup
from langchain_core.tools import tool
from loguru import logger

from app.schemas import ContactScraperOutput, ContactScraperInput


class WebsiteUnreachableError(Exception):
    """Custom exception for when a website cannot be reached."""
    pass


class ScrapingError(Exception):
    """Custom exception for errors that occur during scraping."""
    pass


class GlobalTimeoutLimitReached(Exception):
    """Custom exception for when the global timeout limit is exceeded."""
    pass


class ContactScraper:
    """
    A class to scrape contact information (emails, phone numbers, social media links)
    from a given website.
    """

    # A tuple of common file extensions to ignore during crawling
    IGNORED_EXTENSIONS = (
        # Images
        '.png', '.jpg', '.jpeg', '.gif', '.svg', '.webp', '.bmp', '.ico',
        # Documents
        '.pdf', '.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx', '.txt', '.csv',
        # Archives
        '.zip', '.rar', '.tar', '.gz',
        # Audio/Video
        '.mp3', '.mp4', '.avi', '.mov',
        # Other
        '.css', '.js', '.xml', '.json'
    )

    def __init__(self, url: str, max_links: int) -> None:
        """
        Initializes the ContactScraper with a starting URL.

        Args:
            url (str): The URL of the website to scrape.
        """
        if not urlparse(url).scheme:
            url = f"https://{url}"
            logger.info(f"No scheme provided. Assuming HTTPS. Using: {url}")

        self.start_url = url
        self.max_links = max_links

        parsed_url = urlparse(self.start_url)
        self.domain = parsed_url.netloc
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        self.visited_urls = set()
        self.contacts = {
            "emails": set(),
            "phone_numbers": set(),
            "social_media": set()
        }
        self.timeout_count = 0
        self.max_timeouts = 5

    def _fetch_html(self, url: str) -> str | None:
        """
        Fetches the HTML content of a given URL.

        Args:
            url (str): The URL to fetch the HTML from.

        Returns:
            str | None: The HTML content as a string, or None if the request fails.

        Raises:
            WebsiteUnreachableError: If the initial URL cannot be reached.
        """
        try:
            response = self.session.get(url, timeout=10)
            response.raise_for_status()  # Raise an HTTPError for bad responses (4xx or 5xx)
            if 'text/html' not in response.headers.get('Content-Type', ''):
                logger.debug(f"Skipping non-HTML content at {url}")
                return None
            return response.text
        except requests.exceptions.Timeout as e:
            self.timeout_count += 1
            logger.warning(f"Timeout fetching {url}. Total timeouts: {self.timeout_count}/{self.max_timeouts}")
            if self.timeout_count >= self.max_timeouts:
                raise GlobalTimeoutLimitReached(f"Global timeout limit of {self.max_timeouts} reached.") from e
            return None
        except requests.exceptions.RequestException as e:
            logger.error(f"Could not fetch URL {url}: {e}")
            if url == self.start_url:
                raise WebsiteUnreachableError(f"The initial URL {url} is unreachable.") from e
            return None

    def _extract_emails(self, soup: BeautifulSoup, page_text: str) -> None:
        """
        Extracts email addresses from page text and mailto links.

        Args:
            soup (BeautifulSoup): The BeautifulSoup object of the page.
            page_text (str): The pre-extracted text content of the page.
        """
        email_regex = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'

        # 1. Find in all page text (using the provided text)
        emails_in_text = re.findall(email_regex, page_text)
        for email in emails_in_text:
            self.contacts["emails"].add(email)

        # 2. Find in 'mailto:' links
        for a_tag in soup.find_all('a', href=True):
            href = a_tag['href']

            # Filter out irrelevant links before processing
            path = urlparse(href).path.lower()

            if any(path.endswith(ext) for ext in self.IGNORED_EXTENSIONS):
                continue

            if href.startswith('mailto:'):
                # Extract email from href, remove 'mailto:' and potential query params
                email = href.replace('mailto:', '', 1).split('?')[0]
                if re.fullmatch(email_regex, email):
                    self.contacts["emails"].add(email)

    def _extract_phone_numbers(self, soup: BeautifulSoup, page_text: str) -> None:
        """
        Extracts phone numbers from page text and 'tel:' links using regex.
        This regex is designed to find various common phone number formats.

        Args:
            soup (BeautifulSoup): The BeautifulSoup object of the page.
            page_text (str): The pre-extracted text content of the page.
        """
        # 1. Find in all page text (using the provided text)
        phone_regex = r'(\+?\d{1,3}[-.\s]?)?(\(?\d{3}\)?[-.\s]?)?[\d\s.-]{7,10}'
        phone_numbers_in_text = re.findall(phone_regex, page_text)
        for match in phone_numbers_in_text:
            phone_number = "".join(match).strip()
            # Validate to avoid matching random numbers, ensuring at least 7 digits
            if len(re.sub(r'\D', '', phone_number)) >= 7:
                self.contacts["phone_numbers"].add(phone_number)

        # 2. Find in 'tel:' links
        for a_tag in soup.find_all('a', href=True):
            href = a_tag['href']

            # Filter out irrelevant links before processing
            path = urlparse(href).path.lower()

            if any(path.endswith(ext) for ext in self.IGNORED_EXTENSIONS):
                continue

            if href.startswith('tel:'):
                phone_number = href.replace('tel:', '', 1).strip()
                self.contacts["phone_numbers"].add(phone_number)

    def _extract_social_media(self, soup: BeautifulSoup) -> None:
        """
        Extracts social media links from the parsed HTML.

        Args:
            soup (BeautifulSoup): The BeautifulSoup object of the page.
        """
        social_media_patterns = [
            'linkedin.com', 'twitter.com', 'facebook.com',
            'instagram.com', 'github.com', 'youtube.com'
        ]
        for a_tag in soup.find_all('a', href=True):
            href = a_tag['href']

            # Filter out irrelevant links before processing
            path = urlparse(href).path.lower()

            if any(path.endswith(ext) for ext in self.IGNORED_EXTENSIONS):
                continue

            if any(pattern in href for pattern in social_media_patterns):
                self.contacts["social_media"].add(href)

    def _crawl(self, url: str) -> None:
        """
        Recursively crawls a website starting from the given URL.

        Args:
            url (str): The URL to crawl.
        """
        if url in self.visited_urls or urlparse(url).netloc != self.domain:
            return

        if len(self.visited_urls) > self.max_links:
            return

        logger.info(f"Scraping: {url}")
        self.visited_urls.add(url)

        html = self._fetch_html(url)
        if not html:
            return

        try:
            soup = BeautifulSoup(html, 'html.parser')
            page_text = soup.get_text()  # Get text once to avoid errors and improve performance

            # Pass both soup object and page_text string to extraction methods
            self._extract_emails(soup, page_text)
            self._extract_phone_numbers(soup, page_text)
            self._extract_social_media(soup)

            for a_tag in soup.find_all('a', href=True):
                link = a_tag['href']

                # Filter out irrelevant links before processing
                path = urlparse(link).path.lower()

                if any(path.endswith(ext) for ext in self.IGNORED_EXTENSIONS):
                    continue

                absolute_link = urljoin(url, link)
                parsed_link = urlparse(absolute_link)
                # Reconstruct link without fragments
                clean_link = f"{parsed_link.scheme}://{parsed_link.netloc}{parsed_link.path}"
                if parsed_link.query:
                    clean_link += f"?{parsed_link.query}"

                self._crawl(clean_link)
        except Exception as e:
            logger.error(f"Error while parsing {url}: {e}")
            raise ScrapingError(f"Failed to parse content from {url}") from e

    def run(self) -> ContactScraperOutput:
        """
        The main entry point for the scraper. Starts the crawling process
        and returns the collected contact information.

        Returns:
            dict: A dictionary containing sets of emails, phone numbers,
                  and social media links.
        """
        logger.info(f"Starting scrape for {self.start_url}")
        try:
            self._crawl(self.start_url)
        except GlobalTimeoutLimitReached as e:
            logger.critical(f"{e} Aborting crawl. Returning what has been found so far.")
        except (WebsiteUnreachableError, ScrapingError) as e:
            logger.critical(f"A critical error occurred: {e}")

        logger.success("Scraping finished.")
        # Convert sets to lists for easier use (e.g., JSON serialization)
        final_contacts = {
            "emails": list(self.contacts["emails"]),
            "phone_numbers": list(self.contacts["phone_numbers"]),
            "social_media": list(self.contacts["social_media"])
        }
        logger.success(f"Found: {final_contacts}")
        return ContactScraperOutput(**final_contacts)


@tool(args_schema=ContactScraperInput)
def contact_scraper(url: str, max_links: int) -> ContactScraperOutput:
    """Scrapes a website to find and extract contact information.

    This tool crawls an entire website starting from the provided URL. It searches
    all accessible pages within the same domain for contact details such as
    email addresses, phone numbers, and links to social media profiles.
    The collected information is deduplicated and returned in a structured format.

    Args:
        url (str): The base URL or domain name of the website to scrape.

    Returns:
        ContactInfo: An object containing lists of found emails,
                     phone numbers, and social media links.
    """
    scraper = ContactScraper(url, max_links)
    contact_info = scraper.run()
    return contact_info


if __name__ == '__main__':
    # Example usage:
    target_url = "https://www.google.com"

    scraper = ContactScraper(target_url)
    contact_info = scraper.run()

    if contact_info:
        logger.success("\n--- Contact Information Found ---")
        logger.success(f"Emails: {contact_info.emails}")
        logger.success(f"Phone Numbers: {contact_info.phone_numbers}")
        logger.success(f"Social Media: {contact_info.social_media}")
        logger.success("---------------------------------")
    else:
        logger.error("Could not retrieve contact information.")
