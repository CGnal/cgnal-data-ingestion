try:
    from itertools import izip as zip  # type: ignore
except ImportError:  # will be 3.x series
    pass

import sys
from abc import ABC
from typing import Union, Sequence, Optional, TypeVar, Generic, List, Tuple, Any, Type, Dict, \
    Iterator, overload

import numpy as np  # type: ignore
import pandas as pd  # type: ignore
from pandas import DataFrame, Series
from typing_extensions import Literal

from cgnal import T, PathLike
from cgnal.data.model.core import BaseIterable, LazyIterable, CachedIterable, IterGenerator, PickleSerialization, \
    DillSerialization
from cgnal.utils.decorators import lazyproperty as lazy
from cgnal.utils.pandas import loc

if sys.version_info[0] < 3:
    from itertools import izip as zip, islice
else:
    from itertools import islice

FeatType = TypeVar('FeatType', List[Any], Tuple[Any], np.ndarray, Dict[str, Any])
LabType = TypeVar('LabType', int, float)
FeaturesType = Union[np.ndarray, pd.DataFrame, Dict[str, FeatType], List[FeatType], Iterator[FeatType]]
LabelsType = Union[np.ndarray, pd.DataFrame, Dict[str, LabType], List[LabType], Iterator[LabType]]
AllowedTypes = Literal['array', 'pandas', 'dict', 'list', 'lazy']


def features_and_labels_to_dataset(X: Union[pd.DataFrame, pd.Series],
                                   y: Optional[Union[pd.DataFrame, pd.Series]] = None) -> 'CachedDataset':
    if y is not None:
        df = pd.concat({"features": X, "labels": y}, axis=1)
    else:
        df = pd.concat({"features": X}, axis=1)
        df["labels"] = None

    return CachedDataset([Sample(features, label, name)
                          for features, label, name in zip(np.array(df["features"]), np.array(df["labels"]), df.index)])


class Sample(PickleSerialization, Generic[FeatType, LabType]):
    def __init__(self, features: FeatType, label: Optional[LabType] = None, name: Optional[str] = None) -> None:
        """
        Object representing a single sample of a training or test set

        :param features: features of the sample
        :param label: labels of the sample (optional)
        :param name: id of the sample (optional)
        """
        self.features: FeatType = features
        self.label: Optional[LabType] = label
        self.name: Optional[str] = name


class MultiFeatureSample(Sample[List[np.ndarray], LabType]):
    @staticmethod
    def __check_features__(features: List[np.ndarray]) -> None:
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

    def __init__(self, features: List[np.ndarray], label: Optional[LabType] = None, name: str = None) -> None:
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


SampleTypes = Union[Sample[FeatType, LabType], MultiFeatureSample[LabType]]


class Dataset(BaseIterable[SampleTypes], Generic[FeatType, LabType], ABC):

    @property
    def __lazyType__(self) -> Type[LazyIterable]:
        return LazyDataset

    @property
    def __cachedType__(self) -> Type[CachedIterable]:
        return CachedDataset

    @staticmethod
    def checkNames(x: Optional[str]) -> str:
        if x is None:
            raise AttributeError("With type 'dict' all samples must have a name")
        else:
            return x

    @overload
    def getFeaturesAs(self, type: Literal['array']) -> np.ndarray:
        ...

    @overload
    def getFeaturesAs(self, type: Literal['pandas']) -> pd.DataFrame:
        ...

    @overload
    def getFeaturesAs(self, type: Literal['dict']) -> Dict[str, FeatType]:
        ...

    @overload
    def getFeaturesAs(self, type: Literal['list']) -> List[FeatType]:
        ...

    @overload
    def getFeaturesAs(self, type: Literal['lazy']) -> Iterator[FeatType]:
        ...

    def getFeaturesAs(self, type: AllowedTypes = 'array') -> FeaturesType:
        """
        Object of the specified type containing the feature space

        :param type: type of return. Can be one of "pandas", "dict", "list" or "array
        :return: an object of the specified type containing the features
        """

        if type == 'array':
            return np.array([sample.features for sample in self])
        elif type == 'dict':
            return {self.checkNames(sample.name): sample.features for sample in self}
        elif type == 'list':
            return [sample.features for sample in self]
        elif type == 'lazy':
            return (sample.features for sample in self)
        elif type == 'pandas':
            try:
                features: Union[Dict[str, FeatType], List[FeatType]] = self.getFeaturesAs('dict')
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
            raise ValueError(f'Type {type} not allowed')

    @overload
    def getLabelsAs(self, type: Literal['array']) -> np.ndarray:
        ...

    @overload
    def getLabelsAs(self, type: Literal['pandas']) -> pd.DataFrame:
        ...

    @overload
    def getLabelsAs(self, type: Literal['dict']) -> Dict[str, LabType]:
        ...

    @overload
    def getLabelsAs(self, type: Literal['list']) -> List[LabType]:
        ...

    @overload
    def getLabelsAs(self, type: Literal['lazy']) -> Iterator[LabType]:
        ...

    def getLabelsAs(self, type: AllowedTypes = 'array') -> LabelsType:
        """
        Object of the specified type containing the labels

        :param type: type of return. Can be one of "pandas", "dict", "list" or "array
        :return: an object of the specified type containing the features
        :rtype: np.array/dict/pd.DataFrame
        """
        if type == 'array':
            return np.array([sample.label for sample in self])
        elif type == 'dict':
            return {self.checkNames(sample.name): sample.label for sample in self}
        elif type == 'list':
            return [sample.label for sample in self]
        elif type == 'lazy':
            return (sample.label for sample in self)
        elif type == 'pandas':
            try:
                labels: Union[List[LabType], Dict[str, LabType]] = self.getLabelsAs('dict')
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

    def union(self, other: 'Dataset') -> 'Dataset':

        if not isinstance(other, Dataset):
            raise ValueError("Union can only be done between Datasets. Found %s" % str(type(other)))

        def __generator__():
            for sample in self:
                yield sample
            for sample in other:
                yield sample

        return LazyDataset(IterGenerator(__generator__))


