from itertools import islice
import numpy as np

from abc import ABCMeta, abstractproperty, abstractmethod
import pickle

from cgnal.utils.dict import groupIterable

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

    @abstractproperty
    def cached(self):
        raise NotImplementedError

    @abstractmethod
    def kfold(self, int):
        raise NotImplementedError

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
        :return: (Dataset, Dataset), Train and Test Dataset
        """
        fold = int(round(1.0 / ratio))
        if (fold * ratio - 1.0 > 1E-1):
            print(' Approximating ratio of %f to %f' % (ratio, 1.0 / fold))
        return self.kfold(fold).next()



class LazyIterable(Iterable):

    def __init__(self, items):
        if not isinstance(items, IterGenerator):
            raise TypeError("For lazy documents the input must be an IterGenerator(object). Input of type %s passed"
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
        raise CachedIterable(items)


    def batch(self, size = 100):
        for batch in super(LazyIterable, self).batch(size=size):
            yield self.toCached(batch)

    def cache(self):
        return self.toCached(list(self.items))

    def take(self, size):
        def generator():
            return islice(self.items, size)
        return self.__create_instance__( IterGenerator( generator ) )

    def kfold(self, folds=3):
        """
        Kfold iterator of Train, Test Dataset split over the folds

        :param folds: Int, number of folds
        :return: Iterator(Dataset, Dataset), Iterator over the Train, Test splits for the given fold
        """
        for fold in range(folds):

            def test():
                for istory, story in enumerate(self.items):
                    if ((istory + fold) % folds == 0):
                        yield story
                    else:
                        pass

            def train():
                for istory, story in enumerate(self.items):
                    if ((istory + fold) % folds != 0):
                        yield story
                    else:
                        pass

            yield self.__create_instance__(IterGenerator(train)), \
                  self.__create_instance__(IterGenerator(test))


class CachedIterable(Iterable):

    def __init__(self, items):
        self.__items__ = list(items)

    def __len__(self):
        return len(self.items)

    @property
    def items(self):
        return self.__items__

    @property
    def cached(self):
        return True

    def batch(self, size = 100):
        for batch in super(CachedIterable, self).batch(size=size):
            yield self.__create_instance__(batch)


    def kfold(self, folds=3):
        array = np.array(self.items)
        size = range(len(array))
        for fold in xrange(folds):
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



