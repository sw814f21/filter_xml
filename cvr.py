

class CVRHandlerBase:
    URL = ''

    def append_data(self):
        pass


class CVRHandlerVirk(CVRHandlerBase):
    URL = ''

    def append_data(self):
        pass


class CVRHandlerCVRAPI(CVRHandlerBase):
    URL = ''

    def append_data(self):
        pass


class CVRHandlerScrape(CVRHandlerBase):
    URL = ''

    def append_data(self):
        pass


def get_cvr_handler(provider: str) -> CVRHandlerBase:
    if provider == 'cvrapi':
        return CVRHandlerCVRAPI()
    elif provider == 'virk':
        return CVRHandlerVirk()
    elif provider == 'scrape':
        return CVRHandlerScrape()
    else:
        raise KeyError(f'provider \"{provider}\" is invalid, please choose one of '
                       f'[ cvrapi | virk | scrape ]')