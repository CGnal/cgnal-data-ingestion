import unittest

from cgnal.logging.defaults import getDefaultLogger
from cgnal.tests.core import logTest, TestCase
from cgnal.utils.dict import union, filterNones

logger = getDefaultLogger()

class TestUtils(TestCase):

    @logTest
    def test_utils_dict(self):
        self.assertEqual(
            filterNones({"a": 1, "b": None}),
            {"a": 1}
        )

        self.assertEqual(
            union({"1": {"a": 1}}, filterNones({"1": {"a": None}, "b": 1})),
            {"1": {"a": 1}, "b": 1}
        )

        self.assertEqual(
            union({"1": {"a": 1}}, filterNones({"1": {"a": 2}, "b": None})),
            {"1": {"a": 2}}
        )



if __name__ == "__main__":
    unittest.main()
