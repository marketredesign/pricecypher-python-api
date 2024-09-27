from __future__ import annotations

import logging
import os
import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq
import re
import smart_open

from abc import ABC
from contextlib import contextmanager
from pathlib import Path
from typing import Type, Union, Optional

from pricecypher.dataclasses import HandlerSettings
from pricecypher.dataclasses.settings.remote_storage_settings import RemoteStorageSettings
from pricecypher.exceptions import InvalidStateException
from pricecypher.storage.transport_params_factory import create_transport_params

p_has_url_proto = re.compile('(.+)://(.+)')


class FileStorage(ABC):
    _path_local: str
    _path_remote_base: str
    _path_remote_prefix: str
    _remote_storage_settings: RemoteStorageSettings

    def __init__(
            self,
            path_local: str,
            path_remote_base: str,
            path_remote_prefix: str,
            remote_storage_settings: RemoteStorageSettings = None,
    ) -> None:
        """
        :param path_local: Path on local filesystem where artifacts should be stored. We assume these artifacts are
            eventually uploaded to a remote location.
        :param path_remote_base: Base path of the remote storage, e.g. an URI pointing to the root of an S3 bucket.
        :param path_remote_prefix: Location within / on top of `path_remote_base` where remote artifacts will end up.

        NB: Values should be such that a locally stored 'file' at `path_local / file` matches with a remote copy at
        `path_remote_base / path_remote_prefix / file`.
        """
        self._path_local = path_local
        self._path_remote_base = path_remote_base
        self._path_remote_prefix = path_remote_prefix
        self._remote_storage_settings = remote_storage_settings or RemoteStorageSettings()

    def get_path_local(self, filename: str) -> str:
        return os.path.join(self._path_local, filename)

    def get_path_remote(self, filename: str, full: bool = True) -> str:
        """
        :param filename: Name of the file.
        :param full: Whether the full remote path, so including `self._path_remote_base`, should be returned.
        :return: Path in remote storage. Either absolute (including 'base') or relative, depending on given `full`.
        """
        suffix = os.path.join(self._path_remote_prefix, filename)

        if not full:
            return suffix

        return os.path.join(self._path_remote_base, suffix)

    @classmethod
    def get_scheme(cls, uri_as_string) -> Optional[str]:
        uri = smart_open.parse_uri(uri_as_string)
        return uri.scheme if hasattr(uri, 'scheme') else None

    def get_scheme_local(self, filename: str) -> str:
        return self.get_scheme(self.get_path_local(filename))

    def get_scheme_remote(self, filename: str) -> str:
        return self.get_scheme(self.get_path_remote(filename))

    @contextmanager
    def save(self, filename: str, mode: str = 'w') -> str:
        """
        Open a file handler context to a new file in local storage.
        NB: the locally saved file should be uploaded to the remote storage automatically / externally.

        :param filename: Name of the file to save.
        :param mode: (Optional) Mimicks the `mode` parameter of the built-in `open` function. Defaults to 'w'.

        See Also
        --------
        - `Standard library reference <https://docs.python.org/3.7/library/functions.html#open>`__
        - `smart_open README.rst <https://github.com/RaRe-Technologies/smart_open/blob/master/README.rst>`__
        """
        if not self._path_local:
            raise InvalidStateException("The `path_local_outputs` and `path_local_outputs` must be set to save files.")

        local = self.get_path_local(filename)
        scheme = self.get_scheme(local)
        transport_params = create_transport_params(self._remote_storage_settings, scheme)

        logging.info(f"Saving file, local path = '{local}', remote path = '{self.get_path_remote(filename)}'...")

        if scheme == 'file':
            logging.debug("Making non-existing directories on the path to parent of `file_path_local`...")
            Path(local).parent.mkdir(parents=True, exist_ok=True)

        with smart_open.open(local, mode, transport_params=transport_params) as file:
            yield file

    @contextmanager
    def load(self, path: Union[Path, str], mode: str = 'r') -> str:
        """
        Open a file handler context to the give (remote) file path.

        :param path: Either an absolute path to a (remote) file, or a relative path from the remote file store.
        :param mode: (Optional) Mimicks the `mode` parameter of the built-in `open` function. Defaults to 'r'.
        """
        scheme = self.get_scheme(path)

        if isinstance(path, Path):
            path = path.as_posix()

        if scheme == 'file' and not Path(path).is_absolute():
            path = self.get_path_remote(path)

        transport_params = create_transport_params(self._remote_storage_settings, scheme)

        logging.debug(f"Loading / opening (remote) file at path '{path}'...")

        with smart_open.open(path, mode, transport_params=transport_params) as file:
            yield file

    @classmethod
    def from_handler_settings(cls: Type[FileStorage], settings: HandlerSettings) -> FileStorage:
        return cls(
            path_local=settings.path_local_out,
            path_remote_base=settings.path_remote_out_base,
            path_remote_prefix=settings.path_remote_out_prefix,
            remote_storage_settings=settings.remote_storage_settings,
        )

    def read_file(self, path_in: str) -> str:
        """
        Read a string file from path_in, using FileStorage.
        :param path_in: the path to read from.
        :return: the file contents.
        """
        with self.load(path_in, mode='r') as f:
            return f.read()

    def write_file(self, path_out: str, string: str) -> str:
        """
        Write a string to a file, using FileStorage.
        :param path_out: the path to write the file to.
        :param string: the string to write to the file.
        :return: the remote storage path.
        """
        self._create_folders(path_out)
        with self.save(path_out, mode='w') as f:
            f.write(string)
        return self.get_path_remote(path_out)

    def read_df(self, path_in: str) -> pd.DataFrame:
        """
        Read a DataFrame pickle from path_in, using FileStorage.
        :param path_in: the path to read from.
        :return: the DataFrame.
        """
        with self.load(path_in, mode='rb') as f:
            return pd.read_pickle(f)

    def write_df(self, path_out: str, df: pd.DataFrame) -> str:
        """
        Write a DataFrame to a pickle, using FileStorage.
        :param path_out: the path to write the pickle to.
        :param df: the DataFrame to store.
        :return: the remote storage path.
        """
        self._create_folders(path_out)
        with self.save(path_out, mode='wb') as f:
            pd.to_pickle(df, f)
        return self.get_path_remote(path_out)

    def read_parquet(self, path_in: str) -> pa.Table:
        """
        Read a parquet file from path_in, using FileStorage.
        :param path_in: the path to read from.
        :return: the DataFrame.
        """
        with self.load(path_in, mode='rb') as f:
            return pq.read_table(f)

    def write_parquet(self, path_out: str, table: pa.Table) -> str:
        """
        Write a parquet file, using FileStorage.
        :param path_out: the path to write the parquet file to.
        :param table: the Table to store.
        :return: the remote storage path.
        """
        self._create_folders(path_out)
        with self.save(path_out, mode='wb') as f:
            pq.write_table(table, f)
        return self.get_path_remote(path_out)

    def _create_folders(self, path: str) -> None:
        """
        Create the folders in path if they don't exist.
        :param path:
        """
        pathdir = os.path.dirname(path)
        if not os.path.exists(pathdir):
            os.makedirs(pathdir)
