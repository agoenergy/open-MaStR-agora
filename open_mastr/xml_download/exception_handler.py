# -*- coding: utf-8 -*-
"""Handle exceptions across DataProcessingTools."""
import logging
import os
from dotenv import load_dotenv
from logging.handlers import SMTPHandler
from requests.exceptions import HTTPError
from sqlalchemy.exc import OperationalError, ProgrammingError
from open_mastr.utils.config import setup_logger

load_dotenv()
email_from_user = os.getenv("EMAIL_FROM_USR")
email_from_pass = os.getenv("EMAIL_FROM_PASS")
email_to = os.getenv("EMAIL_TO")

# Define a flag to control whether to send error emails or not.
# Can be set to "False" for testing/debugging to avoid receiving too many emails.
SEND_ERROR_EMAILS = True

# Write logs to the "*.log" file.
logger = setup_logger()

# Send logs via email using SMTP only when the corresponding flag is set to True.
if SEND_ERROR_EMAILS:
    smtp_handler = SMTPHandler(
        mailhost=("mail.dotplex.com", 25),
        secure=(),
        credentials=(email_from_user, email_from_pass),
        fromaddr=email_from_user,
        toaddrs=email_to,
        subject="system error - log",
    )
    smtp_handler.setLevel(logging.ERROR)
    mail_handler = logging.getLogger(__name__)
    mail_handler.addHandler(smtp_handler)
    mail_handler.setLevel(logging.ERROR)

# Define a dictionary to map HTTP error codes to their corresponding messages.
HTTP_ERROR_MESSAGES = {
    400: "Invalid request due to HTTPError 400 Bad Request.",
    401: "Unauthorized response due to HTTPError 401.",
    503: "Stop execution due to HTTPError 503. The server is unavailable.",
}


def download_exception_handler(func):
    """Exception decorator."""

    def inner_function(*args, **kwargs):
        """Capture and log exceptions."""
        try:
            func(*args, **kwargs)
        except TypeError as err:
            logger.exception("TypeError:%s", err)
            if SEND_ERROR_EMAILS:
                mail_handler.exception("TypeError:%s", err)
        except HTTPError as err:
            if hasattr(err, "code"):
                error_message = HTTP_ERROR_MESSAGES.get(err.code)
                if error_message:
                    logger.exception(error_message)
                else:
                    logger.exception("HTTPError:%s", err)
                    if SEND_ERROR_EMAILS:
                        mail_handler.exception("HTTPError:%s", err)
        except TimeoutError as err:
            logger.exception("TimeoutError:%s", err)
            if SEND_ERROR_EMAILS:
                mail_handler.exception("TimeoutError:%s", err)

    return inner_function


def db_exception_handler(func):
    """Exception decorator."""

    def inner_function(*args, **kwargs):
        """Capture and log exceptions."""
        try:
            func(*args, **kwargs)
        except TypeError as err:
            logger.exception("TypeError:%s", err)
            if SEND_ERROR_EMAILS:
                mail_handler.exception("TypeError:%s", err)
        except TimeoutError as err:
            logger.exception("TimeoutError:%s", err)
            if SEND_ERROR_EMAILS:
                mail_handler.exception("TimeoutError:%s", err)
        except OperationalError as err:
            logger.exception("OperationalError:%s", err)
            if SEND_ERROR_EMAILS:
                mail_handler.exception("OperationalError:%s", err)
        except ProgrammingError as err:
            logger.exception("ProgrammingError:%s", err)
            if SEND_ERROR_EMAILS:
                mail_handler.exception("ProgrammingError:%s", err)

    return inner_function
