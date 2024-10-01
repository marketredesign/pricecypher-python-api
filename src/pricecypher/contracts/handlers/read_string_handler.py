import pandas as pd

from abc import abstractmethod
from typing import Any

from pricecypher.contracts import BaseHandler
from pricecypher.dataclasses import HandlerSettings
from pricecypher.enums import AccessTokenGrantType
from pricecypher.oidc import AccessTokenGenerator
from pricecypher.storage import FileStorage


class ReadStringHandler(BaseHandler):
    """
    The abstract ReadStringHandler class provides a base to read a file with string contents into a pandas DataFrame.
    Extend this class and override the `process()` method when you want to do exactly that.
    The input string file should be available at the `path_in` location. The output DataFrame will be
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
        Needs a string file stored at the `path_in` location. The output pandas DataFrame will be stored as a pickle at
        the `path_out` location.

        :param user_input: requires `path_in` and `path_out`.
        :return: the remote storage path.
        """
        input_string = self._file_storage.read_string(user_input.get('path_in'))
        output_df = self.process(input_string)
        return self._file_storage.write_df(user_input.get('path_out'), output_df)

    @abstractmethod
    def process(self, file_string: str) -> pd.DataFrame:
        """
        Override to implement and transform a string, read from the file at the `path_in` location passed in the
        `handle()` method, into a pandas DataFrame.

        :param file_string: the input string.
        :return: the resulting DataFrame.
        """
        raise NotImplementedError
