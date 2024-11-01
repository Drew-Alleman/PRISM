
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