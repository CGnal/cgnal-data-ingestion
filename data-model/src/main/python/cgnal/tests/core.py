import pandas as pd  # type: ignore
import numpy as np  # type: ignore
from time import time
from typing import Callable, TypeVar
from unittest import TestCase as CoreTestCase
from cgnal.logging.defaults import WithLogging

class TestCase(CoreTestCase, WithLogging):

    def compareLists(self, first: list, second: list, strict: bool = False) -> None:
        if strict:
            for item1, item2 in zip(first, second):
                self.assertEqual(item1, item2)
        else:
            self.assertTrue(len(set(first).intersection(second)) == len(set(first)))

    def compareDicts(self, first: dict, second: dict, strict: bool = False) -> None:
        for key in set(first.keys()).union(second.keys()):
            if isinstance(first[key], dict):
                self.compareDicts(first[key], second[key])
            elif isinstance(first[key], list):
                self.compareLists(first[key], second[key], strict)
            else:
                self.assertEqual(first[key], second[key])

    def compareDataFrames(self, first: pd.DataFrame, second: pd.DataFrame, msg: str) -> None:
        try:
            pd.testing.assert_frame_equal(first, second)
        except AssertionError as e:
            raise self.failureException("Input series are different") from e

    def compareSeries(self, first: pd.Series, second: pd.Series, msg: str) -> None:
        try:
            pd.testing.assert_series_equal(first, second)
        except AssertionError as e:
            raise self.failureException("Input series are different") from e

    def compareArrays(self, first: np.ndarray, second: np.ndarray, msg: str) -> None:
        try:
            np.testing.assert_almost_equal(first, second, decimal=7)
        except AssertionError as e:
            raise self.failureException("Input arrays are different") from e

    def setUp(self) -> None:
        self.addTypeEqualityFunc(pd.DataFrame, self.compareDataFrames)
        self.addTypeEqualityFunc(pd.Series, self.compareSeries)
        self.addTypeEqualityFunc(np.ndarray, self.compareArrays)


T = TypeVar("T", bound=WithLogging)

def logTest(test: Callable[[T], None]) -> Callable[[T], None]:
    def wrap(obj: T) -> None:
        t0 = time()
        obj.logger.info(f"Executing Test {str(test.__name__)}")
        test(obj)
        obj.logger.info(f"Execution Time: {time() - t0} secs")
    return wrap
