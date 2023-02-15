from dataclasses import field
from marshmallow_dataclass import dataclass

from pricecypher.models.namespaced_schema import NamespacedSchema


@dataclass(base_schema=NamespacedSchema, frozen=True)
class ConfigSection:
    key: str = field(compare=True)
    name: str = field(compare=False)
    order: str = field(compare=False)

    class Meta:
        name = "section"
        plural_name = "sections"
