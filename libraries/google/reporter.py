import matplotlib.pyplot as plt
from docx import Document
from docx.shared import Inches

from libraries.utilities.utils import get_owned_domains, get_domain_from_email

class Reporter:
    def __init__(self):
        self.quarantined = 0
        self.delivered = 0
        self.viewed = 0
        self.marked_as_spam = 0
        self.bounced = 0
        self.emails_sent_to_external_domains = 0
        self.start_time = None
        self.senders = set()
        self.owned_domains = get_owned_domains()
    
    @property
    def summary_text(self):
        """Generates a summary of the provided events."""
        formatted_start_time = self.start_time.strftime("%I:%M %p")
        sender_text = f"{self.senders.pop()}" if len(self.senders) == 1 else "multiple users"
        
        internal_count = self.total_emails - self.emails_sent_to_external_domains
        if self.emails_sent_to_external_domains > 0:
            summary_intro = (
                f"At {formatted_start_time}, an email from {sender_text} was identified as a phishing attempt. "
                f"It was sent to a total of {self.total_emails} recipients, including "
                f"{internal_count} within our managed domains and {self.emails_sent_to_external_domains} external organizations."
            )
        else:
            summary_intro = (
                f"At {formatted_start_time}, an email from {sender_text} was identified as a phishing attempt. "
                f"It was sent to {self.total_emails} recipients within our managed domains."
            )
        
        if self.viewed > 0:
            viewed_text = f"Of these, {self.viewed} emails were viewed by the recipients."
        else:
            viewed_text = "Fortunately, none of the recipients within our managed domains opened the email."
        
        return f"{summary_intro} {viewed_text}"

    def generate_report(self, filename: str, entries: list) -> None:
        """
        Generates a report document after updating counts and creating a pie chart image.
        """
        self.__update_numbers(entries)
        self.__generate_pie_chart()
        self.__generate_docx(filename)

    def __update_numbers(self, entries: list) -> None:
        """
        Updates email status counts based on entries, processing each unique user only once.
        Prioritizes 'viewed', 'bounced', and 'quarantined' statuses, but counts 'delivered' 
        if no other status occurred for that user.
        """
        processed_users = {}
        self.start_time = None
        external_recipients = set() 

        for email_log in entries:
            recipient = email_log.recipient_address
            self.senders.add(email_log.sender)  

            if self.start_time is None or email_log.start_date < self.start_time:
                self.start_time = email_log.start_date

            if recipient not in processed_users:
                domain = get_domain_from_email(recipient)
                if domain not in self.owned_domains:
                    external_recipients.add(recipient)  

            if email_log.was_email_viewed:
                processed_users[recipient] = "viewed"
            elif email_log.was_email_bounced:
                processed_users.setdefault(recipient, "bounced")
            elif email_log.was_email_quarantined:
                if processed_users.get(recipient) not in ["viewed", "bounced"]:
                    processed_users[recipient] = "quarantined"
            elif email_log.was_email_delivered:
                processed_users.setdefault(recipient, "delivered")

        self.viewed = sum(1 for status in processed_users.values() if status == "viewed")
        self.bounced = sum(1 for status in processed_users.values() if status == "bounced")
        self.quarantined = sum(1 for status in processed_users.values() if status == "quarantined")
        self.delivered = sum(1 for status in processed_users.values() if status == "delivered")
        self.total_emails = len(processed_users)
        self.emails_sent_to_external_domains = len(external_recipients)

    def __generate_docx(self, filename: str) -> None:
        """ Generates a .docx report containing basic information about the incident. """
        doc = Document()
        doc.add_heading(f"{self.start_time.strftime('%m/%d/%Y')} Phishing Incident", level=1)
        doc.add_heading("Executive Summary", level=2)
        doc.add_paragraph(self.summary_text)
        doc.add_heading("Email Distribution Overview", level=2)
        doc.add_picture("chart.png", width=Inches(4.0))
        doc.save(filename)



    def __generate_pie_chart(self):
        """ Generates a static pie chart image for faster output. """
        labels = ['Viewed', 'Bounced', 'Quarantined', 'Delivered']
        values = [self.viewed, self.bounced, self.quarantined, self.delivered]
        filtered_labels = [label for label, value in zip(labels, values) if value > 0]
        filtered_values = [value for value in values if value > 0]
        plt.figure(figsize=(6, 6))
        
        def autopct_format(pct):
            total = sum(filtered_values)
            count = int(round(pct * total / 100.0))
            return f"{count}" 
        
        plt.figure(figsize=(6, 6))
        plt.pie(filtered_values, labels=filtered_labels, autopct=autopct_format, startangle=140)
        plt.title(f"Total Emails Delivered: {self.total_emails}")
        plt.savefig("chart.png")
        plt.close()
