from app import schemas, crud
from app.core import SessionLocal
from app.schemas import State


def save_intermediate_state_node(state: State) -> State:
    initial_state_create = schemas.StateCreate(**state.model_dump())

    db = SessionLocal()
    created_state = crud.create_state(db, state_data=initial_state_create)
    state = State.model_validate(created_state)

    db.close()

    return state
