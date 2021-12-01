import pickle
import sys
from abc import ABC, abstractmethod
from functools import reduce
from itertools import islice
from typing import List, Iterable, Iterator, Tuple, Union, Type, Any

import dill  # type: ignore
import numpy as np  # type: ignore
import pandas as pd  # type: ignore
from pandas.core.tools.datetimes import DatetimeScalar, Timestamp  # type: ignore

from cgnal.typing import PathLike, T, T_co
from cgnal.utils.dict import groupIterable

if sys.version_info[0] < 3:
    pass

from typing import Generic, Callable, Sequence


class Serializable(ABC):

    @abstractmethod
    def write(self, filaname: PathLike) -> None: ...

    @classmethod
    @abstractmethod
    def load(cls, filename: PathLike) -> 'Serializable': ...


class PickleSerialization(Serializable):

    def write(self, filename: PathLike) -> None:
        """
        Write instance as pickle

        :param filename: Name of the file where to save the instance

        :return: None
        """
        with open(filename, 'wb') as fid:
            pickle.dump(self, fid)

    @classmethod
    def load(cls, filename: PathLike) -> 'PickleSerialization':
        """
        Load instance from pickle

        :param filename: Name of the file to be read
        :return: Instance of the read Model
        """
        with open(filename, 'rb') as fid:
            return pickle.load(fid)


class DillSerialization(Serializable):

    def write(self, filename: PathLike) -> None:
        """
        Write instance as pickle

        :param filename: Name of the file where to save the instance

        :return: None
        """
        with open(filename, 'wb') as fid:
            dill.dump(self, fid)

    @classmethod
    def load(cls, filename: PathLike) -> 'DillSerialization':
        """
        Load instance from file

        :param filename: Name of the file to be read
        :return: Instance of the read Model
        """
        with open(filename, 'rb') as fid:
            return dill.load(fid)


class IterGenerator(Generic[T]):
    def __init__(self, generator_function: Callable[[], Iterator[T]]):
        """
        Class that allows a given generator to be accessed as an Iterator via .iterator property.

        :param generator_function: function that outputs a generator
        """
        self.generator_function = generator_function

    @property
    def iterator(self) -> Iterator[T]:
        """
        Property to access iterator for the given generator function

        :return: an iterator
        """
        return self.generator_function()


class BaseIterable(Generic[T], ABC):
    """
    Class to provide base interfaces and methods for enhancing iterables classes and enable more functional
    approaches. In particular, the class provides among others implementation for map, filter and foreach
    methods.
    """

    @property
    @abstractmethod
    def items(self) -> Iterable[T]:
        """
        Property representing the iterable elements

        :return: Iterable[T]
        """
        raise NotImplementedError

    @property
    @abstractmethod
    def cached(self) -> bool:
        """
        Whether the iterable is cached in memory or lazy

        :return: boolean indicating whether iterable is fully-stored in memory
        """
        raise NotImplementedError

    @property
    def __lazyType__(self) -> 'Type[LazyIterable]':
        return LazyIterable

    @property
    def __cachedType__(self) -> 'Type[CachedIterable]':
        return CachedIterable

    @property
    def asLazy(self) -> 'LazyIterable':
        """
        Provide a lazy representation of the iterable

        :return: lazy iterable
        """

        def generator():
            for item in self:
                yield item

        return self.__lazyType__(IterGenerator(generator))

    @property
    def asCached(self) -> 'CachedIterable':
        """
        Provide a in-memory cached representation of the iterable

        :return: cached iterable
        """
        return self.__cachedType__(list(self.items))

    def take(self, size: int) -> 'Iterable[T]':
        """
        Take the first n elements of the iterables

        :param size: number of elements to be taken
        :return: cached iterable with the first elements
        """
        return self.__cachedType__(list(islice(self, size)))

    def filter(self, f: Callable[[T], bool]) -> 'LazyIterable[T]':
        """
        Return an iterable where elements have been filtered based on a boolean function

        :param f: boolean function that selects items
        :return: lazy iterable with elements filtered
        """
        def generator():
            for item in self:
                if f(item):
                    yield item

        return self.__lazyType__(IterGenerator(generator))

    def __iter__(self) -> Iterator[T]:
        for item in self.items:
            yield item

    def batch(self, size: int = 100) -> 'Iterator[CachedIterable[T]]':
        """
        Return an iterator of batches of size *size*.

        :param size: dimension of the batch
        :return: iterator of batches
        """
        for batch in groupIterable(self.items, batch_size=size):
            yield self.__cachedType__(batch)

    def map(self, f: Callable[[T], T_co]) -> 'LazyIterable[T_co]':
        """
        Map all elements of an iterable with the provided function

        :param f: function to be used to map the elements
        :return: mapped iterable
        """
        def generator():
            for item in self:
                yield f(item)

        return self.__lazyType__(IterGenerator(generator))

    def foreach(self, f: Callable[[T], Any]):
        """
        Execute the provided function on each element of the iterable

        :param f: function to be executed for each element
        :return: None
        """
        for doc in self.items:
            f(doc)


