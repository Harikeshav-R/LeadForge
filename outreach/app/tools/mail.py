import smtplib
from email.message import EmailMessage

from loguru import logger

from app.core import Config


class GmailSender:
    """A class to send emails using a Gmail account via SMTP.

    This class is best used as a context manager (using 'with') to
    properly handle the connection and disconnection from the SMTP server.

    Attributes:
        sender_email (str): The Gmail address to send from.
        app_password (str): The 16-digit "App Password".
        smtp_server (str): The SMTP server address (default "smtp.gmail.com").
        smtp_port (int): The SMTP server port (default 587).
        server (smtplib.SMTP | None): The smtplib.SMTP server instance.
    """

    def __init__(self, sender_email: str, app_password: str):
        """Initializes the GmailSender.

        Args:
            sender_email (str): The Gmail address to send from.
            app_password (str): The 16-digit "App Password" generated from
                                Google Account settings.
        """
        if not sender_email.endswith('@gmail.com'):
            logger.warning(
                "This class is optimized for Gmail. Using a non-Gmail "
                "address (%s) may fail.", sender_email
            )

        self.sender_email = sender_email
        self.app_password = app_password
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
            logger.info("Connecting to SMTP server %s:%s...",
                        self.smtp_server, self.smtp_port)
            self.server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            self.server.starttls()  # Secure the connection
            logger.info("Logging in as %s...", self.sender_email)
            self.server.login(self.sender_email, self.app_password)
            logger.info("Successfully connected and logged in.")
            return self
        except smtplib.SMTPConnectError as e:
            logger.error("Failed to connect to SMTP server: %s", e)
            raise
        except smtplib.SMTPHeloError as e:
            logger.error("Server refused HELO/EHLO: %s", e)
            raise
        except smtplib.SMTPAuthenticationError as e:
            logger.error("SMTP authentication failed (check email/app password): %s", e)
            raise
        except smtplib.SMTPException as e:
            logger.error("An SMTP error occurred during connection: %s", e)
            raise
        except Exception as e:
            logger.error("An unexpected error occurred during connection: %s", e)
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
            logger.error("Exiting context due to an exception: %s: %s",
                         exc_type.__name__, exc_value)

        if self.server:
            try:
                self.server.quit()
                logger.info("Disconnected from SMTP server.")
            except smtplib.SMTPException as e:
                logger.error("Error during server.quit(): %s", e)

    def send_email(self, recipient_email: str, subject: str, body: str):
        """Sends a single email.

        This method must be called within a 'with' block, after the
        connection has been established.

        Args:
            recipient_email (str): The email address of the recipient.
            subject (str): The subject line of the email.
            body (str): The plain-text content of the email.

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

        try:
            logger.info("Sending email to %s (Subject: %s)...",
                        recipient_email, subject)
            self.server.send_message(msg)
            logger.info("Email sent successfully to %s.", recipient_email)
        except smtplib.SMTPRecipientsRefused as e:
            logger.error("Server refused recipient %s: %s", recipient_email, e)
            raise
        except smtplib.SMTPSenderRefused as e:
            logger.error("Server refused sender %s: %s", self.sender_email, e)
            raise
        except smtplib.SMTPDataError as e:
            logger.error("Server refused email data: %s", e)
            raise
        except smtplib.SMTPException as e:
            logger.error("Error sending email: %s", e)
            raise
        except Exception as e:
            logger.error("An unexpected error occurred during sending: %s", e)
            raise


# --- Global Wrapper Function ---

def send_gmail(sender_email: str, app_password: str, recipient_email: str,
               subject: str, body: str) -> bool:
    """A global wrapper function to send a single email.

    This function handles the complete process:
    1. Connects to the Gmail SMTP server.
    2. Logs in.
    3. Sends the email.
    4. Disconnects.

    Args:
        sender_email (str): The Gmail address to send from.
        app_password (str): The 16-digit "App Password".
        recipient_email (str): The email address of the recipient.
        subject (str): The subject line of the email.
        body (str): The plain-text content of the email.

    Returns:
        bool: True if the email was sent successfully, False otherwise.
    """
    logger.info("--- Using global send_gmail function ---")
    try:
        # Use the class as a context manager
        with GmailSender(sender_email, app_password) as mailer:
            mailer.send_email(recipient_email, subject, body)
        logger.info("--- Global function complete ---")
        return True
    except Exception as e:
        # The class methods already log the specific error
        logger.error("Global function send_gmail() failed: %s", e)
        return False


# --- Example Usage ---

if __name__ == "__main__":
    logger.info("\n--- Testing Global Function ---")
    try:
        success = send_gmail(
            sender_email=Config.SENDER_EMAIL_ADDRESS,
            app_password=Config.SENDER_EMAIL_PASSWORD,
            recipient_email="r.harikeshav@gmail.com",
            subject="Test from Global Function",
            body="Hello! This email was sent using the send_gmail() wrapper function."
        )
        logger.info("Global function test result: %s", "Success" if success else "Failed")

    except Exception as e:
        logger.error("Unhandled exception during global function test: %s", e)
