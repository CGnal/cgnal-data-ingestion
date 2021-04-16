from __future__ import annotations
import pickle
from abc import ABCMeta, abstractproperty, abstractmethod
from functools import reduce
from itertools import islice
from typing import List, Iterator
from collections import namedtuple

import dill
import numpy as np
import pandas as pd
from pandas.core.tools.datetimes import DatetimeScalar

from cgnal.utils.dict import groupIterable

try:
    # Python 2
    from future_builtins import filter
except ImportError:
    # Python 3
    pass


class IterGenerator(object):
    def __init__(self, generator_function):
        self.generator_function = generator_function

    @property
    def iterator(self):
        return self.generator_function()


class Iterable(object):
    __metaclass__ = ABCMeta

    def __create_instance__(self, items):
        obj = self.__new__(type(self))
        obj.__init__(items)
        return obj

    @abstractproperty
    def items(self):
        raise NotImplementedError

    @abstractmethod
    def take(self, size):
        raise NotImplementedError

    def filter(self, f):
        raise NotImplementedError

    @abstractproperty
    def cached(self):
        raise NotImplementedError

    @abstractmethod
    def kfold(self, int):
        raise NotImplementedError

    def __iter__(self):
        for item in self.items:
            yield item

    def batch(self, size=100):
        for batch in groupIterable(self.items, batch_size=size):
            yield batch

    def map(self, f):
        for doc in self.items:
            yield f(doc)

    def foreach(self, f):
        for doc in self.items:
            f(doc)

    def hold_out(self, ratio):
        """
        Train, Test Dataset split

        :param ratio: Int, ratio for splitting
        :return: (Dataset, Dataset), Train and Test Datasets
        """
        fold = int(round(1.0 / ratio))
        if fold * ratio - 1.0 > 1E-1:
            print(' Approximating ratio of %f to %f' % (ratio, 1.0 / fold))
        return next(self.kfold(fold))


class LazyIterable(Iterable):

    def __init__(self, items):
        if not isinstance(items, IterGenerator):
            raise TypeError("For lazy iterables the input must be an IterGenerator(object). Input of type %s passed"
                            % type(items))
        self.__items__ = items

    @property
    def items(self):
        return self.__items__.iterator

    @property
    def cached(self):
        return False

    @staticmethod
    def toCached(items):
        return CachedIterable(items)

    def batch(self, size=100):
        for batch in super(LazyIterable, self).batch(size=size):
            yield self.toCached(batch)

    def cache(self):
        return self.toCached(list(self.items))

    def take(self, size):
        def generator():
            return islice(self.items, size)

        return self.__create_instance__(IterGenerator(generator))

    def filter(self, f):
        def generator():
            return filter(self.items, f)

        return self.__create_instance__(IterGenerator(generator))

    def kfold(self, folds=3):
        """
        Kfold iterator of Train, Test Dataset split over the folds

        :param folds: Int, number of folds
        :return: Iterator(Dataset, Dataset), Iterator over the Train, Test splits for the given fold
        """
        for fold in range(folds):

            def test():
                for istory, story in enumerate(self.items):
                    if (istory + fold) % folds == 0:
                        yield story
                    else:
                        pass

            def train():
                for istory, story in enumerate(self.items):
                    if (istory + fold) % folds != 0:
                        yield story
                    else:
                        pass

            yield self.__create_instance__(IterGenerator(train)), self.__create_instance__(IterGenerator(test))


class CachedIterable(Iterable):

    def __init__(self, items):
        self.__items__ = list(items)

    def __len__(self):
        return len(self.items)

    @property
    def items(self):
        return self.__items__

    def __getitem__(self, item):
        return self.items[item]

    @property
    def cached(self):
        return True

    def batch(self, size=100):
        for batch in super(CachedIterable, self).batch(size=size):
            yield self.__create_instance__(batch)

    def filter(self, f):
        return self.__create_instance__(filter(f, self.items))

    def kfold(self, folds=3):
        array = np.array(self.items)
        size = range(len(array))
        for fold in range(folds):
            iTest = array[((size + fold) % folds == 0)]
            iTrain = array[((size + fold) % folds != 0)]
            yield self.__create_instance__(array[iTrain]), self.__create_instance__(array[iTest])

    def take(self, size):
        return self.__create_instance__(self.items[:size])

    def save(self, filename):
        with open(filename, 'w') as fid:
            pickle.dump(self.items, fid)
        return filename

    @staticmethod
    def load(filename):
        with open(filename, 'r') as fid:
            items = pickle.load(fid)
        return CachedIterable(items)


