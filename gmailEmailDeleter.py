"""
Deletes all emails from the provided export.
"""

from libraries.utilities.logger import logger, handle_exception
from libraries.utilities.utils import display_logo
from libraries.google.parser import GoogleLogParser
from libraries.google.authentication import NoConfigurationsLoaded
from libraries.google import Google, FailedToFindInternalID, DelegationDeniedException
from argparse import ArgumentParser

VERSION = "dev 0.0.0"
SCRIPT_NAME = "Google: Email Deleter"

display_logo(SCRIPT_NAME, VERSION)
logger.debug(f"Starting: gmailEmailDeleter.py version: {VERSION}")

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
    """Attempts to delete an email and logs the result.

    :param entry: The email log entry containing the message ID and recipient address.
    """
    log_text = f"email: {entry.message_id} from {entry.recipient_address}"
    try:
        if GOOGLE.delete_email(entry.message_id, entry.recipient_address):
            logger.info(f"Deleted {log_text}")
        else:
            logger.error(f"Failed to delete {log_text}")
    except (FailedToFindInternalID, DelegationDeniedException) as e:
        handle_exception(e, e.message)


def delete_all_emails(logfile: str):
    """Deletes all emails listed in the provided log file.

    :param logfile: Path to the Google Log Search Export file to be processed.
    """
    try:
        LOG_PARSER.read_export(logfile)
        entries = LOG_PARSER.get_entries()
        logger.debug(f"Loaded {len(entries)} entries from {logfile}. Removing duplicates...")
        entries = LOG_PARSER.stabilize()
        logger.debug(f"Stabilized entries count: {len(entries)}")
    except FileNotFoundError as e:
        handle_exception(e, "Log file not found. Please check the file path.", critical=True)
        return

    for entry in entries:
        delete_email(entry)


def parse_arguments() -> ArgumentParser:
    """Parses command-line arguments.

    :return: Parsed command-line arguments.
    """
    parser = ArgumentParser(description="PRISM - Deletes all emails in the provided Google Email Log Search exports.")
    parser.add_argument(
        "--logfile",
        type=str,
        required=True,
        help="Path to the Google Log Search Export file to be processed."
    )
    return parser.parse_args()


def main():
    """Main function to parse arguments and initiate the delete_all_emails process."""
    args = parse_arguments()
    delete_all_emails(args.logfile)


if __name__ == "__main__":
    main()
