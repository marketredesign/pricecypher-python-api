import pbr.version

from .collections.scope_collection import ScopeCollection
from .collections.scope_value_collection import ScopeValueCollection
from .config_sections import ConfigSections
from .datasets import Datasets

__version__ = pbr.version.VersionInfo('pricecypher_sdk').version_string()
