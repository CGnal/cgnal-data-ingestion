import pickle
from abc import ABCMeta, abstractmethod
from functools import reduce
from itertools import islice
from typing import List, Iterator, Tuple

import dill
import numpy as np
import pandas as pd
from pandas.core.tools.datetimes import DatetimeScalar, Timestamp, DatetimeIndex

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


class BaseRange(object):
    """
    Abstract Range Class
    """

    @property
    @abstractmethod
    def start(self) -> Timestamp:
        """
        First timestamp
        :return: Timestamp
        """
        raise NotImplementedError

    @property
    @abstractmethod
    def end(self) -> Timestamp:
        """
        Last timestamp
        :return: Timestamp
        """
        raise NotImplementedError

    @abstractmethod
    def __iter__(self) -> Iterator['Range']:
        raise NotImplementedError

    @abstractmethod
    def __add__(self, other: 'BaseRange') -> 'BaseRange':
        raise NotImplementedError

    @abstractmethod
    def overlaps(self, other: 'BaseRange') -> bool:
        raise NotImplementedError

    @abstractmethod
    def range(self, freq="H") -> List[Timestamp]:
        """
        Compute date range with given frequency

        :param freq: frequency

        :type: str

        :return: List of timestamps
        """
        raise NotImplementedError

    def __str__(self) -> str:
        return " // ".join([f"{range.start}-{range.end}" for range in self])

    @property
    def days(self) -> List[Timestamp]:
        """
        Create date range with daily frequency

        :return: pd.date_range from start to end with daily frequency
        """
        return self.range(freq="1D")

    @property
    def business_days(self) -> List[Timestamp]:
        """
        Create date range with daily frequency

        :return: pd.date_range from start to end with daily frequency
        """
        return self.range(freq="1B")

    @property
    def minutes_15(self) -> List[Timestamp]:
        """
        Create date range with daily frequency

        :return: pd.date_range from start to end with daily frequency
        """
        return self.range(freq="15T")


class Range(BaseRange):

    def __init__(self, start: DatetimeScalar, end: DatetimeScalar):
        """
        Simple Range Class

        :param start: starting datetime for the range
        :param end: ending datetime for the range
        """
        self.__start__ = pd.to_datetime(start)
        self.__end__ = pd.to_datetime(end)

        if self.start > self.end:
            raise ValueError("Start and End values should be consequential: start < end")

    @property
    def start(self) -> Timestamp:
        return self.__start__

    @property
    def end(self) -> Timestamp:
        return self.__end__

    def __iter__(self) -> Iterator['Range']:
        yield Range(self.start, self.end)

    def range(self, freq="H") -> List[Timestamp]:
        return pd.date_range(self.start, self.end, freq=freq).tolist()

    def __overlaps_range__(self, other: 'Range') -> bool:
        return ((self.start < other.start) and (self.end > other.start)) or (
                (other.start < self.start) and (other.end > self.start))

    def overlaps(self, other: 'BaseRange') -> bool:
        """
        Returns whether two ranges overlaps

        :param other: other range to be compared with
        :return: True or False whether the two overlaps
        """
        return any([self.__overlaps_range__(range) for range in other])

    def __add__(self, other: BaseRange) -> BaseRange:
        if not isinstance(other, BaseRange):
            raise ValueError(f"add operator not defined for argument of type {type(other)}. Argument should be of "
                             f"type BaseRange")
        if isinstance(other, Range) and self.overlaps(other):
            return Range(min(self.start, other.start), max(self.end, other.end))
        else:
            return CompositeRange([self] + [span for span in other])


class CompositeRange(BaseRange):

    def __init__(self, ranges: List[Range]):
        """
        Ranges made up of multiple ranges

        :param ranges: List of Ranges
        """
        self.ranges = ranges

    def simplify(self) -> BaseRange:
        """
        Simplifies the list into disjoint Range objects, aggregating non-disjoint ranges. If only one range would be
        present, a simple Range object is returned

        :return: BaseRange
        """
        ranges = sorted(self.ranges, key=lambda range: range.start)

        # check overlapping ranges
        overlaps = [first.overlaps(second) for first, second in zip(ranges[:-1], ranges[1:])]

        def merge(agg: List[Range], item: Tuple[int, bool]):
            ith, overlap = item
            return agg + [ranges[ith + 1]] if not (overlap) else agg[:-1] + [agg[-1] + ranges[ith + 1]]

        # merge ranges
        rangeList = reduce(merge, enumerate(overlaps), [ranges[0]])

        if len(rangeList) == 1:
            return rangeList[0]
        else:
            return CompositeRange(rangeList)

    @property
    def start(self) -> Timestamp:
        return min([range.start for range in self.ranges])

    @property
    def end(self) -> Timestamp:
        return max([range.end for range in self.ranges])

    def __iter__(self) -> Iterator['Range']:
        for range in self.ranges:
            yield range

    def range(self, freq="H") -> List[Timestamp]:
        items = np.unique([
            item for range in self.ranges for item in pd.date_range(range.start, range.end, freq=freq)
        ])
        return sorted(items)

    def __add__(self, other: BaseRange):
        if not isinstance(other, BaseRange):
            raise ValueError(f"add operator not defined for argument of type {type(other)}. Argument should be of "
                             f"type BaseRange")
        return CompositeRange(self.ranges + list(other)).simplify()

    def overlaps(self, other: 'BaseRange') -> bool:
        return any([range.overlaps(other) for range in self])


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
