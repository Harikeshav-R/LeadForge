from app.core import Config
from app.schemas import State
from app.tools import start_phone_call


def start_phone_call_node(state: State) -> State:
    start_phone_call(
        Config.TWILIO_ACCOUNT_SID,
        Config.TWILIO_AUTH_TOKEN,
        Config.TWILIO_PHONE_NUMBER,
        state.client_phone_number
    )

    return state.model_copy()
