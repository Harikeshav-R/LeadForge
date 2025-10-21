import time
from typing import Any, Optional, Callable

import googlemaps
from googlemaps.exceptions import ApiError, HTTPError, Timeout, TransportError
from langchain_core.tools import tool
from loguru import logger

from app.core import Config
from app.schemas import GoogleMapsSearchInput, GoogleMapsSearchOutput, SearchMetadata, PlaceResult, Location


# --- Custom Exception Classes ---

class GoogleMapsClientError(Exception):
    """Base exception for custom errors in the GoogleMapsClient."""
    pass


class APIKeyError(GoogleMapsClientError):
    """Raised when the Google Maps API key is missing or invalid."""
    pass


class LocationNotFoundError(GoogleMapsClientError):
    """Raised when a specified location (e.g., city) cannot be geocoded."""
    pass


class GoogleMapsClient:
    """
    A client for interacting with the Google Maps API to search for businesses.

    This class provides a high-level interface to find businesses, handle API
    errors gracefully, and format the results into a clean, usable structure.
    """
    # Valid types for the 'type' parameter in a places_nearby search.
    # See: https://developers.google.com/maps/documentation/places/web-service/supported_types
    _VALID_NEARBY_SEARCH_TYPES = {
        "accounting", "airport", "amusement_park", "aquarium", "art_gallery",
        "atm", "bakery", "bank", "bar", "beauty_salon", "bicycle_store",
        "book_store", "bowling_alley", "bus_station", "cafe", "campground",
        "car_dealer", "car_rental", "car_repair", "car_wash", "casino",
        "cemetery", "church", "city_hall", "clothing_store", "convenience_store",
        "courthouse", "dentist", "department_store", "doctor", "drugstore",
        "electrician", "electronics_store", "embassy", "fire_station", "florist",
        "funeral_home", "furniture_store", "gas_station", "gym", "hair_care",
        "hardware_store", "hindu_temple", "home_goods_store", "hospital",
        "insurance_agency", "jewelry_store", "laundry", "lawyer", "library",
        "light_rail_station", "liquor_store", "local_government_office",
        "locksmith", "lodging", "meal_delivery", "meal_takeaway", "mosque",
        "movie_rental", "movie_theater", "moving_company", "museum", "night_club",
        "painter", "park", "parking", "pet_store", "pharmacy", "physiotherapist",
        "plumber", "police", "post_office", "primary_school", "real_estate_agency",
        "restaurant", "roofing_contractor", "rv_park", "school", "secondary_school",
        "shoe_store", "shopping_mall", "spa", "stadium", "storage", "store",
        "subway_station", "supermarket", "synagogue", "taxi_stand",
        "tourist_attraction", "train_station", "transit_station", "travel_agency",
        "university", "veterinary_care", "zoo"
    }

    def __init__(self, api_key: Optional[str]) -> None:
        """
        Initializes the GoogleMapsClient.

        Args:
            api_key: The Google Maps API key for authentication.

        Raises:
            APIKeyError: If the API key is not provided or is invalid,
                         preventing client initialization.
        """
        if not api_key:
            logger.error("Google Maps API key not provided.")
            raise APIKeyError("Google Maps API key is required.")

        try:
            self.client = googlemaps.Client(key=api_key)
            # Perform a test query to validate the key immediately.
            self.client.geocode("USA")
            logger.info("Google Maps client initialized and validated successfully.")
        except (ApiError, HTTPError, TransportError) as e:
            logger.error(f"Failed to initialize Google Maps client: {e}")
            raise APIKeyError(f"API key is invalid or client failed to initialize: {e}") from e

    def _get_city_location(self, city: str) -> dict[str, float]:
        """
        Geocodes a city name to get its latitude and longitude.

        Args:
            city: The name of the city to locate.

        Returns:
            A dictionary containing the 'lat' and 'lng' of the city.

        Raises:
            LocationNotFoundError: If the city cannot be found.
            GoogleMapsClientError: For other API-related errors.
        """
        try:
            geocode_result = self.client.geocode(city)
            if not geocode_result:
                raise LocationNotFoundError(f"Could not find location for city: {city}")

            location = geocode_result[0]['geometry']['location']
            logger.info(f"Found location for {city}: {location}")
            return location
        except (ApiError, HTTPError, Timeout) as e:
            logger.error(f"API error while geocoding {city}: {e}")
            raise GoogleMapsClientError(f"An API error occurred while finding {city}") from e

    @staticmethod
    def _perform_paginated_search(
            search_func: Callable[..., dict],
            max_results: int,
            **kwargs: Any
    ) -> list[dict[str, Any]]:
        """
        Performs a search using a given client method and handles pagination.

        Args:
            search_func: The googlemaps client method to call (e.g., self.client.places).
            max_results: The maximum number of results to fetch.
            **kwargs: Arguments to pass to the search function.

        Returns:
            A list of raw place results from the API.

        Raises:
            GoogleMapsClientError: For API-related errors during the search.
        """
        all_results = []
        try:
            response = search_func(**kwargs)
            all_results.extend(response.get('results', []))
            next_page_token = response.get('next_page_token')

            while next_page_token and len(all_results) < max_results:
                time.sleep(2)  # Required delay before fetching the next page.
                logger.info(f"Fetching next page of results for query: {kwargs.get('query')}")
                response = search_func(page_token=next_page_token, **kwargs)
                all_results.extend(response.get('results', []))
                next_page_token = response.get('next_page_token')

        except (ApiError, HTTPError, Timeout) as e:
            logger.error(f"API error during paginated search: {e}")
            raise GoogleMapsClientError(f"An API error occurred during search.") from e

        return all_results

    def _get_place_details(self, place_id: str) -> Optional[dict[str, Any]]:
        """
        Fetches detailed information for a specific place ID.

        Args:
            place_id: The unique identifier for the place.

        Returns:
            A dictionary containing the place details, or None on error.
        """
        try:
            place_details = self.client.place(place_id=place_id)
            return place_details.get('result', None)
        except (ApiError, HTTPError, Timeout) as e:
            logger.warning(f"Could not get details for place_id {place_id}: {e}")
            return None

    @staticmethod
    def _is_valid_website(website: str) -> bool:
        """
        Checks if a website URL appears to be a real, functional website.

        Args:
            website: The URL string to check.

        Returns:
            True if the website is considered valid, False otherwise.
        """
        if not website:
            return False

        # Basic checks for placeholder or non-functional websites
        invalid_indicators = [
            "placeholder", "coming-soon", "under-construction", "example.com"
        ]
        return all([
            len(website) > 5,
            "." in website,
            not any(indicator in website.lower() for indicator in invalid_indicators),
            not website.startswith("http://localhost"),
        ])

    @staticmethod
    def _format_business_data(
            place: dict[str, Any],
            details: dict[str, Any]
    ) -> PlaceResult:
        """
        Formats raw place and details data into a structured business dictionary.

        Args:
            place: The initial place data from a search result.
            details: The detailed place data from a place details request.

        Returns:
            A dictionary with standardized business information.
        """
        # return {
        #     "place_id": place.get('place_id'),
        #     "name": details.get('name', place.get('name')),
        #     "address": details.get('formatted_address'),
        #     "phone": details.get('formatted_phone_number'),
        #     "website": details.get('website'),
        #     "rating": details.get('rating', place.get('rating')),
        #     "total_ratings": details.get('user_ratings_total', 0),
        #     "category": (details.get('types') or [None])[0],
        #     "price_level": details.get('price_level'),
        #     "is_open": details.get('opening_hours', {}).get('open_now'),
        #     "location": place.get('geometry', {}).get('location', {})
        # }
        return PlaceResult(
            place_id=place.get("place_id"),
            name=details.get("name", place.get("name")),
            address=details.get("formatted_address"),
            phone_number=details.get("formatted_phone_number"),
            website=details.get("website"),
            rating=details.get("rating", place.get("rating")),
            total_ratings=details.get("user_ratings_total", 0),
            category=details.get("types", [None])[0],
            price_level=details.get("price_level"),
            is_open=details.get("opening_hours", {}).get("open_now"),
            location=Location(**place.get("geometry", {}).get("location", {}))
        )

    def _process_place_results(
            self,
            places: list[dict[str, Any]],
            min_rating: float,
            exclude_websites: bool,
            max_results: int
    ) -> list[PlaceResult]:
        """
        Processes raw search results into a final list of formatted businesses.

        This method fetches details for each place, applies filters, and formats
        the data into the final structure.

        Args:
            places: A list of raw place results from the API.
            min_rating: The minimum rating for a business to be included.
            exclude_websites: If True, only include businesses without a valid website.
            max_results: The maximum number of final results to return.

        Returns:
            A list of processed and filtered business dictionaries.
        """
        businesses = []
        processed_ids = set()

        for place in places:
            if len(businesses) >= max_results:
                break

            place_id = place.get('place_id')
            if not place_id or place_id in processed_ids:
                continue

            processed_ids.add(place_id)

            details = self._get_place_details(place_id)
            if not details:
                continue

            rating = details.get('rating', 0) or 0
            if rating < min_rating:
                continue

            website = details.get('website', '')
            if exclude_websites and self._is_valid_website(website):
                continue

            business_data = self._format_business_data(place, details)
            if business_data.name and business_data.address:
                businesses.append(business_data)

        return businesses

    def search_businesses(
            self,
            city: str,
            business_type: Optional[str] = None,
            radius: int = 50000,
            min_rating: float = 0.0,
            max_results: int = 100,
            exclude_websites: bool = True
    ) -> list[PlaceResult]:
        """
        Searches for businesses in a city, applying filters and formatting results.

        This method orchestrates the entire search process, from finding the city's
        location to fetching and processing business data.

        Args:
            city: The name of the city to search within.
            business_type: An optional specific type of business to search for (e.g., "restaurant").
            radius: The search radius in meters from the city center.
            min_rating: The minimum review rating for businesses to be included.
            max_results: The maximum number of businesses to return.
            exclude_websites: If True, filters out businesses that have a website.

        Returns:
            A list of dictionaries, where each dictionary represents a business.

        Raises:
            LocationNotFoundError: If the specified city cannot be found.
            GoogleMapsClientError: For other API or processing errors.
        """
        location = self._get_city_location(city)
        query = f"{business_type or 'business'} in {city}"

        # Perform a Text Search first, as it's generally broader
        raw_results = self._perform_paginated_search(
            search_func=self.client.places,
            max_results=max_results * 5,  # Fetch more to have enough for filtering
            query=query,
            location=location,
            radius=radius
        )

        # If a valid business_type is provided, also do a Nearby Search
        if business_type and business_type in self._VALID_NEARBY_SEARCH_TYPES:
            logger.info(f"Performing additional Nearby Search for type: {business_type}")
            nearby_results = self._perform_paginated_search(
                search_func=self.client.places_nearby,
                max_results=max_results * 3,
                location=location,
                radius=radius,
                type=business_type
            )
            # Combine and deduplicate results
            places_by_id = {p['place_id']: p for p in raw_results}
            places_by_id.update({p['place_id']: p for p in nearby_results})
            raw_results = list(places_by_id.values())

        logger.info(f"Found {len(raw_results)} total raw results for {city}.")

        return self._process_place_results(
            places=raw_results,
            min_rating=min_rating,
            exclude_websites=exclude_websites,
            max_results=max_results
        )


