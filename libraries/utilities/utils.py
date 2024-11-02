from yaml import safe_load
from json import load
from os.path import dirname, join, abspath


def get_config_file_path() -> str:
    """
    Returns the absolute path to the configuration file in the /configuration directory.

    :return: The full path to the .config.yaml file.
    """
    # Go back 3 directories
    base_dir = dirname(dirname(dirname(abspath(__file__))))
    config_path = join(base_dir, 'config.yaml')
    return abspath(config_path)

def load_yaml_file_to_dict(filename: str) -> dict:
    """
    Loads a YAML file and parses it as a dictionary.

    :param filename: The path to the YAML file to load.
    :return: A dictionary containing the parsed YAML data.
    :raises FileNotFoundError: If the specified file does not exist.
    :raises yaml.YAMLError: If there is an error parsing the YAML file.

    """
    with open(filename, 'r') as file:
        data = safe_load(file)
        return data if data is not None else {}
    
def load_secret_file(secret_file: str) -> dict:
    """
    Reads the Google API Secret JSON file and returns its contents as a dictionary.
    
    :param secret_file: The path to the JSON file.
    :return: A dictionary containing the parsed JSON data.
    :raises FileNotFoundError: If the file does not exist.
    :raises json.JSONDecodeError: If there is an error decoding the JSON file.
    """
    with open(secret_file, 'r') as file:
        return load(file)
    

def get_domain_from_email(email: str) -> str:
    """ Fetches the domain from the provided email
    :param email: the email to fetch the domain name from
    :return: the domain name with no @ symbol in front
    """
    return email.split("@")[1]

def get_owned_domains() -> list:
    """ Gatheres all domains from `config.yaml`
    :return: a list of domain names that are managed by the user
    """
    config_yaml = load_yaml_file_to_dict(get_config_file_path())
    domains = []
    for service_account in config_yaml.get("google_service_accounts"):
        google_domains = service_account.get("domains")
        if not google_domains:
            continue
        domains.extend(google_domains)
    return domains