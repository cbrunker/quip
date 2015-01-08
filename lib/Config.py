#
# Client configuration handler
#
from configparser import ConfigParser
import logging

class Configuration:
    """
    Return known configuration
    """

    def __init__(self, config='client.conf'):
        """

        @param config: Location of client configuration file
        @return: Configuration Object
        """
        self.configPath = config
        self.__loadConfig()

        # required fields and their defaults. Defaults are used when fields do not exist or contain invalid data
        self.required = {'verify': 1, 'download_directory': 'Downloads', 'max_chunk': 524288,
                         'request_expiry': 28, 'file_expiry': 7,
                         'host': '', 'tcp': 22012, 'idle_timeout': 30}

        self.__checkRequired()

    def save(self):
        """
        Save current config values to file
        """
        config = ConfigParser()
        config.read(self.configPath)
        for s in config.sections():
            for k, v in ((k, config[s][k]) for k in config[s] if not config[s][k].startswith('_')):
                config[s][k] = getattr(self, k.lower())

        with open(self.configPath, 'w') as newConfig:
            config.write(newConfig)

    def __checkRequired(self):
        """
        Check the config file for required fields and values. Warn and set defaults to missing fields or invalid values
        """

        for attribute, default in self.required.items():
            try:
                value = getattr(self, attribute)
                # enforce integer value compliance for specific items
                if type(default) is int:
                    try:
                        int(value)
                    except ValueError:
                        logging.warning("Invalid config value '{}' for item '{}', "
                                        "should be an integer. "
                                        "Setting item to default value '{}'".format(value, attribute, default))
            except AttributeError:
                logging.warning("Required config item '{}' not found, "
                                "setting item to default value '{}'".format(attribute, default))
                setattr(self, attribute, default)

    def __loadConfig(self):
        """
        Load config file into class attributes
        """
        config = ConfigParser()
        config.read(self.configPath)

        for s in config.sections():
            for k, v in ((k, config[s][k]) for k in config[s] if not config[s][k].startswith('_')):
                setattr(self, k.lower(), v)

    def _reload(self):
        """
        Reload config file
        """
        self.__loadConfig()
        self.__checkRequired()