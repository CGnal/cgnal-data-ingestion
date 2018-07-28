import numpy as np
import pandas as pd

from abc import ABCMeta, abstractmethod, abstractproperty
from cgnal.data.model.core import Iterable, LazyIterable, CachedIterable, IterGenerator

import pickle

def features_and_labels_to_dataset(X, y=None):

    if (y is not None):
        df = pd.concat({"features": X, "labels": y}, axis=1)
    else:
        df = pd.concat({"features": X}, axis=1)
        df["labels"] = None

    return CachedDataset([Sample(features, label, name)
                          for features, label, name in zip(np.array(df["features"]), np.array(df["labels"]), df.index)])


class Sample(object):
    """
    Object representing a single sample of a training or test set
    """

    def __init__(self, features, label, name=None):
        """
        Object representing a single sample of a training or test set

        :param features: List(object), features of the sample
        :param label: List(object), label of the sample
        :param name: object, id of the sample (optional)
        """
        self.features = features
        self.label = label
        self.name = name


class Dataset(object):

    __metaclass__ = ABCMeta

    @abstractproperty
    def samples(self):
        raise NotImplementedError


    __default_type__ = 'pandas'

    @property
    def default_type(self):
        return self.__default_type__

    @default_type.setter
    def default_type(self, value):
        self.__default_type__ = value

    @property
    def features(self):
        return self.getFeaturesAs(self.default_type)

    @property
    def labels(self):
        return self.getLabelsAs(self.default_type)

    @abstractmethod
    def getFeaturesAs(self, type='array'):
        raise NotImplementedError

    @abstractmethod
    def getLabelsAs(self, type='array'):
        raise NotImplementedError

    def write(self, filename):
        with open(filename, 'w') as fid:
            pickle.dump(self.samples, fid)


class IterableDataset(Iterable, Dataset):
    """
    Collection of Samples object to be used
    """

    @property
    def samples(self):
        return self.items

    def getFeaturesAs(self, type='array'):
        """
        Dictionary with key name of the sample and value the associated features

        :return: dict, Dictionary with key name of the sample and value the associated features

        This can easily be turned into a DataFrame or a Serie (when the sample are not a size-fixed
        number of features) using the following commands:

            df = pd.DataFrame( dataset.features ).T
            s  = pd.Series( dataset.features )
        """
        if type is 'array':
            return np.array([sample.features for sample in self.samples])
        elif type is 'dict':
            return {sample.name: sample.features for sample in self.samples}
        elif type is 'pandas':
            features = self.getFeaturesAs('dict')
            try:
                return pd.DataFrame(features).T
            except(ValueError):
                return pd.Series(features)
        else:
            raise ValueError('Type %s not allowed' % type)

    def getLabelsAs(self, type='array'):
        """
        Dictionary with key name of the sample and value the associated label

        :return: dict, Dictionary with key name of the sample and value the associated label

        This can easily be turned into a Serie using the following commands:

            s  = pd.Series( dataset.labels )
        """
        if type is 'array':
            return np.array([sample.label for sample in self.samples])
        elif type is 'dict':
            return {sample.name: sample.label for sample in self.samples}
        elif type is 'pandas':
            return pd.Series(self.getLabelsAs('dict'))
        else:
            raise ValueError('Type %s not allowed' % type)


class CachedDataset(CachedIterable, IterableDataset):

    def to_df(self):
        """
        Reformat the Features and Labels as a DataFrame

        :return: DataFrame, Dataframe with features and labels
        """
        return pd.concat({
            "features": self.getFeaturesAs('pandas'),
            "labels": self.getLabelsAs('pandas')}, axis=1)



class LazyDataset(LazyIterable, IterableDataset):

    @staticmethod
    def toCached(items):
        return CachedDataset(items)

    def rebalance(self, prob):
        def __generator__():
            for sample in self.samples:
                p = prob.get(sample.label, 1)
                _p = np.random.uniform()
                if (_p > p):
                    continue
                yield sample

        return LazyDataset( IterGenerator(__generator__) )


class PandasDataset(Dataset):

    def __init__(self, features, labels):
        self.__features__ = features
        self.__labels__ = labels

    @staticmethod
    def __to_dict__(df):
        if isinstance(df, pd.Series):
            return df.to_dict()
        elif isinstance(df, pd.DataFrame):
            return df.to_dict(orient='index')

    @property
    def samples(self):
        for index, row in self.__to_dict__(self.__features__).items():
            yield Sample(name=index, features=row, label=self.__labels__.loc[index])

    def intersection(self):
        idx = pd.to_datetime(self.features.index.intersection(self.labels.index))
        return PandasDataset(self.features.loc[idx], self.labels.loc[idx])

    def loc(self, idx):
        return PandasDataset(self.features.loc[idx], self.labels.loc[idx])

    def getFeaturesAs(self, type='array'):
        if type is 'array':
            return np.array(self.__features__)
        elif type is 'pandas':
            return self.__features__
        elif type is 'dict':
            return self.__to_dict__( self.__features__ )

    def getLabelsAs(self, type='array'):
        if type is 'array':
            return np.array(self.__labels__)
        elif type is 'pandas':
            return self.__labels__
        elif type is 'dict':
            return self.__to_dict__( self.__labels__ )

    def write(self, filename):
        pd.concat({
            "features": self.getFeaturesAs("pandas"),
            "labels": self.getLabelsAs("pandas")
        }, axis=1).to_pickle(filename)

    @staticmethod
    def read(filename):
        _in = pd.read_pickle(filename)
        return PandasDataset(_in["features"], _in["labels"])