class LazyIterable(BaseIterable, Generic[T]):
    """
    Base class to be used for implementing lazy iterables
    """

    def __init__(self, items: IterGenerator):
        """
        Base class to be used for implementing lazy iterables

        :param items: IterGenerator containing the generator of items
        """
        if not isinstance(items, IterGenerator):
            raise TypeError("For lazy iterables the input must be an IterGenerator(object). Input of type %s passed"
                            % type(items))
        self.__items__ = items

    @property
    def items(self) -> Iterator[T]:
        return self.__items__.iterator

    @property
    def cached(self) -> bool:
        return False


class CachedIterable(BaseIterable, Generic[T], DillSerialization):
    """
    Base class to be used for implementing cached iterables
    """

    def __init__(self, items: Sequence[T]):
        """
        Base class to be used for implementing cached iterables

        :param items: sequence or iterable of elements
        """
        self.__items__ = list(items)

    def __len__(self) -> int:
        return len(self.items)

    @property
    def items(self) -> Sequence[T]:
        return self.__items__

    def __getitem__(self, item: int) -> T:
        return self.items[item]

    @property
    def cached(self) -> bool:
        return True


class BaseRange(ABC):
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
    def __iter__(self) -> Iterator['Range']: ...

    @abstractmethod
    def __add__(self, other: 'BaseRange') -> 'BaseRange': ...

    @abstractmethod
    def overlaps(self, other: 'BaseRange') -> bool: ...

    @abstractmethod
    def range(self, freq="H") -> List[Timestamp]: ...

    def __str__(self) -> str:
        return " // ".join([f"{r.start}-{r.end}" for r in self])

    @property
    def days(self) -> List[Timestamp]:
        """
        Create date range with daily frequency

        :return: list of pd.Timestamp from start to end with daily frequency
        """
        return self.range(freq="1D")

    @property
    def business_days(self) -> List[Timestamp]:
        """
        Create date range with daily frequency

        :return: list of pd.Timestamp from start to end with daily frequency including only days from Mon to Fri
        """
        return self.range(freq="1B")

    @property
    def minutes_15(self) -> List[Timestamp]:
        """
        Create date range with daily frequency

        :return: list of pd.Timestamp from start to end with 15 minutes frequency
        """
        return self.range(freq="15T")


class Range(BaseRange):

    def __init__(self, start: DatetimeScalar, end: DatetimeScalar) -> None:
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
        return any([self.__overlaps_range__(r) for r in other])

    def __add__(self, other: BaseRange) -> Union['CompositeRange', 'Range']:
        if not isinstance(other, Range):
            raise ValueError(f"add operator not defined for argument of type {type(other)}. Argument should be of "
                             f"type Range")
        if isinstance(other, Range) and self.overlaps(other):
            return Range(min(self.start, other.start), max(self.end, other.end))
        else:
            return CompositeRange([self] + [span for span in other])


class CompositeRange(BaseRange):

    def __init__(self, ranges: List[Range]) -> None:
        """
        Ranges made up of multiple ranges

        :param ranges: List of Ranges
        """
        self.ranges = ranges

    def simplify(self) -> Union['CompositeRange', Range]:
        """
        Simplifies the list into disjoint Range objects, aggregating non-disjoint ranges. If only one range would be
        present, a simple Range object is returned

        :return: BaseRange
        """
        ranges = sorted(self.ranges, key=lambda r: r.start)

        # check overlapping ranges
        overlaps = [first.overlaps(second) for first, second in zip(ranges[:-1], ranges[1:])]

        def merge(agg: List[Range], item: Tuple[int, bool]) -> List[Range]:
            ith, overlap = item
            return agg + [ranges[ith + 1]] if not overlap else agg[:-1] + [agg[-1] + ranges[ith + 1]]  # type: ignore

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

    def __add__(self, other: BaseRange) -> BaseRange:
        if not isinstance(other, BaseRange):
            raise ValueError(f"add operator not defined for argument of type {type(other)}. Argument should be of "
                             f"type BaseRange")
        return CompositeRange(self.ranges + list(other)).simplify()

    def overlaps(self, other: 'BaseRange') -> bool:
        return any([r.overlaps(other) for r in self])
