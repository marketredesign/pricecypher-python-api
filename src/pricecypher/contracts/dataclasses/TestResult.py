from dataclasses import dataclass
from typing import Union

from pricecypher.contracts import TestStatus


@dataclass
class ElementTestResult:
    key: str
    label: str
    value: Union[str, int]


@dataclass
class ElementTest:
    label: str
    message: str
    status: TestStatus
    results: list[ElementTestResult]


@dataclass
class TestResult:
    key: str
    label: str
    coverage: str
    status: TestStatus
    element_label: str
    elements: list[ElementTest]
