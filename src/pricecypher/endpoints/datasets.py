from pricecypher.endpoints import Endpoint
from pricecypher.models import Scope, ScopeValue, TransactionSummary, Transaction
from pricecypher.rest import RestClient


class DatasetsEndpoint(Endpoint):
    """PriceCypher dataset endpoints in dataset service.

    :param str bearer_token: Bearer token for PriceCypher (logical) API. Needs 'read:datasets' scope.
    :param int dataset_id: Dataset ID.
    :param str dss_base: (optional) Base URL for PriceCypher dataset service API.
        (defaults to https://datasets.pricecypher.com)
    :param str users_base: (optional) Base URL for PriceCypher user tool API. Used to find base URL of dataset service
        for the given dataset, when no dss_base is provided.
        (defaults to https://users.pricecypher.com)
    :param RestClientOptions rest_options: (optional) Set any additional options for the REST client, e.g. rate-limit.
        (defaults to None)
    """

    def __init__(self, bearer_token, dataset_id, dss_base='https://datasets.pricecypher.com', users_base='https://users.pricecypher.com', rest_options=None):
        self.bearer_token = bearer_token
        self.dataset_id = dataset_id
        self.users_base = users_base
        self.base_url = dss_base
        self.client = RestClient(jwt=bearer_token, options=rest_options)

    def business_cell(self, bc_id):
        """

        :param str bc_id:
        :return:
        """
        url = self.url(['api/datasets', self.dataset_id, 'business_cells', bc_id])
        return BusinessCellEndpoint(self.client, url)


class BusinessCellEndpoint(Endpoint):
    def __init__(self, client, base):
        self.client = client
        self.base_url = base

    def scopes(self):
        return ScopesEndpoint(self.client, self.url('scopes'))

    def transactions(self):
        return TransactionsEndpoint(self.client, self.url('transactions'))


class ScopesEndpoint(Endpoint):
    def __init__(self, client, base):
        self.client = client
        self.base_url = base

    def index(self):
        return self.client.get(self.url(), schema=Scope.Schema(many=True))

    def scope_values(self, scope_id):
        return self.client.get(self.url([scope_id, 'scope_values']), schema=ScopeValue.Schema(many=True))


class TransactionsEndpoint(Endpoint):
    def __init__(self, client, base):
        self.client = client
        self.base_url = base

    def index(self, data):
        return self.client.post(self.url(), data=data, schema=Transaction.Schema(many=True))

    def summary(self):
        return self.client.get(self.url('summary'), schema=TransactionSummary.Schema())
