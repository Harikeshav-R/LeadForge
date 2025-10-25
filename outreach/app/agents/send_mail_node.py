from app.schemas import State, MailOutput, MailInput
from app.tools import send_gmail


def send_mail_node(state: State) -> State:
    result: MailOutput = send_gmail.invoke(
        MailInput(
            recipient_email_address=state.client_email,
            subject=state.email_contents.subject,
            body=state.email_contents.body,
            html_content=state.email_contents.html_content,
        ).model_dump()
    )

    return state.model_copy(update={"email_sent": result.success})
