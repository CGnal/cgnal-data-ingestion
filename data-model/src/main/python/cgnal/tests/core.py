import pandas as pd
import numpy as np
from time import time
from unittest import TestCase as CoreTestCase
from cgnal.logging.defaults import WithLogging


def logTest(test):
    def wrap(obj):
        t0 = time()
        obj.logger.info(f"Executing Test {str(test.__name__)}")
        test(obj)
        obj.logger.info(f"Execution Time: {time() - t0} secs")
    return wrap


class TestCase(CoreTestCase, WithLogging):

    def compareLists(self, first, second, strict=False):
        if strict:
            [self.assertEqual(item1, item2) for item1, item2 in zip(first, second)]
        else:
            self.assertTrue(len(set(first).intersection(second)) == len(set(first)))

    def compareDicts(self, first, second, strict=False):
        for key in set(first.keys()).union(second.keys()):
            if isinstance(first[key], dict):
                self.compareDicts(first[key], second[key])
            elif isinstance(first[key], list):
                self.compareLists(first[key], second[key], strict)
            else:
                self.assertEqual(first[key], second[key])

    def compareDataFrames(self, first, second, msg):
        try:
            pd.testing.assert_frame_equal(first, second)
        except AssertionError as e:
            raise self.failureException("Input series are different") from e

    def compareSeries(self, first, second, msg):
        try:
            pd.testing.assert_series_equal(first, second)
        except AssertionError as e:
            raise self.failureException("Input series are different") from e

    def compareArrays(self, first, second, msg):
        try:
            np.testing.assert_almost_equal(first, second, decimal=7)
        except AssertionError as e:
            raise self.failureException("Input arrays are different") from e

    def setUp(self) -> None:
        self.addTypeEqualityFunc(pd.DataFrame, self.compareDataFrames)
        self.addTypeEqualityFunc(pd.Series, self.compareSeries)
        self.addTypeEqualityFunc(np.ndarray, self.compareArrays)
