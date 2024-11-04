from libraries.google.parser import GoogleLogParser
from libraries.google.reporter import Reporter
from libraries.utilities.utils import display_logo
from argparse import ArgumentParser

VERSION = "dev 0.0.0"
SCRIPT_NAME = "Google Email Deleter"
display_logo(SCRIPT_NAME, VERSION)

LOG_PARSER = GoogleLogParser()
REPORTER = Reporter()


def main():
    parser = ArgumentParser(description="PRISM - Generate a detailed report based on a Google Log Search Export file.")
    parser.add_argument(
        "--docx", 
        type=str, 
        required=True,
        help="Path to the DOCX file where the generated report will be saved."
    )
    parser.add_argument(
        "--logfile", 
        type=str, 
        required=True,
        help="Path to the Google Log Search Export file to be processed."
    )
    args = parser.parse_args()
    
    LOG_PARSER.read_export(args.logfile)
    REPORTER.generate_report(args.docx, LOG_PARSER.get_entries())

if __name__ == "__main__":
    main()