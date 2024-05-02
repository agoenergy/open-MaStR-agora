#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
open-MaStR - Main file

Bulk: Download XML-Dump and fill in local SQLite database.
API: Download latest entries using the SOAP-API.

SPDX-License-Identifier: AGPL-3.0-or-later
"""
import os
import time
import logging
from logging.handlers import SMTPHandler
from sshtunnel import SSHTunnelForwarder
from dotenv import load_dotenv
from sqlalchemy import create_engine
from open_mastr import Mastr
import os


load_dotenv()
EMAIL_FROM_USR = os.getenv("EMAIL_FROM_USR")
EMAIL_FROM_PASS = os.getenv("EMAIL_FROM_PASS")
EMAIL_TO = os.getenv("EMAIL_TO")

smtp_handler = SMTPHandler(
    mailhost=("mail.dotplex.com", 25),
    secure=(),
    credentials=(EMAIL_FROM_USR, EMAIL_FROM_PASS),
    fromaddr=EMAIL_FROM_USR,
    toaddrs=EMAIL_TO,
    subject="system error - log",
)
smtp_handler.setLevel(logging.ERROR)
mail_handler = logging.getLogger(__name__)
mail_handler.addHandler(smtp_handler)
mail_handler.setLevel(logging.ERROR)


def retry_function(func, max_retries=3, retry_delay=1):
    retries = 0
    while retries < max_retries:
        try:
            result = func()
            return result  # If the function succeeds, return its result
        except Exception as e:
            print(f"Attempt {retries + 1} failed with error: {str(e)}")
            time.sleep(retry_delay)  # Wait for a short period before retrying
            retries += 1

    print(f"Function failed after {max_retries} attempts")
    raise Exception("Max retries exceeded")


def mastr_temp_update():
    """Update the temporary MaStR version."""

    SSH_ADDRESS = os.getenv("SSH_HOST")
    SSH_PORT = int(os.getenv("SSH_PORT"))
    PATH_PKEY_SSH = os.getenv("PATH_PKEY_SSH")
    SSH_USERNAME = os.getenv("SSH_USERNAME")
    SSH_PASSPHRASE = os.getenv("SSH_PASSPHRASE")
    LOCAL_HOST = os.getenv("LOCAL_HOST")
    LOCAL_PORT = int(os.getenv("LOCAL_PORT"))
    USERNAME_POSTGRES = os.getenv("USERNAME_POSTGRES")
    PASSWORD_POSTGRES = os.getenv("PASSWORD_POSTGRES")
    POSTGRES_DB = os.getenv("POSTGRES_DB")
    FACT_SCHEMA = os.getenv("FACT_SCHEMA")

    server = SSHTunnelForwarder(
        ssh_address_or_host=(SSH_ADDRESS, SSH_PORT),
        ssh_pkey=PATH_PKEY_SSH,
        ssh_username=SSH_USERNAME,
        ssh_password=SSH_PASSPHRASE,
        remote_bind_address=(LOCAL_HOST, LOCAL_PORT),
    )
    server.start()
    LOCAL_PORT = str(server.local_bind_port)

    engine = create_engine(
        f"postgresql://{USERNAME_POSTGRES}:{PASSWORD_POSTGRES}@{LOCAL_HOST}:"
        f"{LOCAL_PORT}/{POSTGRES_DB}",
        echo=True,
        connect_args={"options": f"-c search_path={FACT_SCHEMA}"}
        #execution_options={"schema_translate_map": {None: FACT_SCHEMA}},
    )

    db = Mastr(engine=engine)
    db.download(data=["solar", "wind", "hydro", "biomass", "permit"])


if __name__ == "__main__":
    # update MaStR
    try:
        result = retry_function(mastr_temp_update)
        print(f"Function succeeded with result: {result}")
    except Exception as err:
        mail_handler.exception(
            f"After three retries MaStR couldn't be updatet with {err}."
        )