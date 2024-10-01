import json
import pandas as pd

from abc import abstractmethod
from typing import Any

from pricecypher.contracts import BaseHandler
from pricecypher.dataclasses import HandlerSettings, TestSuite
from pricecypher.encoders import PriceCypherJsonEncoder
from pricecypher.enums import AccessTokenGrantType
from pricecypher.oidc import AccessTokenGenerator
from pricecypher.storage import FileStorage


class DataReportHandler(BaseHandler):
    """
    The abstract DataReportHandler class provides a base for storing a TestSuite report based on a pandas DataFrame.
    Extend this class and override the `process()` method when you want to receive a DataFrame and do data checks on
    it.
    The input DataFrame should be available as a pickle at the `path_in` location. The output TestSuite will be stored
    as a json file to the `path_out` location.
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
        Needs a pandas DataFrame stored as a pickle at the `path_in` location. The output json will be
        stored at the `path_out` location.

        :param user_input: requires `path_in` and `path_out`.
        :return: the remote storage path.
        """
        input_df = self._file_storage.read_df(user_input.get('path_in'))
        output_report_json = json.dumps(self.process(input_df), cls=PriceCypherJsonEncoder)
        return self._file_storage.write_string(user_input.get('path_out'), output_report_json)

    @abstractmethod
    def process(self, df: pd.DataFrame) -> TestSuite:
        """
        Override to implement and run data checks on the input DataFrame.

        :param df: the input DataFrame.
        :return: the resulting TestSuite.
        """
        raise NotImplementedError
