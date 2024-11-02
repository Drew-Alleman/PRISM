from libraries.google.parser import GoogleLogParser
from libraries.google.reporter import Reporter
from argparse import ArgumentParser
LOG_PARSER = GoogleLogParser()
REPORTER = Reporter()

def main():
    parser = ArgumentParser(description="Generates a report from the provided Google Log Search Export")
    parser.add_argument("--docx", type=str, help="The file to store the report")
    parser.add_argument("--logfile", type=str, help="The Google Log Search Export to load")
    args = parser.parse_args()
    LOG_PARSER.read_export(args.logfile)
    REPORTER.generate_report(args.docx, LOG_PARSER.get_entries())


if __name__ == "__main__":
    main()