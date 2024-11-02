
from libraries.utilities.utils import load_secret_file
from libraries.utilities.utils import load_yaml_file_to_dict, get_config_file_path, get_domain_from_email

from loguru import logger
from threading import Lock
from yaml import YAMLError
from json import JSONDecodeError
from google.oauth2 import service_account
from googleapiclient.discovery import build

class ConfigurationException(Exception):
    pass

class FailedToLoadSecretFile(ConfigurationException):
    def __init__(self, filename: str, original_exception: Exception):
        self.message = f"Failed to load the provided Google API secret file: '{filename}'. Please ensure the filepath is correct, and the JSON is valid.  Setting-Up a Secret File Guide: https://developers.google.com/zero-touch/guides/customer/quickstart/python-service-account"
        self.filename = filename
        self.original_exception = original_exception
        super().__init__(self.message + f"\nOriginal exception: {original_exception}")

class NoConfigurationsLoaded(ConfigurationException):
    def __init__(self):
        self.message = "No configurations were loaded due to previous errors. Please review and resolve the error messages above, then try again."
        super().__init__(self.message)


class FailedToLoadYAMLConfig(ConfigurationException):
    def __init__(self, filename: str, original_exception: Exception):
        self.filename = filename
        self.original_exception = original_exception
        self.message = f"Failed to load the provided file: {filename}. Please ensure the filepath is correct, and the YAML is valid.. Syntax Guide: https://docs.ansible.com/ansible/latest/reference_appendices/YAMLSyntax.html"
        super().__init__(self.message)

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
        return service_account.Credentials.from_service_account_file(self.secret_file, scopes=self.scopes)


class GoogleAuthenticationHandler:
    """ Class used to load multiple Google Service accounts and assign 
    domains to the proper authentication object
    """

    def __init__(self):
        self.domain_mapping: dict = {}
        self.loaded_services: dict = {}
        self.yaml_data = {}
        self.lock = Lock() 
        self.__load()

    def __load(self) -> None:
        """ 
        Calls __load_yaml_from_config() and __load_service_accounts()
        """
        self.__load_yaml_from_config()
        self.__load_service_accounts()

    def __load_yaml_from_config(self) -> None:
        """ 
        Loads the `/configuration/config.yaml` file into `self.yaml_data`

        :raises: FailedToLoadYAMLConfig if the file could not be read OR parsed
        """
        filename = get_config_file_path()
        try:
            self.yaml_data = load_yaml_file_to_dict(filename)
        except (FileNotFoundError, YAMLError) as e:
            raise FailedToLoadYAMLConfig(filename, e)
        
    def __load_service_accounts(self) -> None:
        """ 
        Assigns the dictionary from `__load_data_from_config()` to `self.config`
        """
        for service_account in self.yaml_data["google_service_accounts"]:
            try:
                google_configuration = GoogleAuthentication(service_account)
            except FailedToLoadSecretFile as e:
                logger.error(e.message)
                continue
            for domain in google_configuration.domains:
                self.domain_mapping[domain] = google_configuration

        if not self.domain_mapping:
            raise NoConfigurationsLoaded

    def get_service_for_user(self, user_email: str, service_name: str, service_version: str = "v1"):
        """
        Loads a Google API service (e.g., Gmail) for the specified user.
        """
        domain_name = get_domain_from_email(user_email)
        if not domain_name:
            raise ValueError(f"Invalid email format or domain missing in '{user_email}'.")

        authentication_obj = self.domain_mapping.get(domain_name)
        if not authentication_obj:
            raise KeyError(f"No authentication configuration found for domain '{domain_name}'.")

        cache_key = f"{domain_name}-{service_name}-{service_version}"

        # Use a lock to safely access and modify `loaded_services`
        with self.lock:
            if cache_key in self.loaded_services:
                return self.loaded_services[cache_key]

            service = build(service_name, service_version, credentials=authentication_obj.get_credentials())
            self.loaded_services[cache_key] = service

        
