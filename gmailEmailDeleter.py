"""
Deletes all emails from the provided export.
"""

from libraries.utilities.logger import logger, handle_exception
from libraries.utilities.utils import display_logo
from libraries.google.parser import GoogleLogParser
from libraries.google.authentication import NoConfigurationsLoaded
from libraries.google import Google
from argparse import ArgumentParser

VERSION = "dev 0.0.0"
SCRIPT_NAME = "Google Email Deleter"

display_logo(SCRIPT_NAME, VERSION)

LOG_PARSER = GoogleLogParser()

try:
    GOOGLE = Google()
except NoConfigurationsLoaded as e:
    handle_exception(
        e,
        "Cannot run the script: no valid configurations were found in `config.yaml`. "
        "Please ensure the provided secret file is correctly specified, and verify "
        "that the `config.yaml` file is properly formatted with no errors.",
        critical=True
    )

def delete_email(entry):
    """Attempts to delete an email and logs the result."""
    log_text = f"subject: {entry.message_id} from {entry.recipient_address}"
    if GOOGLE.delete_email(entry.message_id, entry.recipient_address):
        logger.info(f"Deleted {log_text}")
    else:
        logger.error(f"Failed to delete {log_text}")

def delete_all_emails(logfile: str):
    """Deletes all emails listed in the provided log file using multithreading."""
    try:
        LOG_PARSER.read_export(logfile)
        entries = LOG_PARSER.get_entries()
    except FileNotFoundError as e:
        handle_exception(e, "Log file not found. Please check the file path.", critical=True)

    for entry in entries:
        delete_email(entry)
    
def main():
    """Main function to parse arguments and initiate the delete_all_emails process."""
    parser = ArgumentParser(description="PRISM - Deletes all emails in the provided Google Email Log Search exports.")
    parser.add_argument(
        "--logfile", 
        type=str, 
        required=True,
        help="Path to the Google Log Search Export file to be processed."
    )
    args = parser.parse_args()

    delete_all_emails(args.logfile)

if __name__ == "__main__":
    main()