class CachedDataset(CachedIterable[SampleTypes], Dataset):

    def to_df(self) -> pd.DataFrame:
        """
        Reformat the Features and Labels as a DataFrame

        :return: DataFrame, Dataframe with features and labels
        """
        return pd.concat({
            "features": self.getFeaturesAs('pandas'),
            "labels": self.getLabelsAs('pandas')}, axis=1)

    @property
    def asPandasDataset(self) -> 'PandasDataset':
        return PandasDataset(self.getFeaturesAs("pandas"), self.getLabelsAs("pandas"))


class LazyDataset(LazyIterable[Sample], Dataset):

    def withLookback(self, lookback: int) -> 'LazyDataset':
        """
        Create a LazyDataset with features that are an array of lookback lists of samples' features.

        :param lookback: number of samples' features to look at

        :return: LazyDataset with changed samples
        """

        def __transformed_sample_generator__() -> Iterator[Sample]:
            slices = [islice(self, n, None) for n in range(lookback)]
            for ss in zip(*slices):
                yield Sample(features=np.array([s.features for s in ss]), label=ss[-1].label)

        return LazyDataset(IterGenerator(__transformed_sample_generator__))

    def features(self) -> Iterator[FeatType]:
        return self.getFeaturesAs('lazy')

    def labels(self) -> Iterator[LabType]:
        return self.getLabelsAs('lazy')

    def getFeaturesAs(self, type: AllowedTypes = 'lazy') -> FeaturesType:
        return super(LazyDataset, self).getFeaturesAs(type)

    def getLabelsAs(self, type: AllowedTypes = 'lazy') -> FeaturesType:
        return super(LazyDataset, self).getLabelsAs(type)


