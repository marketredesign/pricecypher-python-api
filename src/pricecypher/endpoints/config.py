from pricecypher.endpoints.base_endpoint import BaseEndpoint
from pricecypher.models import ConfigSection, ConfigSectionWithKeys


class ConfigEndpoint(BaseEndpoint):
    """PriceCypher config service endpoints.

        :param RestClient client: HTTP client for making API requests.
        :param str users_base: (optional) Base URL for PriceCypher config service API.
            (defaults to https://config.pricecypher.com)
        """

    def __init__(self, client, dataset_id, users_base='https://config.pricecypher.com'):
        self.base_url = users_base
        self.client = client
        self.dataset_id = dataset_id

    def sections(self):
        """
        Dataset endpoints in user tool API.
        :rtype: DatasetsEndpoint
        """
        return SectionsEndpoint(self.client, self._url(['api/datasets', self.dataset_id, '/config/sections']))


class SectionsEndpoint(BaseEndpoint):
    """
    PriceCypher dataset endpoints in user tool API.
    """
    def __init__(self, client, base):
        self.client = client
        self.base_url = base

    def index(self) -> list[ConfigSection]:
        """List all available sections the user has access to.

        :return: list of datasets.
        :rtype list[Dataset]
        """
        return self.client.get(self._url(), schema=ConfigSection.Schema(many=True))

    def get(self, section_key) -> ConfigSectionWithKeys:
        return self.client.get(self._url(section_key), schema=ConfigSectionWithKeys.Schema(many=False))
