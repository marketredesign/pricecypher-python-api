from pricecypher.models import Dataset
from pricecypher.rest import RestClient


class UsersEndpoint(object):
    """PriceCypher dataset endpoints in user tool.

    :param str bearer_token: Bearer token for PriceCypher (logical) API. Needs 'read:datasets' scope.
    :param str users_base: (optional) Base URL for PriceCypher user tool API.
        (defaults to https://users.pricecypher.com)
    :param RestClientOptions rest_options: (optional) Set any additional options for the REST client, e.g. rate-limit.
        (defaults to None)
    """

    def __init__(self, bearer_token, users_base='https://users.pricecypher.com', rest_options=None):
        self.users_base = users_base
        self.bearer_token = bearer_token
        self.client = RestClient(jwt=bearer_token, options=rest_options)

    def _url(self, path):
        return '{}/{}'.format(self.users_base.strip('/'), path.strip('/'))

    def datasets(self):
        return DatasetsEndpoint(self.client, self._url('api/datasets'))


class DatasetsEndpoint(object):
    def __init__(self, client, base):
        self.client = client
        self.base = base

    def index(self) -> list[Dataset]:
        """List all available datasets the user has access to.

        :return: list of datasets.
        :rtype list[Dataset]
        """
        return self.client.get(self.base, schema=Dataset.Schema(many=True))