# --- Public API Function ---

_maps_client_instance: Optional[GoogleMapsClient] = None


def get_maps_client() -> GoogleMapsClient:
    """
    Acts as a singleton factory for the GoogleMapsClient.

    Initializes the client on first call and returns the existing instance
    on subsequent calls.

    Returns:
        An initialized GoogleMapsClient instance.

    Raises:
        APIKeyError: If the client cannot be initialized due to a missing key.
    """
    global _maps_client_instance
    if _maps_client_instance is None:
        logger.info("Initializing global GoogleMapsClient instance...")
        _maps_client_instance = GoogleMapsClient(api_key=Config.GOOGLE_MAPS_API_KEY)
    return _maps_client_instance


def _google_maps_search(
        city: str,
        business_type: Optional[str] = None,
        radius: int = 50000,
        min_rating: float = 0.0,
        max_results: int = 100,
        exclude_websites: bool = True
) -> GoogleMapsSearchOutput:
    """
    High-level function to search for businesses using Google Maps.

    This function provides a safe and simple interface for the search,
    handling client initialization and all potential errors, and returning
    a standardized dictionary response.

    Args:
        city: The name of the city to search in.
        business_type: Optional business type filter (e.g., "cafe").
        min_rating: Minimum rating filter.
        max_results: Maximum number of results to return.
        exclude_websites: If True, only return businesses without websites.

    Returns:
        A dictionary with search status, results, and metadata.
    """
    response_metadata = {
        "city": city,
        "business_type": business_type,
        "radius": radius,
        "min_rating": min_rating,
        "max_results": max_results,
        "exclude_websites": exclude_websites,
    }

    try:
        maps_client = get_maps_client()
        businesses = maps_client.search_businesses(
            city=city,
            business_type=business_type,
            radius=radius,
            min_rating=min_rating,
            max_results=max_results,
            exclude_websites=exclude_websites
        )

        return GoogleMapsSearchOutput(
            status="success",
            message=None,
            total_results=len(businesses),
            results=businesses,
            search_metadata=SearchMetadata(**response_metadata, api_available=True)
        )
        #
        # return {
        #     "status": "success",
        #     "total_results": len(businesses),
        #     "results": businesses,
        #     "search_metadata": {**response_metadata, "api_available": True}
        # }

    except (APIKeyError, LocationNotFoundError, GoogleMapsClientError) as e:
        logger.error(f"Failed to complete Google Maps search for '{city}': {e}")
        # return {
        #     "status": "error",
        #     "message": str(e),
        #     "total_results": 0,
        #     "results": [],
        #     "search_metadata": {**response_metadata, "api_available": False}
        # }
        return GoogleMapsSearchOutput(
            status="error",
            message=str(e),
            total_results=0,
            results=[],
            search_metadata=SearchMetadata(**response_metadata, api_available=False)
        )
    except Exception as e:
        logger.critical(f"An unexpected error occurred during search: {e}", exc_info=True)
        # return {
        #     "status": "error",
        #     "message": "An unexpected internal error occurred.",
        #     "total_results": 0,
        #     "results": [],
        #     "search_metadata": {**response_metadata, "api_available": False}
        # }
        return GoogleMapsSearchOutput(
            status="error",
            message="An unexpected internal error occurred.",
            total_results=0,
            results=[],
            search_metadata=SearchMetadata(**response_metadata, api_available=False)
        )


