from typing import Union

from better_abc import ABCMeta, abstract_attribute


class Endpoint(metaclass=ABCMeta):
    base_url: str = abstract_attribute()

    def url(self, path: Union[None, str, list[str]] = None):
        if path is None:
            return self.base_url
        if type(path) is list:
            path = '/'.join(str(s).strip('/') for s in path)
        else:
            path = path.strip('/')
        return '{}/{}'.format(self.base_url.strip('/'), path)
