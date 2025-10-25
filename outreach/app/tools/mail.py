import smtplib
from email.message import EmailMessage

from langchain_core.tools import tool
from loguru import logger

from app.core import Config
from app.schemas import MailInput, MailOutput


class GmailSender:
    """A class to send emails using a Gmail account via SMTP.

    This class is best used as a context manager (using 'with') to
    properly handle the connection and disconnection from the SMTP server.

    Attributes:
        sender_email_address (str): The Gmail address to send from.
        sender_email_password (str): The 16-digit "App Password".
        smtp_server (str): The SMTP server address (default "smtp.gmail.com").
        smtp_port (int): The SMTP server port (default 587).
        server (smtplib.SMTP | None): The smtplib.SMTP server instance.
    """

    def __init__(self, sender_email_address: str, sender_email_password: str):
        """Initializes the GmailSender.

        Args:
            sender_email_address (str): The Gmail address to send from.
            sender_email_password (str): The 16-digit "App Password" generated from
                                Google Account settings.
        """
        if not sender_email_address.endswith('@gmail.com'):
            logger.warning(
                "This class is optimized for Gmail. Using a non-Gmail "
                f"address ({sender_email_address}) may fail."
            )

        self.sender_email = sender_email_address
        self.sender_email_password = sender_email_password
        self.smtp_server = "smtp.gmail.com"
        self.smtp_port = 587
        self.server: smtplib.SMTP | None = None

    def __enter__(self):
        """Initializes and connects to the SMTP server.

        Called when entering a 'with' block.

        Returns:
            GmailSender: The instance of itself.

        Raises:
            smtplib.SMTPConnectError: If it fails to connect to the server.
            smtplib.SMTPHeloError: If the server refuses the HELO/EHLO message.
            smtplib.SMTPAuthenticationError: If login fails (bad user/pass).
            smtplib.SMTPException: For other general SMTP errors.
            Exception: For non-SMTP unexpected errors.
        """
        try:
            logger.info(f"Connecting to SMTP server {self.smtp_server}:{self.smtp_port}...")
            self.server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            self.server.starttls()  # Secure the connection
            logger.info(f"Logging in as {self.sender_email}...")
            self.server.login(self.sender_email, self.sender_email_password)
            logger.info("Successfully connected and logged in.")
            return self
        except smtplib.SMTPConnectError as e:
            logger.error(f"Failed to connect to SMTP server: {e}")
            raise
        except smtplib.SMTPHeloError as e:
            logger.error(f"Server refused HELO/EHLO: {e}")
            raise
        except smtplib.SMTPAuthenticationError as e:
            logger.error(f"SMTP authentication failed (check email/app password): {e}")
            raise
        except smtplib.SMTPException as e:
            logger.error(f"An SMTP error occurred during connection: {e}")
            raise
        except Exception as e:
            logger.error(f"An unexpected error occurred during connection: {e}")
            raise

    def __exit__(self, exc_type, exc_value, traceback):
        """Disconnects from the SMTP server.

        Called when exiting a 'with' block.

        Args:
            exc_type (type | None): The type of exception raised, if any.
            exc_value (Exception | None): The exception instance, if any.
            traceback (TracebackType | None): The traceback, if any.
        """
        if exc_type:
            logger.error(f"Exiting context due to an exception: {exc_type.__name__}: {exc_value}")

        if self.server:
            try:
                self.server.quit()
                logger.info("Disconnected from SMTP server.")
            except smtplib.SMTPException as e:
                logger.error(f"Error during server.quit(): {e}")

    def send_email(self, recipient_email: str, subject: str, body: str,
                   html_content: str | None = None):
        """Sends a single email.

        This method must be called within a 'with' block, after the
        connection has been established. If html_content is provided,
        the email will be sent as a multipart/alternative message with
        the plain text 'body' as a fallback.

        Args:
            recipient_email (str): The email address of the recipient.
            subject (str): The subject line of the email.
            body (str): The plain-text content of the email.
            html_content (str | None, optional): The HTML content for the
                                                email. Defaults to None.

        Raises:
            ConnectionError: If called before connecting (not in 'with' block).
            smtplib.SMTPRecipientsRefused: If the server rejects the recipient.
            smtplib.SMTPSenderRefused: If the server rejects the sender.
            smtplib.SMTPDataError: If the server rejects the email data.
            smtplib.SMTPException: For other general SMTP errors.
            Exception: For non-SMTP unexpected errors.
        """
        if not self.server:
            logger.error("send_email() called but not connected to server.")
            raise ConnectionError("Not connected. This method must be called "
                                  "within a 'with' block.")

        # Create the email message object
        msg = EmailMessage()
        msg['Subject'] = subject
        msg['From'] = self.sender_email
        msg['To'] = recipient_email
        msg.set_content(body)

        # If HTML content is provided, add it as an 'alternative'
        if html_content:
            msg.add_alternative(html_content, subtype='html')
            logger.info("Added HTML alternative to the email.")

        try:
            logger.info(f"Sending email to {recipient_email} (Subject: {subject})...")
            self.server.send_message(msg)
            logger.info(f"Email sent successfully to {recipient_email}.")
        except smtplib.SMTPRecipientsRefused as e:
            logger.error(f"Server refused recipient {recipient_email}: {e}")
            raise
        except smtplib.SMTPSenderRefused as e:
            logger.error(f"Server refused sender {self.sender_email}: {e}")
            raise
        except smtplib.SMTPDataError as e:
            logger.error(f"Server refused email data: {e}")
            raise
        except smtplib.SMTPException as e:
            logger.error(f"Error sending email: {e}")
            raise
        except Exception as e:
            logger.error(f"An unexpected error occurred during sending: {e}")
            raise


