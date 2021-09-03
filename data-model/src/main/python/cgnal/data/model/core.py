import sys
import pickle
from abc import ABC, abstractmethod
from functools import reduce
from itertools import islice
from typing import List, Iterator, Tuple, Callable, Iterable as IterableType, Union, Any, overload, Generic, Sequence

import dill  # type: ignore
import numpy as np  # type: ignore
import pandas as pd  # type: ignore
from pandas.core.tools.datetimes import DatetimeScalar, Timestamp, DatetimeIndex  # type: ignore

from cgnal import T, PathLike
from cgnal.utils.dict import groupIterable

if sys.version_info[0] < 3:
    from future_builtins import filter


class IterGenerator(Generic[T]):
    def __init__(self, generator_function: Callable[[], Iterator[T]]) -> None:
        self.generator_function = generator_function

    @property
    def iterator(self) -> Iterator[T]:
        return self.generator_function()


class Iterable(ABC, IterableType[T], Generic[T]):

    # TODO: shouldn't this class have an __init__ like this?
    #  def __init__(self, items: Union[IterGenerator, IterableType]):
    #      self.__items__ = items

    # TODO: wouldn't it be better if this becomes a classmethod?

    @overload
    def __create_instance__(self, items: IterableType) -> 'CachedIterable': ...

    @overload
    def __create_instance__(self, items: IterGenerator) -> 'LazyIterable': ...

    def __create_instance__(self, items: Union[IterGenerator, IterableType]) -> Union['CachedIterable', 'LazyIterable']:
        obj = self.__new__(type(self))
        obj.__init__(items)
        return obj

    @property
    @abstractmethod
    def items(self) -> IterableType[T]: ...

    @abstractmethod
    def take(self, size: int) -> 'Iterable': ...

    # TODO: shouldn't this method be abstract?
    def filter(self, f: Callable) -> 'Iterable':
        raise NotImplementedError

    @property
    @abstractmethod
    def cached(self) -> bool: ...

    @abstractmethod
    def kfold(self, folds: int) -> Iterator[Tuple['Iterable', 'Iterable']]: ...

    def __iter__(self) -> Iterator[T]:
        for item in self.items:
            yield item

    def batch(self, size: int = 100) -> Iterator[List[T]]:
        """
        Generator that yields batches of items of given size
        :param size: batch size
        :return: list of "size" items
        """
        for batch in groupIterable(self.items, batch_size=size):
            yield batch

    def map(self, f: Callable[[T], Any]) -> Iterator[Any]:
        for item in self.items:
            yield f(item)

    # TODO why does this method return None? What is the point of this method?
    def foreach(self, f: Callable[[T], Any]) -> None:
        for item in self.items:
            f(item)

    # TODO Do we really need this functionality when we have the FeatureProcessing class in cgnal.analytics?
    def hold_out(self, ratio: float) -> Tuple['Iterable', 'Iterable']:
        """
        Train, Test Iterable split

        :param ratio: Int, ratio for splitting
        :return: (Dataset, Dataset), Train and Test Datasets
        """
        fold = int(round(1.0 / ratio))
        if fold * ratio - 1.0 > 1E-1:
            print(' Approximating ratio of %f to %f' % (ratio, 1.0 / fold))
        return next(self.kfold(fold))


# TODO wouldn't it be better for this class to inherit from PickleSerialization or DillSerialization instead of
#  implementing its own save and load methods?
class CachedIterable(Iterable, Generic[T]):

    def __init__(self, items: IterableType[T]):
        self.__items__ = list(items)

    def __len__(self) -> int:
        return len(self.items)

    @property
    def items(self) -> List[T]:
        return self.__items__

    @overload
    def __getitem__(self, item: int) -> T: ...

    @overload
    def __getitem__(self, item: slice) -> List[T]: ...

    def __getitem__(self, item: Union[int, slice]) -> Union[T, List[T]]:
        return self.items[item]

    @property
    def cached(self) -> bool:
        return True

    # TODO: this method's signature is not coherent with parents' method signature
    def batch(self, size: int = 100) -> Iterator['CachedIterable']:
        """
        Generator that yields batches of given size
        :param size: batch size
        :return: CachedIterable with
        """
        for batch in super(CachedIterable, self).batch(size=size):
            yield self.__create_instance__(batch)

    def filter(self, f: Callable[[T], T]) -> 'CachedIterable':
        return self.__create_instance__(filter(f, self.items))

    # TODO this method seems wrong. size is a range and fold is and int, they cannot be summed. Below the proposed fix
    def kfold(self, folds: int = 3) -> Iterator[Tuple['CachedIterable', 'CachedIterable']]:
        """
        Generator to select
        :param folds:
        :return:
        """
        array = np.array(self.items)
        size = range(len(array))
        for fold in range(folds):
            iTest = array[((size + fold) % folds == 0)]
            iTrain = array[((size + fold) % folds != 0)]
            yield self.__create_instance__(array[iTrain]), self.__create_instance__(array[iTest])
        # for fold in range(folds):
        #     yield (self.__create_instance__([x for n, x in enumerate(self.items)
        #                                      if n not in range(fold, len(self), folds)]),
        #            self.__create_instance__(self[fold::folds]))

    def take(self, size: int) -> 'CachedIterable':
        """
        Get first size elements

        :param size: number of items to take
        :return: CachedIterable with only chosen items
        """
        return self.__create_instance__(self.items[:size])

    def save(self, filename: PathLike) -> PathLike:
        with open(filename, 'w') as fid:
            pickle.dump(self.items, fid)  # type: ignore
        return filename

    @staticmethod
    def load(filename: PathLike) -> 'CachedIterable':
        with open(filename, 'r') as fid:
            items = pickle.load(fid)  # type: ignore
        return CachedIterable(items)


class LazyIterable(Iterable, Generic[T]):

    def __init__(self, items: IterGenerator[T]) -> None:
        if not isinstance(items, IterGenerator):
            raise TypeError(f"The input must be an IterGenerator. Input of type {type(items)} passed")
        self.__items__ = items

    @property
    def items(self) -> Iterator[T]:
        return self.__items__.iterator

    @property
    def cached(self) -> bool:
        return False

    @staticmethod
    def toCached(items: IterableType[T]) -> CachedIterable:
        return CachedIterable(items)

    # TODO: this method's signature is not coherent with parents' method signature
    def batch(self, size: int = 100) -> Iterator['CachedIterable']:
        for batch in super(LazyIterable, self).batch(size=size):
            yield self.toCached(batch)

    def cache(self) -> 'CachedIterable':
        return self.toCached(self.items)

    def take(self, size: int) -> 'LazyIterable':
        def generator():
            return islice(self.items, size)

        return self.__create_instance__(IterGenerator(generator))

    def filter(self, f: Callable[[T], T]) -> 'LazyIterable':
        def generator():
            return filter(self.items, f)

        return self.__create_instance__(IterGenerator(generator))

    def kfold(self, folds: int = 3) -> Iterator[Tuple['LazyIterable', 'LazyIterable']]:
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