class Range(object):

    Interval = namedtuple('Interval', ['start', 'end'])
    ranges: List[Interval] = []

    def __init__(self, start: DatetimeScalar, end: DatetimeScalar):
        """
        Range Class

        :param start: starting datetime for the range
        :param end: ending datetime for the range
        """
        if start > end:
            raise ValueError("Start and End values should be consequential: start < end")

        self.ranges.append(self.Interval(start, end))

    @classmethod
    def from_list_of_ranges(cls, ranges: List[Range]) -> Range:
        """
        Instantiates a new Range object from a list of Range objects
        :param ranges: input ranges
        :return: new Range object
        """
        return reduce(cls.add, ranges)

    @classmethod
    def from_list_of_intervals(cls, intervals: List[Range.Interval]) -> Range:
        """
        Instantiates a new Range object from a list of intervals tuples
        :param intervals: input intervals
        :return: new Range object
        """
        return reduce(cls.add, [Range(*interval) for interval in intervals])

    @staticmethod
    def add(first: Range, second: Range) -> Range:
        return first + second

    def simplify(self) -> Range:
        """
        Simplifies the list into disjoint Range objects, aggregating non-disjoint ranges. If only one range would be
        present, a simple Range object is returned

        :return: Range
        """

        def __add_simple_range(first: Range, second: Range) -> Range:
            """
            Add a simple Range (single interval) to another (possibly already complex) Range,
            checking and simplifying overlaps between the simple Range and the last interval of the complex Range
            :param first: first Range (possibly complex)
            :param second: second Range (single interval)
            :return: new Range
            """
            if first.start > second.start:
                first, second = second, first
            if len(second.ranges) != 1:
                raise ValueError('This method works only if the second operand is a simple range.')
            if Range(*first.ranges[-1]).overlaps(second):
                return Range.from_list_of_intervals(first.ranges[:-1] + [first.ranges[-1].start, second.ranges[0].end])
            else:
                return first + second

        ranges = [Range(*r) for r in sorted(self.ranges, key=lambda r: r.start)]
        return reduce(__add_simple_range, ranges[1:], ranges[0])

    @property
    def start(self):
        return min([r.start for r in self.ranges])

    @property
    def end(self):
        return max([r.end for r in self.ranges])

    def __iter__(self) -> Iterator[Range]:
        for r in self.ranges:
            yield Range(*r)

    def range(self, freq="H"):
        items = np.unique([
            item for r in self.ranges for item in pd.date_range(r.start, r.end, freq=freq)
        ])
        return sorted(items)

    def __add__(self, other: Range) -> Range:
        if not isinstance(other, Range):
            raise ValueError(f"add operator not defined for argument of type {type(other)}. Argument should be of "
                             f"type CompositeRange")
        return self.add(self, other)

    @staticmethod
    def __overlaps_simple_range(first: Range, second: Range) -> bool:
        """
        Checks overlaps between two simple Ranges (single intervals)
        :param first: simple Range
        :param second: simple Range
        :return: True if they overlap, False otherwise
        """
        if len(first.ranges) != 1 or len(second.ranges) != 1:
            raise ValueError('This method works only for two simple ranges.')
        return ((first.start < second.start) and (first.end > second.start)) or (
                (second.start < first.start) and (second.end > first.start))

    def overlaps(self, other: Range) -> bool:
        """
        Checks if this Range overlaps with another Range
        :param other: Range
        :return: True if they overlap, False otherwise
        """
        return any([self.__overlaps_simple_range(Range(*first), Range(*second))
                    for first in self.ranges for second in other.ranges])

    def __str__(self):
        return " // ".join([f"{range.start}-{range.end}" for range in self])

    @property
    def days(self):
        """
        Create date range with daily frequency

        :return: pd.date_range from start to end with daily frequency
        """
        return self.range(freq="1D")

    @property
    def business_days(self):
        """
        Create date range with daily frequency

        :return: pd.date_range from start to end with daily frequency
        """
        return self.range(freq="1B")

    @property
    def minutes_15(self):
        """
        Create date range with daily frequency

        :return: pd.date_range from start to end with daily frequency
        """
        return self.range(freq="15T")


class Serializable(object):

    @abstractmethod
    def write(self, filaname: str):
        raise NotImplementedError

    @classmethod
    def load(cls, filename: str):
        raise NotImplementedError


class PickleSerialization(Serializable):

    def write(self, filename: str):
        """
        Write processing pipeline as pickle

        :param filename: Name of the file where to save the model

        :type filename: str

        :return: None
        """
        with open(filename, 'wb') as fid:
            pickle.dump(self, fid)

    @classmethod
    def load(cls, filename: str):
        """
        Load processing pipeline

        :param filename: Name of the file to be read
        :return: Instance of the read Model
        """
        with open(filename, 'rb') as fid:
            return pickle.load(fid)


class DillSerialization(Serializable):

    def write(self, filename: str):
        """
        Write processing pipeline as pickle

        :param filename: Name of the file where to save the model

        :type filename: str

        :return: None
        """
        with open(filename, 'wb') as fid:
            dill.dump(self, fid)

    @classmethod
    def load(cls, filename: str):
        """
        Load processing pipeline

        :param filename: Name of the file to be read
        :return: Instance of the read Model
        """
        with open(filename, 'rb') as fid:
            return dill.load(fid)
