from loguru import logger

from app.schemas import GoogleMapsSearchOutput, GoogleMapsSearchInput
from app.schemas.lead import Lead
from app.schemas.state import State
from app.tools import google_maps_search


def generate_leads_node(state: State) -> State:
    """Generates business leads by searching Google Maps.

    This function takes the current state, which includes search parameters
    like city, business type, and radius, and uses them to query the
    Google Maps search tool. It processes the results, converts them into
    a list of Lead objects, and updates the state with these leads.
    It includes robust error handling for the API call and data processing.

    Args:
        state: An object containing the current application state, including
               all necessary parameters for the Google Maps search.

    Returns:
        An updated State object. If the search is successful, the state's
        'leads' attribute will be populated with a list of Lead objects.
        If an error occurs, the original state is returned, potentially
        with an error message if the state schema supports it.
    """
    logger.info(
        "Starting lead generation for business type '%s' in %s.",
        state.business_type,
        state.city
    )

    try:
        # Step 1: Prepare the input for the Google Maps search tool
        # using the parameters from the current state.
        search_input = GoogleMapsSearchInput(
            city=state.city,
            business_type=state.business_type,
            radius=state.radius,
            min_rating=state.min_rating,
            max_results=state.max_results,
        ).model_dump()

        # Step 2: Invoke the external tool/API to perform the search.
        # This is wrapped in a try-except block to catch any exceptions
        # during the API call, such as network issues or timeouts.
        google_maps_search_result: GoogleMapsSearchOutput = google_maps_search.invoke(
            search_input
        )
        logger.debug("Received response from Google Maps search API.")

    except Exception as e:
        # Catch any unexpected exceptions during the API call.
        logger.exception(
            "An unexpected error occurred while calling the google_maps_search tool: %s", e
        )
        # Return the original state without modification, preventing a crash.
        return state.model_copy()

    # Step 3: Process the response from the search tool.
    # Check if the result object exists and if the status is 'success'.
    if google_maps_search_result and google_maps_search_result.status == "success":
        if not google_maps_search_result.results:
            logger.warning(
                "Google Maps search was successful but returned no results for the given criteria."
            )
            # If there are no results, update the state with an empty list.
            return state.model_copy(update={"leads": []})

        try:
            # Use a list comprehension to iterate through the raw results
            # and create a list of structured Lead objects.
            # This ensures the data conforms to our application's schema.
            updated_leads: list[Lead] = [
                Lead(
                    place_id=result.place_id,
                    name=result.name,
                    address=result.address,
                    phone_number=result.phone_number,
                    website=result.website,
                    rating=result.rating,
                    total_ratings=result.total_ratings,
                    category=result.category,
                    price_level=result.price_level,
                    is_open=result.is_open,
                    location=result.location
                ) for result in google_maps_search_result.results
            ]
            logger.info(
                "Successfully generated %d leads.", len(updated_leads)
            )

            # Return a copy of the state, updated with the new list of leads.
            return state.model_copy(update={"leads": updated_leads})

        except (TypeError, AttributeError, KeyError) as e:
            # Catch potential errors during the creation of Lead objects,
            # which could happen if the API response format is unexpected.
            logger.exception(
                "Error processing search results into Lead objects: %s", e
            )
            # Return original state to avoid propagating corrupted data.
            return state.model_copy()

    else:
        # Handle cases where the API call was made but returned a failure status.
        error_message = (
            google_maps_search_result.error
            if google_maps_search_result and google_maps_search_result.error
            else "Unknown error from the search tool."
        )
        logger.error(
            "Google Maps search tool returned a failure status: %s", error_message
        )
        # Return the original state. In a real-world scenario, you might want
        # to add the error message to the state if the schema allows it.
        return state.model_copy()
