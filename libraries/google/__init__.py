from libraries.google.authentication import GoogleAuthenticationHandler
from libraries.google.google_classes import LoginEvent
from googleapiclient.errors import HttpError
from google.auth.exceptions import RefreshError

class GoogleException(Exception):
    pass

class FailedToFindInternalID(GoogleException):
    def __init__(self, message_id: str, affected_user: str):
        self.message = f"Failed to find the internal message ID from the provided id: '{message_id}' for the user {affected_user}"
        super().__init__(self.message)

class DelegationDeniedException(GoogleException):
    def __init__(self, affected_user: str):
        self.message = f"Delegation denied for the user {affected_user}. Is this an Admin Users? Please check user permissions."
        super().__init__(self.message)

class MissingScopeFromConfig(GoogleException):
    def __init__(self, affected_user: str, function_name: str, e: Exception):
        self.message = f"Failed to call {function_name} for {affected_user}. You are most likely missing a Google API scope in the `config.yaml`. Please refrence the README for more information about API scopes."
        self.error = e
        super().__init__(self.message)

class MissingScopeFromClient(GoogleException):
    def __init__(self, affected_user: str, function_name: str, e: Exception):
        self.message = f"Failed to call {function_name} for {affected_user}. You are most likely forgetting to add the needed scope to the client. Link to Admin Setting: https://admin.google.com/u/3/ac/owl/domainwidedelegation. Please read the permission section in the README."  
        self.error = e
        super().__init__(self.message)

class WeakPassword(GoogleException):
    def __init__(self, affected_user: str):
        self.message = f"Failed to modifiy {affected_user} password the provided one was too weak."
        super().__init__(self.message)

class CantSuspendSelf(GoogleException):
    def __init__(self, affected_user: str):
        self.message = f"Failed to suspend: {affected_user}. This is the same user as the account performing API actions."
        super().__init__(self.message)

def handle_http_error(error: HttpError, user: str = None, function_name: str = None, message_id: str = None):
    """
    Handles HttpError and raises appropriate custom exceptions based on error content and status.
    
    :param error: The HttpError encountered during API calls.
    :param user: The user involved in the API call.
    :param function_name: The function name where the error occurred.
    :param message_id: The message ID related to the error, if applicable.
    """
    error_content = error.content.decode()
    print(error_content)
    if error.resp.status == 403:
        if 'Delegation denied' in error_content:
            raise DelegationDeniedException(user) from error
        elif 'Request had insufficient authentication scopes.' in error_content:
            raise MissingScopeFromConfig(user, function_name, error) from error
        elif 'Insufficient Permission':
            raise MissingScopeFromClient(affected_user=user, function_name=function_name, e=error)
    elif error.resp.status == 400:
        if 'Invalid Password' in error_content:
            raise WeakPassword(user)
        if 'Admin cannot suspend self' in error_content:
            raise CantSuspendSelf(user)
    elif error.resp.status == 404:
        raise FailedToFindInternalID(message_id, user) from error
    else:
        raise error

def handle_google_error(error: Exception, user: str, function_name: str):
    """ 
    Handles a custom Google Exception and raises the appopriate custom exceptions based on error content and status.
    :param error: The Google exception to handle.
    :param user: The involved user in the API call.
    :param function_name: The name of the function to call
    """
    if "Client is unauthorized to retrieve access tokens using this method" in str(error):
        raise MissingScopeFromClient(user, function_name, error)

