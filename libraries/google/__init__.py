from libraries.google.authentication import GoogleAuthenticationHandler

class Google:
    def __init__(self):
        self.auth_handler = GoogleAuthenticationHandler()

    def delete_email(self, message_id: str, affected_user: str) -> bool:
        """
        Deletes the provided email out of the users inbox

        :param message_id: The Email message ID to delete
        :param affected_user: The email of the user to delete the message in their inbox
        :return: True if the email was deleted from the affected users inbox
        """
        gmail_service = self.auth_handler.get_service_for_user(affected_user, "gmail")
        response = gmail_service.users().messages().list(
            userId=affected_user,
            q=f'rfc822msgid:"{message_id}"'
        ).execute()
        if 'messages' in response:
            internal_id = response['messages'][0]['id']
            gmail_service.users().messages().delete(userId=affected_user, id=internal_id).execute()
            return True
    
    def bulk_delete_emails(self, message_ids: list, affected_user: str) -> bool:
        """
        Deletes multiple emails from the specified user's inbox.
        
        :param message_ids: List of message ids to search in the users inbox.
        :param affected_user: The email of the user whose inbox is being cleaned.
        :return: True if all emails were successfully deleted.
        """
        results = []
        for message_id in message_ids:
            results.append(self.delete_email(message_id, affected_user))
        return all(results)

    def mark_email_as_spam(self, message_id: str, affected_user: str) -> bool:
        """
        Moves a specific email to a quarantine label/folder for the user.
        
        :param message_id: The Email message ID to quarantine.
        :param affected_user: The email of the user whose message is being quarantined.
        :return: True if the email was successfully quarantined.
        """
        gmail_service = self.auth_handler.get_service_for_user(affected_user, "gmail")
        gmail_service.users().messages().modify(
            userId=affected_user,
            id=message_id, 
            body={'removeLabelIds': ['INBOX'], 'addLabelIds': ['SPAM']}
        ).execute()
        return True
    

    def bulk_mark_email_as_spam(self, message_ids: list, affected_user: str) -> bool:
        """
        Moves a specific email to a quarantine label/folder for the user.
        
        :param message_ids: The Email message IDs to quarantine.
        :param affected_user: The email of the user whose message is being quarantined.
        :return: True if the email was successfully quarantined.
        """
        results = []
        for message_id in message_ids:
            results.append(self.mark_email_as_spam(message_id, affected_user))
        return all(results)


    def suspend_user(self, user: str) -> bool:
        """ 
        Suspends the provided user in Google
        
        :param user: The email of the user to suspend
        :return: True if the user was suspended
        """

    def unsuspend_user(self, user: str) -> bool:
        """ 
        Unsuspend the provided user in Google
        
        :param user: The email of the user to unsuspend
        :return: True if the user was unsuspended
        """

    def get_suspicious_logins(self, user: str) -> list:
        """ 
        Fetches the provided users suspicious logins
        
        :param user: The user to process
        :return: a list of `Login` objects
        """

    def reset_password(self, user: str, new_password: str, force_password_change: bool = False) -> bool:
        """ 
        Resets the provided users password
        
        :param user: The provided user to reset the password for
        :param new_password: The new password to assign the user
        :param force_password_change: If set to False, the end-user will not be prompted to reset their password
        :return: True if the users password was successfully reset
        """

    def add_email_to_blacklist(self, email_address: str) -> bool:
        """
        Blacklists the provided email address to prevent future emails from this sender.
        
        :param email_address: The email address to blacklist.
        :return: True if the email address was successfully blacklisted.
        """

    # def notify_admin(self, message: str, user: str = None) -> bool:
    #     """
    #     Sends a notification to administrators with relevant incident details.
        
    #     :param message: The notification message to send.
    #     :param user: (Optional) The user involved in the incident.
    #     :return: True if the notification was successfully sent.
    #     """

    # def assess_user_risk(self, user: str) -> int:
    #     """
    #     Calculates a risk score for the specified user based on recent activity.
        
    #     :param user: The email of the user to assess.
    #     :return: An integer risk score for the user.
    #     """