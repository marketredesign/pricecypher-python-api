from typing import Protocol, ClassVar, Dict, Any, runtime_checkable


@runtime_checkable
class DataclassProtocol(Protocol):
    __dataclass_fields__: ClassVar[Dict[str, Any]]
