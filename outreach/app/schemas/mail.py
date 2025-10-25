from pydantic import BaseModel, Field


class MailAgentOutput(BaseModel):
    subject: str = Field(..., description="The subject line of the email.")
    body: str = Field(..., description="The plain-text content of the email.")
    html_content: str | None = Field(None, description="The HTML content for the email.")


class MailInput(BaseModel):
    sender_email_address: str = Field(..., description="The Gmail address to send from.")
    sender_email_password: str = Field(...,
                                       description="The 16-digit 'App Password' generated from Google Account settings.")
    recipient_email_address: str = Field(..., description="The email address of the recipient.")
    subject: str = Field(..., description="The subject line of the email.")
    body: str = Field(..., description="The plain-text content of the email.")
    html_content: str | None = Field(None, description="The HTML content for the email.")


class MailOutput(BaseModel):
    success: bool = Field(..., description="True if the email was sent successfully, False otherwise.")