class PandasDataset(Dataset[FeatType, LabType], DillSerialization):

    def __init__(self, features: Union[DataFrame, Series], labels: Union[DataFrame, Series, None] = None) -> None:

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
        elif labels is None:
            self.__labels__ = labels
        else:
            raise ValueError("Labels must be of type pandas.Series or pandas.DataFrame")

    @property
    def items(self) -> Iterator[Sample]:
        for index, row in self.__features__.to_dict(orient="index").items():
            try:
                yield Sample(name=index, features=row, label=self.__labels__.loc[index])
            except KeyError:
                yield Sample(name=index, features=row, label=None)

    @property
    def cached(self) -> bool:
        return True

    @lazy
    def features(self) -> pd.DataFrame:
        return self.getFeaturesAs("pandas")

    @lazy
    def labels(self) -> pd.DataFrame:
        return self.getLabelsAs("pandas")

    @property
    def index(self) -> pd.Index:
        return self.intersection().features.index

    @staticmethod
    def __check_none__(lab: Optional[T]) -> Optional[T]:
        return lab if lab is not None else None

    @staticmethod
    def createObject(features: Union[pd.DataFrame, pd.Series],
                     labels: Optional[Union[pd.DataFrame, pd.Series]]) -> 'PandasDataset':
        return PandasDataset(features, labels)

    def __len__(self) -> int:
        return len(self.index)

    def take(self, n: int) -> 'PandasDataset':
        idx = list(self.features.index.intersection(self.labels.index)) if self.labels is not None else list(
            self.features.index)
        return self.loc(idx[:n])

    def loc(self, idx: List[Any]) -> 'PandasDataset':
        """
        Find given indices in features and labels

        :param idx: input indices
        :return: PandasDataset with features and labels filtered on input indices
        """

        features = loc(self.features, idx) if isinstance(self.features, pd.DataFrame) else self.features.loc[idx]
        labels = self.labels.loc[idx] if self.labels is not None else None

        return self.createObject(features, labels)

    def dropna(self, **kwargs) -> 'PandasDataset':
        """
        Drop NAs from feature and labels

        :return: PandasDataset with features and labels without NAs
        """

        kwargs_feat = {(k.split('__')[1] if k.startswith('feat__') else k): v for k, v in kwargs.items() if not k.startswith('labs__')}
        kwargs_labs = {k.split('__')[1]: v for k, v in kwargs.items() if k.startswith('labs__')}

        return self.createObject(self.features.dropna(**kwargs_feat),
                                 self.__check_none__(self.labels.dropna(**kwargs_labs) if self.labels is not None else None))

    def intersection(self) -> 'PandasDataset':
        """
        Intersect feature and labels indices

        :return: PandasDataset with features and labels with intersected indices
        """
        idx = list(self.features.index.intersection(self.labels.index)) if self.labels is not None else list(
            self.features.index)
        return self.loc(idx)

    @overload
    def getFeaturesAs(self, type: Literal['array']) -> np.ndarray:
        ...

    @overload
    def getFeaturesAs(self, type: Literal['pandas']) -> pd.DataFrame:
        ...

    @overload
    def getFeaturesAs(self, type: Literal['dict']) -> Dict[str, FeatType]:
        ...

    @overload
    def getFeaturesAs(self, type: Literal['list']) -> List[FeatType]:
        ...

    def getFeaturesAs(self, type: AllowedTypes = 'array') -> FeaturesType:
        if type == 'array':
            return np.array(self.__features__)
        elif type == 'pandas':
            return self.__features__
        elif type == 'dict':
            return {k: list(row) for k, row in self.__features__.iterrows()}
        else:
            raise ValueError(
                f'"type" value "{type}" not allowed. Only allowed values for "type" are "array", "dict" or '
                f'"pandas"')

    @overload
    def getLabelsAs(self, type: Literal['array']) -> np.ndarray:
        ...

    @overload
    def getLabelsAs(self, type: Literal['pandas']) -> pd.DataFrame:
        ...

    @overload
    def getLabelsAs(self, type: Literal['dict']) -> Dict[str, LabType]:
        ...

    @overload
    def getLabelsAs(self, type: Literal['list']) -> List[LabType]:
        ...

    def getLabelsAs(self, type: AllowedTypes = 'array') -> LabelsType:
        if type == 'array':
            nCols = len(self.__labels__.columns)
            return np.array(self.__labels__) if nCols > 1 else np.array(self.__labels__[self.__labels__.columns[0]])
        elif type == 'pandas':
            return self.__labels__
        elif type == 'dict':
            nCols = len(self.__labels__.columns)
            return self.__labels__.to_dict(orient="index") if nCols > 1 \
                else self.__labels__[self.__labels__.columns[0]].to_dict()
        else:
            raise ValueError(
                f'"type" value "{type}" not allowed. Only allowed values for "type" are "array", "dict" or '
                f'"pandas"')

    @classmethod
    def from_sequence(cls, datasets: Sequence['PandasDataset']):
        features_iter, labels_iter = zip(*[(dataset.features, dataset.labels) for dataset in datasets])
        labels = None if all([lab is None for lab in labels_iter]) else pd.concat(labels_iter)
        features = pd.concat(features_iter)
        return cls.createObject(features, labels)

    def union(self, other: 'Dataset') -> 'Dataset':
        if isinstance(other, self.__class__):
            features = pd.concat([self.features, other.features])
            labels = pd.concat([self.labels, other.labels]) \
                if not (self.labels is None and other.labels is None) \
                else None
            return self.createObject(features, labels)
        else:
            return Dataset.union(self, other)


class PandasTimeIndexedDataset(PandasDataset):

    def __init__(self,
                 features: Union[pd.DataFrame, pd.Series],
                 labels: Optional[Union[pd.DataFrame, pd.Series]] = None) -> None:
        super(PandasTimeIndexedDataset, self).__init__(features, labels)
        self.__features__.rename(index=pd.to_datetime, inplace=True)
        if self.labels is not None:
            self.__labels__.rename(index=pd.to_datetime, inplace=True)

    @staticmethod
    def createObject(features: Union[pd.DataFrame, pd.Series],
                     labels: Optional[Union[pd.DataFrame, pd.Series]] = None) -> 'PandasTimeIndexedDataset':
        return PandasTimeIndexedDataset(features, labels)
