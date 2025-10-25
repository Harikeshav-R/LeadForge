from app.schemas import State, MailOutput
from app.tools import send_gmail


def send_mail_node(state: State) -> State:
    result: MailOutput = send_gmail.invoke(
        state.email_contents.model_dump()
    )

    return state.model_copy(update={"email_sent": result.success})
