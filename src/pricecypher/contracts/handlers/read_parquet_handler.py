import pandas as pd
import pyarrow as pa

from abc import abstractmethod
from typing import Any

from .base_handler import BaseHandler
from pricecypher.dataclasses import HandlerSettings
from pricecypher.enums import AccessTokenGrantType
from pricecypher.oidc import AccessTokenGenerator
from pricecypher.storage import FileStorage


class ReadParquetHandler(BaseHandler):
    """
    The abstract ReadParquetHandler class provides a base to read a parquet file into a pandas DataFrame.
    Extend this class and override the `process()` method when you want to receive a pyarrow Table to convert to a
    DataFrame.
    The input parquet file should be available at the `path_in` location. The output DataFrame will be
    stored as a pickle at the `path_out` location.
    """

    _dataset_id: int
    _settings: HandlerSettings
    _config: dict[str, dict[str, Any]]
    _token_generator: AccessTokenGenerator
    _file_storage: FileStorage

    def get_allowed_access_token_grant_types(self) -> set[AccessTokenGrantType]:
        return set()

    def get_config_dependencies(self) -> dict[str, list[str]]:
        return dict()

    def handle(self, user_input: dict[str, Any]) -> any:
        """
        Handle the given `user_input`.
        Needs a parquet file stored at the `path_in` location. The output pandas DataFrame will be stored as a pickle at
        the `path_out` location.

        :param user_input: requires `path_in` and `path_out`.
        :return: the remote storage path.
        """
        input_table = self._file_storage.read_parquet(user_input.get('path_in'))
        output_df = self.process(input_table)
        return self._file_storage.write_df(user_input.get('path_out'), output_df)

    @abstractmethod
    def process(self, table: pa.Table) -> pd.DataFrame:
        """
        Override to implement and transform a pyarrow Table (read from the input parquet file) into a pandas DataFrame.

        :param table: the input pyarrow Table.
        :return: the resulting DataFrame.
        """
        raise NotImplementedError
