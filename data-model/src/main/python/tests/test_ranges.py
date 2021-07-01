import unittest

import pandas as pd

from cgnal.logging.defaults import getDefaultLogger
from cgnal.tests.core import logTest, TestCase
from cgnal.data.model.core import Range, CompositeRange

logger = getDefaultLogger()

class TestUtils(TestCase):

    @logTest
    def test_range_creation(self):
        myRange = Range("2021-01-01", "2021-01-10")

        self.assertEqual(myRange.start, pd.to_datetime("2021-01-01"))
        self.assertEqual(myRange.end, pd.to_datetime("2021-01-10"))

        self.assertEqual(len(myRange.range("D")), 10)

        self.assertEqual(len(myRange.range("H")), 9*24 + 1)

        self.assertEqual(len(myRange.range("B")), 6)


    @logTest
    def test_overlaps(self):
        firstRange = Range("2021-01-01", "2021-01-10")
        secondRange = Range("2021-01-08", "2021-01-15")

        self.assertTrue(firstRange.overlaps(secondRange))

    @logTest
    def test_not_overlaps(self):
        firstRange = Range("2021-01-01", "2021-01-10")
        secondRange = Range("2021-01-13", "2021-01-15")

        self.assertFalse(firstRange.overlaps(secondRange))

    @logTest
    def test_composite_overlaps(self):
        firstRange = Range("2021-01-01", "2021-01-10")
        secondRange = Range("2021-01-13", "2021-01-15")
        thirdRange = Range("2021-01-14", "2021-01-18")
        fourthRange = Range("2021-01-16", "2021-01-18")

        compositeRange = CompositeRange([firstRange, thirdRange])

        self.assertTrue(compositeRange.overlaps(secondRange))

        compositeRange = CompositeRange([firstRange, fourthRange])

        self.assertFalse(compositeRange.overlaps(secondRange))

    @logTest
    def test_sum(self):
        firstRange = Range("2021-01-01", "2021-01-10")
        secondRange = Range("2021-01-08", "2021-01-15")
        thirdRange = Range("2021-01-14", "2021-01-20")

        # This should result in a simple Range, since the two ranges are not disjoint
        self.assertTrue(isinstance(firstRange + secondRange, Range))

        # This should result in a CompositeRange, since the two ranges are disjoint
        self.assertTrue(isinstance(firstRange + thirdRange, CompositeRange))

        # This should result in a simple Range, since the three ranges are not disjoint when taken all together
        self.assertTrue(isinstance(firstRange + secondRange + thirdRange, Range))

    @logTest
    def test_simplify(self):
        firstRange = Range("2021-01-01", "2021-01-10")
        secondRange = Range("2021-01-08", "2021-01-15")
        thirdRange = Range("2021-01-14", "2021-01-20")

        composite = CompositeRange([firstRange, secondRange, thirdRange])

        simplified = composite.simplify()

        self.assertTrue(isinstance(simplified, Range))
        self.assertEqual(set(composite.range("D")), set(simplified.range("D")))



if __name__ == "__main__":
    unittest.main()
