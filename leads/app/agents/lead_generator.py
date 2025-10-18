from app.schemas import GoogleMapsSearchOutput, GoogleMapsSearchInput
from app.schemas.lead import Lead
from app.schemas.state import State
from app.tools import google_maps_search


def generate_leads_node(state: State) -> None:
    google_maps_search_result: GoogleMapsSearchOutput = google_maps_search.invoke(
        GoogleMapsSearchInput(
            city=state.city,
            business_type=state.business_type
        )
    )

    if google_maps_search_result.status == "success":
        for result in google_maps_search_result.results:
            state.leads.append(
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
                )
            )

    else:
        pass
