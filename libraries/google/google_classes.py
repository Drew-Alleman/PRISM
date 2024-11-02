
from datetime import datetime
from re import compile

class EmailLogEntry:
    def __init__(self, row_as_dict: dict):
        self.message_id = row_as_dict.get("Message ID")
        start_date = row_as_dict.get("Start date")
        end_date = row_as_dict.get("End date")
        self.end_date = datetime.strptime(end_date, "%Y/%m/%d %H:%M:%S %Z")
        self.start_date = datetime.strptime(start_date, "%Y/%m/%d %H:%M:%S %Z")
        self.sender = row_as_dict.get("Sender")
        self.message_size = int(row_as_dict.get("Message size", 0))
        self.subject = row_as_dict.get("Subject")
        self.direction = row_as_dict.get("Direction")
        self.attachments = int(row_as_dict.get("Attachments", 0))
        self.recipient_address = row_as_dict.get("Recipient address")
        self.event_target = row_as_dict.get("Event target")
        self.event_date = row_as_dict.get("Event date")
        self.event_status = row_as_dict.get("Event status")
        self.event_target_ip_address = row_as_dict.get("Event target IP address")
        self.has_encryption = row_as_dict.get("Has encryption")
        self.event_smtp_reply_code = row_as_dict.get("Event SMTP reply code")
        self.event_description = row_as_dict.get("Event description")
        self.client_type = row_as_dict.get("Client Type")
        self.device_user_session_id = row_as_dict.get("Device User Session ID")

    @property
    def email_has_attachments(self) -> bool:
        return self.attachments >= 1

    @property
    def email_is_encrypted(self) -> bool:
        return self.has_encryption == "Encrypted"

    @property
    def was_email_marked_as_spam(self) -> bool:
        """ 
        :return: True if the email was marked as spam in the user inbox
        """
        return self.event_status == "Marked spam"
    
    @property
    def was_email_quarantined(self) -> bool:
        """
        :return: True if the email was Quarantined by Google
        """
        return self.event_status == "Quarantined"
    
    @property
    def was_email_bounced(self) -> bool:
        """
        :return: True if the email was bounced

        The message bounced because of issues with the email account. Issues can include: your IP address is blocked, 
        your account reached sending or receiving limits, or the message violates a compliance or routing policy rule. 

        """
        return self.event_status == "BOUNCED"

    @property
    def was_email_viewed(self) -> bool:
        """
        :return: True if the email was bounced

        The message bounced because of issues with the email account. Issues can include: your IP address is blocked, 
        your account reached sending or receiving limits, or the message violates a compliance or routing policy rule. 

        """
        return self.event_status == "VIEWED"
    
    @property
    def was_email_delivered(self) -> bool:
        """
        :return: True if the email succesfully landed in the users inbox
        """
        return self.event_status == "DELIVERED"
    
    def does_email_subject_match_regex(self, regex_str: str) -> bool:
        """ Checks if the regex pattern matches the email subject
        :param regex_str: The regex pattern to use
        :return: True if the regex query matches the email subject
        """
        if not self.subject:
            return False
        
        pattern = compile(regex_str)
        return bool(pattern.search(self.subject))
