from dataclasses import dataclass
from typing import Optional

from pricecypher.enums import Accuracy


@dataclass
class PredictValues:
    predictive_price: float
    max_predictive_range: Optional[float]
    min_predictive_range: Optional[float]


@dataclass
class PredictStep:
    key: str
    value: float
    order: Optional[int]


@dataclass
class PredictResult:
    """
    One quality test script always produces one TestSuite response. A test suite (usually) contains multiple test cases.
    It also defines a category that can be used by front-ends to group multiple test suites together.

    label (str): Label of the test suite, e.g. 'Completeness'.

    key (str): Unique identifier of the test suite (lowercase kebab-case), e.g. 'basic-completeness'.

    category_key (str): Unique identifier of the category this test suite is in, e.g. 'basic' or 'advanced'.

    test_results (list[TestResult]): All test cases of this test suite, with their results.
    """
    predictive_values: PredictValues
    predictive_steps: list[PredictStep]
    accuracy: Accuracy
