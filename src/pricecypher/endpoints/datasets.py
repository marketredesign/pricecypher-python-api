import logging
import asyncio

from pricecypher.endpoints.base_endpoint import BaseEndpoint
from pricecypher.models import Scope, ScopeValue, TransactionSummary, TransactionsPage


class DatasetsEndpoint(BaseEndpoint):
    """PriceCypher dataset endpoints in dataset service.

    :param RestClient client: HTTP client for making API requests.
    :param int dataset_id: Dataset ID.
    :param str dss_base: (optional) Base URL for PriceCypher dataset service API.
        (defaults to https://datasets.pricecypher.com)
    """

    def __init__(self, client, dataset_id, dss_base='https://datasets.pricecypher.com'):
        self.dataset_id = dataset_id
        self.base_url = dss_base
        self.client = client

    def business_cell(self, bc_id='all'):
        """
        Business cell-specific endpoints within dataset service.
        :param str bc_id: (optional) Business cell ID.
            (defaults to 'all')
        :return: Business cell endpoint
        :rtype: BusinessCellEndpoint
        """
        url = self._url(['api/datasets', self.dataset_id, 'business_cells', bc_id])
        return BusinessCellEndpoint(self.client, url)


class BusinessCellEndpoint(BaseEndpoint):
    """
    Business cell specific endpoints in dataset service.
    """
    def __init__(self, client, base):
        self.client = client
        self.base_url = base

    def scopes(self):
        """
        Scope endpoints in dataset service.
        :rtype: ScopesEndpoint
        """
        return ScopesEndpoint(self.client, self._url('scopes'))

    def transactions(self):
        """
        Transaction endpoints in dataset service.
        :rtype: TransactionsEndpoint
        """
        return TransactionsEndpoint(self.client, self._url('transactions'))


class ScopesEndpoint(BaseEndpoint):
    """
    Scope endpoints in dataset service.
    """
    def __init__(self, client, base):
        self.client = client
        self.base_url = base

    async def index(self):
        """
        Show a list of all scopes of the dataset.
        :rtype: list[Scope]
        """
        return await self.client.get(self._url(), schema=Scope.Schema(many=True))

    async def scope_values(self, scope_id):
        """
        Get all scope values for the given scope of the dataset.
        :param scope_id: Scope to get scope values for.
        :rtype: list[ScopeValue]
        """
        return await self.client.get(self._url([scope_id, 'scope_values']), schema=ScopeValue.Schema(many=True))


class TransactionsEndpoint(BaseEndpoint):
    """
    Transaction endpoints in dataset service.
    """
    def __init__(self, client, base):
        self.client = client
        self.base_url = base

    async def index(self, data, page_cb):
        """
        Display a listing of transactions. The given data will be passed directly to the dataset service.
        :param page_cb: Callback function with input a single page of transactions, called for each individual page.
        :param data: See documentation of dataset service on what data can be passed.
        :return: A list of all returned transactions, potentially across multiple pages.
        :rtype: list[Transaction]
        """
        # Keep track of all page callback tasks, so we can ensure all tasks are finished before returning.
        callbacks = []

        # Perform initial request to retrieve first page of transactions and page metadata.
        logging.debug('Requesting first page of transactions...')
        init_response = await self.client.post(self._url(), data=data, schema=TransactionsPage.Schema())
        logging.debug('Received first page of transactions.')

        # Collect first page of transactions, which will be appended later when multiple pages are available.
        transactions = init_response.transactions
        curr_page = init_response.meta.current_page
        last_page = init_response.meta.last_page
        request_path = init_response.meta.path

        # Schedule async page callback to be handled by the caller.
        callbacks.append(asyncio.create_task(page_cb(transactions, curr_page, last_page)))

        # Loop over all available pages.
        for page_nr in range(curr_page + 1, last_page + 1):
            logging.debug(f'Requesting transaction page {page_nr}/{last_page}...')
            page_path = f'{request_path}?page={page_nr}'
            page_response = await self.client.post(page_path, data=data, schema=TransactionsPage.Schema())
            logging.debug(f'Received transaction page {page_nr}/{last_page}.')

            # Schedule async page callback function with this page of transactions.
            callbacks.append(asyncio.create_task(page_cb(page_response.transactions, page_nr, last_page)))

            # Append transactions of the current page.
            transactions += page_response.transactions

        # Wait for all callbacks to be done executing.
        await asyncio.gather(*callbacks)

        return transactions

    async def summary(self, intake_status=None):
        """
        Get a summary of the transactions. Contains the first and last date of any transaction in the dataset.
        :param intake_status: (Optional) intake status to fetch the summary for.
        :rtype: TransactionSummary
        """
        params = {}
        if intake_status is not None:
            params['intake_status'] = intake_status
        return await self.client.get(self._url('summary'), params=params, schema=TransactionSummary.Schema())
