from collections.abc import Sequence

from pricecypher.endpoints.datasets import DatasetsEndpoint
from pricecypher.endpoints.users import UsersEndpoint
from pricecypher.models import Scope, ScopeValue
from pricecypher.rest import RestClient


class ScopeCollection(Sequence):
    def __init__(self, scopes):
        self._list = list(scopes)
        self.check_types()

    def check_types(self):
        for v in self._list:
            if not isinstance(v, Scope):
                raise TypeError(v)

    def __repr__(self):
        return "<{0} {1}>".format(self.__class__.__name__, self._list)

    def __len__(self):
        """List length"""
        return len(self._list)

    def __getitem__(self, ii):
        """Get a list item"""
        return self._list[ii]

    def __str__(self):
        return str(self._list)

    def find_by_id(self, scope_id):
        return next((s for s in self._list if s.id == scope_id))

    def find_by_repr(self, representation):
        return next((s for s in self._list if s.representation == representation))

    def find_by_name_dataset(self, name_dataset):
        return next((s for s in self._list if s.name_dataset == name_dataset))

    def _where(self, prop, value):
        scopes = filter(lambda v: getattr(v, prop) == value, self._list)
        return ScopeCollection(scopes)

    def where_type(self, typ):
        return self._where('type', typ)

    def where_multiply_by_volume_enabled(self, enabled=True):
        return self._where('multiply_by_volume_enabled', enabled)


class ScopeValueCollection(Sequence):
    def __init__(self, scope_values):
        self._list = list(scope_values)
        self.check_types()

    def check_types(self):
        for v in self._list:
            if not isinstance(v, ScopeValue):
                raise TypeError(v)

    def __repr__(self):
        return "<{0} {1}>".format(self.__class__.__name__, self._list)

    def __len__(self):
        """List length"""
        return len(self._list)

    def __getitem__(self, ii):
        """Get a list item"""
        return self._list[ii]

    def __str__(self):
        return str(self._list)

    def where_in(self, values):
        if type(values) is not list:
            values = [values]

        # Make sure all values are strings.
        values = list(map(str, values))
        scope_values = [sv for sv in self._list if sv.value in values]
        return ScopeValueCollection(scope_values)

    def pluck(self, prop):
        return [getattr(v, prop) for v in self._list]


class Datasets(object):
    """

    :param str bearer_token: Bearer token for PriceCypher (logical) API. Needs 'read:datasets' scope.
    :param str users_base: (optional) Base URL for PriceCypher user tool API.
        (defaults to https://users.pricecypher.com)
    :param str dss_base: (optional) Base URL for PriceCypher dataset service API.
        (defaults to dss_url property as returned for the dataset by the PriceCypher user tool API)
    :param RestClientOptions rest_options: (optional) Set any additional options for the REST client, e.g. rate-limit.
        (defaults to None)
    """

    def __init__(self, bearer_token, users_base='https://users.pricecypher.com', dss_base=None, rest_options=None):
        self._bearer = bearer_token
        self._users_base = users_base
        self._dss_base = dss_base
        self._rest_options = rest_options
        self._client = RestClient(jwt=bearer_token, options=rest_options)
        self._all_meta = None

    def dss_base(self, dataset_id):
        if self._dss_base is not None:
            return self._dss_base

        return self.get_meta(dataset_id).dss_url

    def index(self):
        """List all available datasets the user has access to.
        Response is cached in this instance for as long as this instance lives.

        :return: list of datasets.
        :rtype list[Dataset]
        """
        if self._all_meta is not None:
            return self._all_meta

        self._all_meta = UsersEndpoint(self._bearer, self._users_base, self._rest_options).datasets().index()
        return self._all_meta

    def get_meta(self, dataset_id):
        """Gets metadata like the dataset service url and time of creation of a dataset

        :param dataset_id: Dataset to get metadata for.
        :return:
        """
        return next((d for d in self.index() if d.id == dataset_id), None)

    def get_scopes(self, dataset_id, bc_id='all'):
        return ScopeCollection(
            DatasetsEndpoint(self._bearer, dataset_id, self.dss_base(dataset_id), self._users_base, self._rest_options)
            .business_cell(bc_id)
            .scopes()
            .index()
        )

    def get_scope_values(self, dataset_id, scope_id, bc_id='all'):
        dss_base = self.dss_base(dataset_id)
        return ScopeValueCollection(
            DatasetsEndpoint(self._bearer, dataset_id, dss_base, self._users_base, self._rest_options)
            .business_cell(bc_id)
            .scopes()
            .scope_values(scope_id)
        )

    def get_transaction_summary(self, dataset_id, bc_id='all'):
        dss_base = self.dss_base(dataset_id)
        return DatasetsEndpoint(self._bearer, dataset_id, dss_base, self._users_base, self._rest_options) \
            .business_cell(bc_id) \
            .transactions()\
            .summary()

    def _add_scopes(self, dataset_id, columns: list, bc_id='all'):
        all_scopes = self.get_scopes(dataset_id, bc_id)

        def add_scope(column: dict):
            if 'representation' in column:
                scope = all_scopes.find_by_repr(column['representation'])
            elif 'name_dataset' in column:
                scope = all_scopes.find_by_name_dataset(column['name_dataset'])
            else:
                raise ValueError('No column could be found for column {0}'.format(str(column)))

            return {**column, 'scope': scope}

        return list(map(add_scope, columns))

    def _add_scope_values(self, dataset_id, column: dict, bc_id='all'):
        if 'scope' not in column:
            pass

        scope = column['scope']
        scope_values = self.get_scope_values(dataset_id, scope.id, bc_id)

        return {**column, 'scope_values': scope_values}

    def _find_scope_value_filters(self, columns: list):
        filters = []

        for column in columns:
            filt = dict.get(column, 'filter')
            scope_values = dict.get(column, 'scope_values')

            if not filt or not scope_values:
                continue

            filters.extend(scope_values.where_in(filt).pluck('id'))

        return filters

    def _find_aggregate_methods(self, columns: list):
        aggregate_methods = []

        for column in columns:
            aggregate = dict.get(column, 'aggregate')
            scope = dict.get(column, 'scope')

            if not aggregate or not scope:
                continue

            aggregate_methods.append({
                'scope_id': scope.id,
                'method': aggregate,
            })

        return aggregate_methods

    def get_transactions(self, dataset_id, aggregate, columns: list, start_date_time=None, end_date_time=None, bc_id='all'):
        dss_base = self.dss_base(dataset_id)
        columns_with_scopes = self._add_scopes(dataset_id, columns, bc_id)
        select_scopes = [c['scope'].id for c in columns_with_scopes]
        columns_with_values = [
            self._add_scope_values(dataset_id, c, bc_id) for c in columns_with_scopes if dict.get(c, 'filter')
        ]
        filters = self._find_scope_value_filters(columns_with_values)
        aggregate_methods = self._find_aggregate_methods(columns_with_scopes)

        request_data = {
            'aggregate': aggregate,
            'select_scopes': select_scopes,
        }

        if len(filters) > 0:
            request_data['filter_scope_values'] = filters

        if len(aggregate_methods) > 0:
            request_data['aggregation_methods'] = aggregate_methods

        return DatasetsEndpoint(self._bearer, dataset_id, dss_base, self._users_base, self._rest_options) \
            .business_cell(bc_id) \
            .transactions() \
            .index(request_data)

