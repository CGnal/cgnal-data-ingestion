import numpy as np
import pandas as pd

from abc import ABCMeta, abstractmethod, abstractproperty
from cgnal.data.model.core import Iterable, LazyIterable, CachedIterable, IterGenerator

import pickle


def features_and_labels_to_dataset(X, y=None):

    if y is not None:
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

    def __init__(self, features, label=None, name=None):
        """
        Object representing a single sample of a training or test set

        :param features: features of the sample
        :param label: labels of the sample (optional)
        :param name: id of the sample (optional)

        :type features: list
        :type label: list or None
        :type name: object
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

    # features e labels non hanno un setter. Questo torna un po' scomodo nei transformers
    #
    # @property
    # def features(self):
    #     return self.__features__
    #
    # @features.setter
    # def features(self, value=None):
    #     self.__features__ = value if value is not None else self.getFeaturesAs(self.default_type)

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
        Object of the specified type containing the feature space

        :param type: type of return. Can be one of "pandas", "dict" or "array
        :return: an object of the specified type containing the features
        :rtype: np.array/dict/pd.DataFrame
        """

        if type == 'array':
            return np.array([sample.features for sample in self.samples])
        elif type == 'dict':
            return {sample.name: sample.features for sample in self.samples}
        elif type == 'pandas':
            features = self.getFeaturesAs('dict')
            try:
                return pd.DataFrame(features).T
            except ValueError:
                return pd.Series(features).to_frame("features")
        else:
            raise ValueError('Type %s not allowed' % type)

    def getLabelsAs(self, type='array'):
        """
        Object of the specified type containing the labels

        :param type: type of return. Can be one of "pandas", "dict" or "array
        :return: an object of the specified type containing the features
        :rtype: np.array/dict/pd.DataFrame
        """
        if type == 'array':
            return np.array([sample.label for sample in self.samples])
        elif type == 'dict':
            return {sample.name: sample.label for sample in self.samples}
        elif type == 'pandas':
            labels = self.getLabelsAs('dict')
            try:
                return pd.DataFrame(labels).T
            except ValueError:
                return pd.Series(labels).to_frame("labels")
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
                if _p > p:
                    continue
                yield sample

        return LazyDataset( IterGenerator(__generator__) )


class PandasDataset(Dataset):

    def __init__(self, features, labels):

        if isinstance(features, pd.Series):
            self.__features__ = features.to_frame()
        elif isinstance(features, pd.DataFrame):
            self.__features__ = features
        else:
            raise ValueError("Features must be of type pandas.Series or pandas.DataFrame")

        if isinstance(labels, pd.Series):
            self.__labels__ = labels.to_frame()
        elif isinstance(labels, pd.DataFrame):
            self.__labels__ = labels
        else:
            raise ValueError("Labels must be of type pandas.Series or pandas.DataFrame")

    @property
    def samples(self):
        for index, row in self.__features__.to_dict(orient="index").items():
            try:
                yield Sample(name=index, features=row, label=self.__labels__.loc[index])
            except KeyError:
                yield Sample(name=index, features=row, label=None)

    def intersection(self):
        idx = list(self.features.index.intersection(self.labels.index))
        return PandasDataset(self.features.loc[idx], self.labels.loc[idx])

    def loc(self, idx):
        return PandasDataset(self.features.loc[idx], self.labels.loc[idx])

    def dropna(self, **kwargs):
        return PandasDataset(self.features.dropna(**kwargs), self.labels.dropna(**kwargs))

    def getFeaturesAs(self, type='array'):
        if type == 'array':
            return np.array(self.__features__)
        elif type == 'pandas':
            return self.__features__
        elif type == 'dict':
            return self.__features__.to_dict(orient="index")

    def getLabelsAs(self, type='array'):
        if type == 'array':
            return np.array(self.__labels__)
        elif type == 'pandas':
            return self.__labels__
        elif type == 'dict':
            return self.__labels__.to_dict(orient="index")

    def write(self, filename, features_cols="features", labels_cols="labels"):
        pd.concat({
            features_cols: self.getFeaturesAs("pandas"),
            labels_cols: self.getLabelsAs("pandas")
        }, axis=1).to_pickle(filename)

    @staticmethod
    def read(filename, features_cols="features", labels_cols="labels"):
        _in = pd.read_pickle(filename)
        return PandasDataset(_in[features_cols], _in[labels_cols])


class PandasTimeIndexedDataset(PandasDataset):

    def __init__(self, features, labels):
        super(PandasTimeIndexedDataset, self).__init__(features, labels)
        self.__features__.index = pd.to_datetime(self.__features__.index)
        self.__labels__.index = pd.to_datetime(self.__labels__.index)
