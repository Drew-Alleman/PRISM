from libraries.google.google_classes import EmailLogEntry

import csv

class GoogleLogParser:
    def __init__(self):
        self.log_entries = []

    def read_export(self, filename: str) -> list:
        """
        Reads the CSV file and populates log entries with EmailLogEntry instances.
        :param filename: The Gmail Log search file to read
        """
        with open(filename, mode='r', newline='', encoding='utf-8') as csv_file:
            csv_reader = csv.DictReader(csv_file)
            for row in csv_reader:
                if row.get("Message ID"):
                    entry = EmailLogEntry(row)
                    self.log_entries.append(entry)

        return self.log_entries
    
    def read_exports(self, filenames: list[str]) -> list:
        """
        Reads the CSV files and populates log entries with EmailLogEntry instances.
        :param filenamse: The Gmail Log search files to read
        """
        for filename in filenames:
            self.read_export(filename)
        return self.log_entries

    def stabilize(self) -> list[EmailLogEntry]:
        """Removes duplicate lines from `self.log_entries`. A duplicate line
        is defined as an entry with the same message ID and recipient address.
        
        :return: A list of unique EmailLsogEntry objects based on message ID and recipient address.
        """
        unique_entries = []
        seen_entries = set()
        for entry in self.log_entries:
            if (entry.message_id, entry.recipient_address) not in seen_entries:
                unique_entries.append(entry)
                seen_entries.add((entry.message_id, entry.recipient_address))
        
        return unique_entries


    def get_entries(self) -> list[EmailLogEntry]:
        """ 
        returns log entires loaded from GoogleLogParser.read_export()

        :return: a list of EmailLogEntry's
        """
        return self.log_entries
    
