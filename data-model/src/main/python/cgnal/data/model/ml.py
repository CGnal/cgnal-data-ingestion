import pickle
import numpy as np
import pandas as pd

try:
    from itertools import izip as zip
except ImportError:  # will be 3.x series
    pass

from itertools import islice
from abc import ABCMeta, abstractmethod, abstractproperty
from cgnal.data.model.core import Iterable, LazyIterable, CachedIterable, IterGenerator


def features_and_labels_to_dataset(X, y=None):

    if y is not None:
        df = pd.concat({"features": X, "labels": y}, axis=1)
    else:
        df = pd.concat({"features": X}, axis=1)
        df["labels"] = None

    return CachedDataset([Sample(features, label, name)
                          for features, label, name in zip(np.array(df["features"]), np.array(df["labels"]), df.index)])


class Sample(object):
    def __init__(self, features, label=None, name=None):
        """
        Object representing a single sample of a training or test set

        :param features: features of the sample
        :param label: labels of the sample (optional)
        :param name: id of the sample (optional)

        :type features: list or couple
        :type label: float, int or None
        :type name: object
        """
        self.features = features
        self.label = label
        self.name = name


class MultiFeatureSample(Sample):
    @staticmethod
    def __check_features__(features):
        """
        Check that features is list of lists

        :param features: list of lists
        :return: None
        """

        if not isinstance(features, list):
            raise TypeError("features must be a list")

        for f in features:
            if not isinstance(f, np.ndarray):
                raise TypeError("all features elements must be np.ndarrays")

    def __init__(self, features, label=None, name=None):
        """
        Object representing a single sample of a training or test set

        :param features: features of the sample
        :param label: labels of the sample (optional)
        :param name: id of the sample (optional)

        :type features: list of lists
        :type label: float, int or None
        :type name: object
        """
        self.__check_features__(features)
        super(MultiFeatureSample, self).__init__(features, label, name)


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

    @abstractmethod
    def union(self, other):
        raise NotImplementedError

    def write(self, filename):
        with open(filename, 'w') as fid:
            pickle.dump(self.samples, fid)


class IterableDataset(Iterable, Dataset):
    """
    Collection of Sample objects to be used
    """

    @property
    def samples(self):
        return self.items

    @staticmethod
    def checkNames(x):
        if x is None:
            raise AttributeError("With type 'dict' all samples must have a name")
        else:
            return x

    def union(self, other):

        if not isinstance(other, Dataset):
            raise ValueError("Union can only be done between Datasets. Found %s" % str(type(other)) )

        def __generator__():
            for sample in self.samples:
                yield sample
            for sample in other.samples:
                yield sample

        return LazyDataset(IterGenerator(__generator__))


    def getFeaturesAs(self, type='array'):
        """
        Object of the specified type containing the feature space

        :param type: type of return. Can be one of "pandas", "dict", "list" or "array
        :return: an object of the specified type containing the features
        :rtype: np.array/dict/pd.DataFrame
        """

        if type == 'array':
            return np.array([sample.features for sample in self.samples])
        elif type == 'dict':
            return {self.checkNames(sample.name): sample.features for sample in self.samples}
        elif type == 'list':
            return [sample.features for sample in self.samples]
        elif type == 'pandas':
            try:
                features = self.getFeaturesAs('dict')
                try:
                    return pd.DataFrame(features).T
                except ValueError:
                    return pd.Series(features).to_frame("features")
            except AttributeError:
                features = self.getFeaturesAs('list')
                try:
                    return pd.DataFrame(features)
                except ValueError:
                    return pd.Series(features).to_frame("features")

        else:
            raise ValueError('Type %s not allowed' % type)

    def getLabelsAs(self, type='array'):
        """
        Object of the specified type containing the labels

        :param type: type of return. Can be one of "pandas", "dict", "list" or "array
        :return: an object of the specified type containing the features
        :rtype: np.array/dict/pd.DataFrame
        """
        if type == 'array':
            return np.array([sample.label for sample in self.samples])
        elif type == 'dict':
            return {self.checkNames(sample.name): sample.label for sample in self.samples}
        elif type == 'list':
            return [sample.label for sample in self.samples]
        elif type == 'pandas':
            try:
                labels = self.getLabelsAs('dict')
                try:
                    return pd.DataFrame(labels).T
                except ValueError:
                    return pd.Series(labels).to_frame("labels")
            except AttributeError:
                labels = self.getLabelsAs('list')
                try:
                    return pd.DataFrame(labels)
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
        return LazyDataset(IterGenerator(__generator__))

    def withLookback(self, lookback):
        """
        Create a LazyDataset with features that are an array of lookback lists of samples' features.

        :param lookback: number of samples' features to look at
        :type lookback: int
        :return: Dataset with changed samples
        :rtype: LazyDataset
        """

        def __transformed_sample_generator__():
            slices = [islice(self.samples, n, None) for n in range(lookback)]
            for ss in zip(*slices):
                yield Sample(features=(np.array([s.features for s in ss])), label=ss[-1].label)
        return LazyDataset(IterGenerator(__transformed_sample_generator__))


class PandasDataset(Dataset):

    def __init__(self, features, labels=None):

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
        elif isinstance(labels, None):
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

    @property
    def index(self):
        return self.intersection().features.index

    def __len__(self):
        return len(self.index)

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

    def union(self, other):
        if isinstance(other, PandasDataset):
            return PandasDataset(pd.concat([self.features, other.features]),
                                 pd.concat([self.labels, other.labels]))
        else:
            return Dataset.union(self, other)


class PandasTimeIndexedDataset(PandasDataset):

    def __init__(self, features, labels):
        super(PandasTimeIndexedDataset, self).__init__(features, labels)
        self.__features__.index = pd.to_datetime(self.__features__.index)
        self.__labels__.index = pd.to_datetime(self.__labels__.index)

    def intersection(self):
        idx = list(self.features.index.intersection(self.labels.index))
        return PandasTimeIndexedDataset(self.features.loc[idx], self.labels.loc[idx])

    def loc(self, idx):
        return PandasTimeIndexedDataset(self.features.loc[idx], self.labels.loc[idx])

    def dropna(self, **kwargs):
        return PandasTimeIndexedDataset(self.features.dropna(**kwargs), self.labels.dropna(**kwargs))

    @staticmethod
    def read(filename, features_cols="features", labels_cols="labels"):
        _in = pd.read_pickle(filename)
        return PandasTimeIndexedDataset(_in[features_cols], _in[labels_cols])


