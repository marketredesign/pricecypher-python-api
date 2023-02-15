from pricecypher.endpoints.base_endpoint import BaseEndpoint
from pricecypher.models import Dataset
from pricecypher.rest import RestClient


class UsersEndpoint(BaseEndpoint):
    """PriceCypher endpoints in user tool.

    :param RestClient client: HTTP client for making API requests.
    :param str users_base: (optional) Base URL for PriceCypher user tool API.
        (defaults to https://users.pricecypher.com)
    """

    def __init__(self, client, users_base='https://users.pricecypher.com'):
        self.base_url = users_base
        self.client = client

    def datasets(self):
        """
        Dataset endpoints in user tool API.
        :rtype: DatasetsEndpoint
        """
        return DatasetsEndpoint(self.client, self._url('api/datasets'))


class DatasetsEndpoint(BaseEndpoint):
    """
    PriceCypher dataset endpoints in user tool API.
    """
    def __init__(self, client, base):
        self.client = client
        self.base_url = base

    async def index(self) -> list[Dataset]:
        """List all available datasets the user has access to.

        :return: list of datasets.
        :rtype list[Dataset]
        """
        return await self.client.get(self._url(), schema=Dataset.Schema(many=True))
