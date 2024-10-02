import pandas as pd
import pyarrow as pa

from abc import abstractmethod
from typing import Any

from .base_handler import BaseHandler
from pricecypher.dataclasses import HandlerSettings
from pricecypher.enums import AccessTokenGrantType
from pricecypher.oidc import AccessTokenGenerator
from pricecypher.storage import FileStorage


class WriteParquetHandler(BaseHandler):
    """
    The abstract WriteParquetHandler class provides a base to write a pandas DataFrame to a parquet file.
    Extend this class and override the `process()` method when you want to do exactly that.
    The input DataFrame file should be available as a pickle at the `path_in` location. The output parquet file will be
    stored at the `path_out` location.
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
        Needs a DataFrame stored as a pickle at the `path_in` location. The output pyarrow Table will be stored as a
        parquet file at the `path_out` location.

        :param user_input: requires `path_in` and `path_out`.
        :return: the remote storage path.
        """
        input_df = self._file_storage.read_df(user_input.get('path_in'))
        output_table = self.process(input_df)
        return self._file_storage.write_parquet(user_input.get('path_out'), output_table)

    @abstractmethod
    def process(self, df: pd.DataFrame) -> pa.Table:
        """
        Override to implement and transform a pandas DataFrame into a pyarrow Table, which will be stored as parquet
        file at the `path_out` location passed in the `handle()` method.

        :param df: the input DataFrame.
        :return: the resulting pyarrow Table.
        """
        raise NotImplementedError
