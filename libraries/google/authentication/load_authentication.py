""" This is an internal class used by the Google() class. This does not needs
to be loaded by an end user. This class loads the service accounts from `config.yaml`
"""

from libraries.google.authentication.authentication import GoogleAuthentication
from libraries.utilities.utils import load_yaml_file_to_dict, get_config_file_path, get_domain_from_email
from libraries.google.authentication.exceptions import FailedToLoadSecretFile, NoConfigurationsLoaded, FailedToLoadYAMLConfig

from yaml import YAMLError
from loguru import logger

from googleapiclient.discovery import build

class GoogleAuthenticationHandler:
    """ Class used to load multiple Google Service accounts and assign 
    domains to the proper authentication object
    """

    def __init__(self):
        self.domain_mapping: dict = {}
        self.loaded_services: dict = {}
        self.yaml_data = {}
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
        Loads a Google API service (e.g., Gmail) for the specified user. This function automatically 
        selects the appropriate authentication method based on the user's email.

        :param user_email: The email address of the user for whom to load the service.
        :param service_name: The name of the Google API service to initialize (e.g., 'gmail').
        :param service_version: The version of the service to load.
        :return: An authenticated service instance for the specified Google API.
        :raises ValueError: If the domain cannot be derived from user_email.
        :raises KeyError: If no authentication object exists for the user's domain.
        """
        domain_name = get_domain_from_email(user_email)
        if not domain_name:
            raise ValueError(f"Invalid email format or domain missing in '{user_email}'.")

        authentication_obj = self.domain_mapping.get(domain_name)
        if not authentication_obj:
            raise KeyError(f"No authentication configuration found for domain '{domain_name}'.")

        cache_key = f"{domain_name}-{service_name}-{service_version}"
        if cache_key in self.loaded_services:
            return self.loaded_services[cache_key]

        service = build(service_name, service_version, credentials=authentication_obj.get_credentials())
        self.loaded_services[cache_key] = service  
        return service
        