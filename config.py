from configparser import ConfigParser


class FilterXMLConfig:

    @classmethod
    def open_config(cls) -> ConfigParser:
        cfg = ConfigParser()
        cfg.read('config.ini')
        return cfg

    @classmethod
    def iso_fmt(cls):
        return '%Y-%m-%dT%H:%M:%SZ'

    @classmethod
    def cvr_provider(cls):
        return cls.open_config().get('cvr', 'provider')

    @classmethod
    def cvrapi_api_key(cls):
        return cls.open_config().get('cvrapi', 'api_key')