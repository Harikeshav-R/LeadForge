from app import schemas, crud, get_db
from app.schemas import State


def save_intermediate_state_node(state: State) -> State:
    initial_state_create = schemas.StateCreate(**state.model_dump())
    created_state = crud.create_state(get_db(), state_data=initial_state_create)

    return State.model_validate(created_state)