# --- Global Wrapper Function ---

@tool(args_schema=MailInput)
def send_gmail(recipient_email_address: str,
               subject: str, body: str,
               html_content: str | None = None) -> MailOutput:
    """A global wrapper function to send a single email.

    This function handles the complete process:
    1. Connects to the Gmail SMTP server.
    2. Logs in.
    3. Sends the email.
    4. Disconnects.

    Args:
        recipient_email_address (str): The email address of the recipient.
        subject (str): The subject line of the email.
        body (str): The plain-text content of the email.
        html_content (str | None, optional): The HTML content for the
                                            email. Defaults to None.

    Returns:
        bool: True if the email was sent successfully, False otherwise.
    """
    logger.info("--- Using global send_gmail function ---")
    try:
        # Use the class as a context manager
        with GmailSender(Config.SENDER_EMAIL_ADDRESS, Config.SENDER_EMAIL_PASSWORD) as mailer:
            mailer.send_email(recipient_email_address, subject, body, html_content)
        logger.info("--- Global function complete ---")
        return MailOutput(success=True)

    except Exception as e:
        # The class methods already log the specific error
        logger.error(f"Global function send_gmail() failed: {e}")
        return MailOutput(success=False)


# --- Example Usage ---

if __name__ == "__main__":
    # --- Example 1: Using the global wrapper function (HTML version) ---
    # Easiest for sending a single email.

    logger.info("\n--- Testing Global Function (with HTML) ---")
    try:
        # Simple HTML content for testing
        html_body = """
        <html>
        <head></head>
        <body>
            <h1 style="color: #336699;">Hello from Python!</h1>
            <p>This email was sent using the 
            <code style="background-color: #f0f0f0; padding: 2px 4px; border-radius: 3px;">send_gmail()</code> 
            wrapper function with HTML content.</p>
            <p>Have a great day!</p>
        </body>
        </html>
        """

        success: MailOutput = send_gmail.invoke(
            MailInput(
                recipient_email_address="test@gmail.com",
                subject="Test from Global Function (HTML)",
                body="Hello! This is the plain-text fallback for the HTML email.",
                html_content=html_body
            ).model_dump()
        )
        logger.info(f"Global function (HTML) test result: {"Success" if success.success else "Failed"}")

    except Exception as e:
        logger.error(f"Unhandled exception during global function test: {e}")
