import pbr.version

from .config_sections import ConfigSections
from .datasets import Datasets

__version__ = pbr.version.VersionInfo('pricecypher_sdk').version_string()
