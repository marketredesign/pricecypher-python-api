from enum import Enum

from pricecypher.oidc import AccessTokenGenerator
from pricecypher.oidc.auth import StaticTokenGenerator, ClientTokenGenerator


class AccessTokenGrantType(Enum):
    STATIC = 'static'
    CLIENT_CREDENTIALS = 'client_credentials'

    def get_generator(self, **kwargs) -> AccessTokenGenerator:
        match self:
            case AccessTokenGrantType.STATIC:
                return StaticTokenGenerator(**kwargs)
            case AccessTokenGrantType.CLIENT_CREDENTIALS:
                return ClientTokenGenerator(**kwargs)