@tool(args_schema=GoogleMapsSearchInput)
def google_maps_search(
        city: str,
        business_type: Optional[str] = None,
        radius: int = 50000,
        min_rating: float = 0.0,
        max_results: int = 10,
        exclude_websites: bool = False
) -> GoogleMapsSearchOutput:
    """
    High-level function to search for businesses using Google Maps.

    This function provides a safe and simple interface for the search,
    handling client initialization and all potential errors, and returning
    a standardized dictionary response.

    Args:
        city: The name of the city to search in.
        business_type: Optional business type filter (e.g., "cafe").
        min_rating: Minimum rating filter.
        max_results: Maximum number of results to return.
        exclude_websites: If True, only return businesses without websites.

    Returns:
        A dictionary with search status, results, and metadata.
    """

    return _google_maps_search(
        city=city,
        business_type=business_type,
        min_rating=min_rating,
        max_results=max_results,
        exclude_websites=exclude_websites
    )


@tool(parse_docstring=True)
def google_maps_nearby_search(city: str, business_type: str = "restaurant") -> GoogleMapsSearchOutput:
    """
    A function to search for a specific type of business in a city.

    This is a wrapper around the main `google_maps_search` tool, pre-configured
    to search for a particular business category.

    Args:
        city: The name of the city to search in.
        business_type: The category of business to search for (e.g., "cafe", "gym").

    Returns:
        A dictionary with search status, results, and metadata.
    """
    return _google_maps_search(city=city, business_type=business_type)


@tool(parse_docstring=True)
def google_maps_high_rated_search(city: str, min_rating: float = 4.0) -> GoogleMapsSearchOutput:
    """
    A function to find highly rated businesses in a city.

    This is a wrapper around the main `google_maps_search` tool, pre-configured
    to filter results by a minimum rating.

    Args:
        city: The name of the city to search in.
        min_rating: The minimum rating a business must have to be included.

    Returns:
        A dictionary with search status, results, and metadata.
    """
    return _google_maps_search(city=city, min_rating=min_rating)


# --- Example Usage ---
if __name__ == '__main__':
    logger.info("--- Searching for restaurants in New York with no websites ---")
    search_result = google_maps_search.run(
        city="New York",
        business_type="restaurant",
        min_rating=0,
        max_results=5,
        exclude_websites=False
    )
    logger.success(search_result.model_dump_json(indent=2))
    # print(json.dumps(search_result, indent=2))
