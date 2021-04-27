from configparser import ConfigParser


class FilterXMLConfig:
    """
    Config class for filter_xml

    Every method should be decorated as a class method
    """

    @classmethod
    def open_config(cls) -> ConfigParser:
        """
        Open config file
        """
        cfg = ConfigParser()
        cfg.read('config.ini')
        return cfg

    @classmethod
    def iso_fmt(cls) -> str:
        """
        Date and time formatting according to ISO 8601 standard

        https://en.wikipedia.org/wiki/ISO_8601
        """
        return '%Y-%m-%dT%H:%M:%SZ'

    @classmethod
    def cvr_provider(cls) -> str:
        """
        Retrieves CVR provider from config file
        """
        return cls.open_config().get('cvr', 'provider')

    @classmethod
    def cvrapi_api_key(cls) -> str:
        """
        Retrieves cvrapi API key from config file
        """
        return cls.open_config().get('cvrapi', 'api_key')

    @classmethod
    def data_endpoint(cls) -> str:
        """
        Retrieves the data endpoint from config file
        """
        return cls.open_config().get('filter_xml', 'data_endpoint')