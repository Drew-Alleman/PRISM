
from libraries.utilities.utils import load_secret_file
from libraries.google.authentication.exceptions import FailedToLoadSecretFile

from json import JSONDecodeError
from google.oauth2 import service_account

class GoogleAuthentication:
    def __init__(self, data: dict):
        """
        Initializes Google configuration attributes based on the provided data.
        """
        self.domains = data.get('domains', [])
        self.secret_file = data.get('secret_file')
        self.name = data.get('name')
        self.secret = None
        self.scopes = data.get('scopes', [])
        self.__check_secret_file()

    def __check_secret_file(self) -> None:
        """
        Checks to see if the provided secret file is valid.
        """
        try:
            _ = load_secret_file(self.secret_file)
        except (FileNotFoundError, JSONDecodeError) as e:
            raise FailedToLoadSecretFile(self.secret_file, e)

    def get_credentials(self):
        """ Fetches the service account credentials file from the provided file
        """
        return service_account.Credentials.from_service_account_file(self.secret_file, scopes=self.scopes )