from libraries.google.parser import GoogleLogParser
from libraries.google.reporter import Reporter
from libraries.utilities.utils import display_logo
from argparse import ArgumentParser

VERSION = "dev 0.0.0"
SCRIPT_NAME = "Google: Phishing Report Generator"
display_logo(SCRIPT_NAME, VERSION)

LOG_PARSER = GoogleLogParser()
REPORTER = Reporter()

def yn(prompt: str) -> bool:
    """ 
    Asks the end user a question and awaits for a yes/no response

    :param prompt: The question to ask the user
    :return: True if the user responded with yes
    """
    response = input(prompt + " (y/n): ")
    return response.lower() in ["y", "yes"]

def get_multiple_responses(prompt: str) -> list:
    """ 
    Prompts the user a question until they are done
    :param prompt: The question to ask each time
    :return: a list of responses
    """
    responses = []
    while True:
        response = input(prompt + " (type 'stop' to quit) ")
        if response.lower() == "stop":
            return responses
        responses.append(response)

def wizard():
    """ 
    The wizard that prompts the end-user additional questions to add more substance
    to the report
    :return: attributes that can be passed to `ingest_custom_attributes`
    """
    custom_attributes = {}
    if yn("Did apply any mitigations and would you like to display them in your report?"):
        custom_attributes["mitigations"] = get_multiple_responses("Please provided a quick bullet point sentence")
    if yn("Would you like to add custom title?"):
        custom_attributes["title"] = input("Custom Title: ")
    if yn("Would you like to add additional information about the author?"):
        custom_attributes["author"] = input("Author Name: ")
        custom_attributes["author_title"] = input("Authors Job Title: ")
        custom_attributes["author_email"] = input("Authors Email: ")
        custom_attributes["author_date"] = input("Date of Report: ")
    return custom_attributes



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
    parser.add_argument(
        "--author",
        type=str,
        help="Specify the author name for the report."
    )
    parser.add_argument(
        "--title",
        type=str,
        default="Phishing Incident Report",
        help="Custom title for the report."
    )
    parser.add_argument(
        "--wizard",
        default=False,
        help="Prompts the end users questions to add additional information to the report.",
        action="store_true"

    )
    args = parser.parse_args()
    
    LOG_PARSER.read_export(args.logfile)
    if args.wizard:
        custom_attributes = wizard()
        REPORTER.ingest_custom_attributes(custom_attributes)
    REPORTER.generate_report(args.docx, LOG_PARSER.get_entries())

if __name__ == "__main__":
    main()
