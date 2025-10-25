import uuid

from pydantic import BaseModel, Field


class MailBase(BaseModel):
    subject: str = Field(..., description="The subject line of the email.")
    body: str = Field(..., description="The plain-text content of the email.")
    html_content: str | None = Field(None, description="The HTML content for the email.")


class MailAgentOutput(MailBase):
    pass


class MailInput(MailBase):
    recipient_email_address: str = Field(..., description="The email address of the recipient.")


class MailOutput(BaseModel):
    success: bool = Field(..., description="True if the email was sent successfully, False otherwise.")


class MailCreate(MailBase):
    recipient_email_address: str = Field(..., description="The email address of the recipient.")


class MailUpdate(BaseModel):
    subject: str | None = Field(None, description="The subject line of the email.")
    body: str | None = Field(None, description="The plain-text content of the email.")
    html_content: str | None = Field(None, description="The HTML content for the email.")


class Mail(MailBase):
    id: uuid.UUID = Field(uuid.uuid4(), description="ID of the mail.")

    recipient_email_address: str = Field(..., description="The email address of the recipient.")

    class Config:
        from_attributes = True