class Google:
    def __init__(self):
        self.auth_handler = GoogleAuthenticationHandler()

    def get_message_id_from_export_id(self, message_id: str, user: str) -> str:
        """ Fetches the internal message ID from the provided id of the email in the Google
        Log Search export. The message_id from the `EmailLogEntry` class does not
        work with the google gmail SDK. 
        :param message_id: The message id from the export to fetch
        :param user: The user the message belongs to
        :return: the internal ID that works with the Google SDK
        :raises FailedToFindInternalID: If no ID was found
        :raises DelegationDeniedException: If delegation is denied for the user
        """
        try:
            gmail_service = self.auth_handler.get_service_for_user(user, "gmail")
            response = gmail_service.users().messages().list(
                userId=user,
                q=f'rfc822msgid:"{message_id}"'
            ).execute()
            if 'messages' in response:
                return response['messages'][0]['id']
            raise FailedToFindInternalID(message_id, user)
        except HttpError as error:
            handle_http_error(error, user, "get_message_id_from_export_id")
        except RefreshError as error:
            handle_google_error(error, user, "reset_password")
            
    def delete_email(self, message_id: str, user: str) -> bool:
        """
        Deletes the provided email out of the users inbox

        :param message_id: The Email message ID to delete
        :param user: The email of the user to delete the message in their inbox
        :return: True if the email was deleted from the affected users inbox
        """
        internal_id = self.get_message_id_from_export_id(message_id, user)
        gmail_service = self.auth_handler.get_service_for_user(user, "gmail")
        gmail_service.users().messages().delete(userId=user, id=internal_id).execute()
        return True
    
    def bulk_delete_emails(self, message_ids: list, user: str) -> bool:
        """
        Deletes multiple emails from the specified user's inbox.
        
        :param message_ids: List of message ids to search in the users inbox.
        :param user: The email of the user whose inbox is being cleaned.
        :return: True if all emails were successfully deleted.
        """
        results = []
        for message_id in message_ids:
            results.append(self.delete_email(message_id, user))
        return all(results)

    def mark_email_as_spam(self, message_id: str, user: str) -> bool:
        """
        Moves a specific email to a quarantine label/folder for the user.
        
        :param message_id: The Email message ID to quarantine.
        :param user: The email of the user whose message is being quarantined.
        :return: True if the email was successfully quarantined.
        """
        internal_id = self.get_message_id_from_export_id(message_id, user)
        gmail_service = self.auth_handler.get_service_for_user(user, "gmail")
        gmail_service.users().messages().modify(
            userId=user,
            id=internal_id,
            body={'removeLabelIds': ['INBOX'], 'addLabelIds': ['SPAM']}
        ).execute()
        return True

    def bulk_mark_email_as_spam(self, message_ids: list, user: str) -> bool:
        """
        Moves a specific email to a quarantine label/folder for the user.
        
        :param message_ids: The Email message IDs to quarantine.
        :param user: The email of the user whose message is being quarantined.
        :return: True if the email was successfully quarantined.
        """
        results = []
        for message_id in message_ids:
            results.append(self.mark_email_as_spam(message_id, user))
        return all(results)

    def __modify_suspended(self, value: bool, user: str) -> bool:
        """ Modifies the user attribute `suspended` and sets it to the provided value
        :param value: The value to set the suspended
        :param user: The email of the user to modify
        :return: True if the `suspended` variable is modified
        """
        try:
            admin_service = self.auth_handler.get_service_for_user(user, "admin", "directory_v1")
            admin_service.users().update(userKey=user, body={'suspended': value}).execute()
            return True
        except HttpError as error:
            handle_http_error(error, user)
        except RefreshError as error:
            handle_google_error(error, user, "__modify_suspended")
    def suspend_user(self, user: str) -> bool:
        """ 
        Suspends the provided user in Google
        
        :param user: The email of the user to suspend
        :return: True if the user was suspended
        """
        return self.__modify_suspended(True, user)
    
    def unsuspend_user(self, user: str) -> bool:
        """ 
        Unsuspend the provided user in Google
        
        :param user: The email of the user to unsuspend
        :return: True if the user was unsuspended
        """
        return self.__modify_suspended(False, user)

    def get_logins(self, user: str) -> list:
        """ 
        Fetches the provided users login events
        :param user: The user to process
        :return: a list of `Login` objects `is_suspicious` attribute is True
        """
        logins = []
        try:
            admin_service = self.auth_handler.get_service_for_user(user, "admin", "reports_v1")
            response = admin_service.activities().list(
                userKey='all',
                applicationName='login',
                eventName='login_failure',
            ).execute()
        except HttpError as error:
            handle_http_error(error, user, "get_logins")
        except RefreshError as error:
            handle_google_error(error, user, "get_logins")
        
        page_token = None

        while True:
            response = admin_service.activities().list(
                userKey='all',
                applicationName='login',
                pageToken=page_token
            ).execute()
            if 'items' in response:
                for event in response['items']:
                    if isinstance(event, dict):
                        login_event = LoginEvent(event)
                        if not login_event.is_suspicious:
                            continue
                        logins.append(login_event)
            page_token = response.get('nextPageToken')
            if not page_token:
                break
        return logins
    
    def get_suspicious_logins(self, user: str) -> list:
        """ 
        Fetches the provided users suspicious logins
        
        :param user: The user to process
        :return: a list of `Login` objects whese the 
        """
        suspicous_logins = []
        logins = self.get_logins(user)
        for login in logins:
            if login.is_suspicous:
                suspicous_logins.append(login)
        return suspicous_logins
    
    def reset_password(self, user: str, new_password: str, force_password_change: bool = False) -> bool:
        """ 
        Resets the provided users password
        
        :param user: The provided user to reset the password for
        :param new_password: The new password to assign the user
        :param force_password_change: If set to False, the end-user will not be prompted to reset their password
        :return: True if the users password was successfully reset
        """
        try:
            admin_service = self.auth_handler.get_service_for_user(user, "admin", "directory_v1")
            admin_service.users().update(
                userKey=user,
                body={
                    'password': new_password,
                    'changePasswordAtNextLogin': force_password_change
                }
            ).execute()
            return True
        except HttpError as error:
            handle_http_error(error, user, "reset_password")
        except RefreshError as error:
            handle_google_error(error, user, "reset_password")

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

    # def assess_user_risk(self, user: str, email_log) -> int:
    #     """
    #     Calculates a risk score for the specified user based on recent activity.
        
    #     :param user: The email of the user to assess.
    #     :return: An integer risk score for the user.
    #     """
