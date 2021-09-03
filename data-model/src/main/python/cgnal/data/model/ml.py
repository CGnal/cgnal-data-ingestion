import sys
import pickle
import numpy as np  # type: ignore
import pandas as pd  # type: ignore
from abc import ABC, abstractmethod
from typing import Union, Sequence, Optional, TypeVar, Generic, List, Tuple, Any, Iterable as IterableType, Dict, \
    Iterator, overload
from typing_extensions import Literal
from cgnal import T, PathLike
from cgnal.data.model.core import Iterable, LazyIterable, CachedIterable, IterGenerator, PickleSerialization, \
    Serializable
from cgnal.utils.pandas import loc

if sys.version_info[0] < 3:
    from itertools import izip as zip, islice
else:
    from itertools import islice


FeatType = TypeVar('FeatType', List[Any], Tuple[Any], np.ndarray, Dict[str, Any])
LabType = TypeVar('LabType', int, float)
# FeaturesType = TypeVar('FeaturesType', pd.DataFrame, np.ndarray,
#                        List[Union[List[Any], Tuple[Any], np.ndarray]],
#                        Dict[str, Union[List[Any], Tuple[Any], np.ndarray]])
# LabelsType = TypeVar('LabelsType', pd.DataFrame, np.ndarray,  List[Union[int, float]],  Dict[str, Union[int, float]])
# FeaturesType = TypeVar('FeaturesType', np.ndarray, pd.DataFrame, dict, list)
# LabelsType = TypeVar('LabelsType', np.ndarray, pd.DataFrame, dict, list)
FeaturesType = Union[np.ndarray, pd.DataFrame, Dict[str, FeatType], List[FeatType]]
LabelsType = Union[np.ndarray, pd.DataFrame, Dict[str, LabType], List[LabType]]
AllowedTypes = Literal['array', 'pandas', 'dict', 'list']


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
        """
        self.__check_features__(features)
        super(MultiFeatureSample, self).__init__(features, label, name)


Samples = Union[Sample[FeatType, LabType], MultiFeatureSample[LabType]]


# TODO: wouldn't it be better that this class inherits from DillSerializable or PickleSerializable instead of
#  implementing its own write/read methods?
class Dataset(ABC, Generic[FeatType, LabType]):

    @property
    @abstractmethod
    def samples(self) -> IterableType[Samples]: ...

    __default_type__: AllowedTypes = 'pandas'

    @property
    def default_type(self) -> AllowedTypes:
        return self.__default_type__

    @default_type.setter
    def default_type(self, value: AllowedTypes) -> None:
        self.__default_type__ = value

    @property
    def features(self) -> FeaturesType:
        return self.getFeaturesAs(self.default_type)

    @property
    def labels(self) -> LabelsType:
        return self.getLabelsAs(self.default_type)

    @overload
    def getFeaturesAs(self, type: Literal['array']) -> np.ndarray: ...

    @overload
    def getFeaturesAs(self, type: Literal['pandas']) -> pd.DataFrame: ...

    @overload
    def getFeaturesAs(self, type: Literal['dict']) -> Dict[str, FeatType]: ...

    @overload
    def getFeaturesAs(self, type: Literal['list']) -> List[FeatType]: ...

    @abstractmethod
    def getFeaturesAs(self, type: AllowedTypes = 'array') -> FeaturesType: ...

    @overload
    def getLabelsAs(self, type: Literal['array']) -> np.ndarray: ...

    @overload
    def getLabelsAs(self, type: Literal['pandas']) -> pd.DataFrame: ...

    @overload
    def getLabelsAs(self, type: Literal['dict']) -> Dict[str, LabType]: ...

    @overload
    def getLabelsAs(self, type: Literal['list']) -> List[LabType]: ...

    @abstractmethod
    def getLabelsAs(self, type: AllowedTypes = 'array') -> LabelsType: ...

    @abstractmethod
    def union(self, other: 'Dataset') -> 'Dataset': ...

    # TODO: shouldn't this method be abstract other than static?
    @staticmethod
    def createObject(features: FeatType, labels: LabType) -> 'Dataset': ...

    def write(self, filename: str) -> None:
        # TODO: check open mode: mypy suggests that using 'w' creates a fid of type IO[str] while pickle.dump requires
        #  a IO[butes] second argument. This issue would be solved using 'wb' open mode.
        with open(filename, 'w') as fid:
            pickle.dump(self.samples, fid)


# TODO: Shouldn't this class be an ABC? It does not implement Iterable's items, take, cached, kfold and filter
#  abstract methods. Should this class really inherit from Iterable at all?
class IterableDataset(Iterable[Samples],  Dataset[FeatType, LabType]):
    """
    Collection of Sample objects to be used
    """

    @property
    def samples(self) -> IterableType[Samples]:
        return self.items

    @staticmethod
    def checkNames(x: Optional[str]) -> str:
        if x is None:
            raise AttributeError("With type 'dict' all samples must have a name")
        else:
            return x

    # TODO: is it correct that a method of a parent class returns an instance of one of its descendants?
    #  Wouldn't it be better for this method to be abstract and for this class to be an ABC?
    def union(self, other: Dataset[FeatType, LabType]) -> 'LazyDataset':

        if not isinstance(other, Dataset):
            raise ValueError(f"Union can only be done between Datasets. Found {type(other)}")

        def __generator__():
            for sample in self.samples:
                yield sample
            for sample in other.samples:
                yield sample

        return LazyDataset(IterGenerator(__generator__))

    @overload
    def getFeaturesAs(self, type: Literal['array']) -> np.ndarray: ...

    @overload
    def getFeaturesAs(self, type: Literal['pandas']) -> pd.DataFrame: ...

    @overload
    def getFeaturesAs(self, type: Literal['dict']) -> Dict[str, FeatType]: ...

    @overload
    def getFeaturesAs(self, type: Literal['list']) -> List[FeatType]: ...

    def getFeaturesAs(self, type: str = 'array') -> FeaturesType:
        """
        Object of the specified type containing the feature space

        :param type: type of return. Can be one of "pandas", "dict", "list" or "array
        :return: an object of the specified type containing the features
        """

        if type == 'array':
            return np.array([sample.features for sample in self.samples])
        elif type == 'dict':
            return {self.checkNames(sample.name): sample.features for sample in self.samples}
        elif type == 'list':
            return [sample.features for sample in self.samples]
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
    def getLabelsAs(self, type: Literal['array']) -> np.ndarray: ...

    @overload
    def getLabelsAs(self, type: Literal['pandas']) -> pd.DataFrame: ...

    @overload
    def getLabelsAs(self, type: Literal['dict']) -> Dict[str, LabType]: ...

    @overload
    def getLabelsAs(self, type: Literal['list']) -> List[LabType]: ...

    def getLabelsAs(self, type: str = 'array') -> LabelsType:
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

    # TODO: Shouldn't this method be implemented or at least made abstract?
    @staticmethod
    def createObject(features: FeatType, labels: LabType) -> Dataset[FeatType, LabType]:
        raise NotImplementedError


class CachedDataset(CachedIterable[Samples], IterableDataset):

    def to_df(self) -> pd.DataFrame:
        """
        Reformat the Features and Labels as a DataFrame

        :return: DataFrame, Dataframe with features and labels
        """
        return pd.concat({
            "features": self.getFeaturesAs('pandas'),
            "labels": self.getLabelsAs('pandas')}, axis=1)


class LazyDataset(LazyIterable[Samples], IterableDataset):

    @staticmethod
    def toCached(items: IterableType[Samples]) -> CachedDataset:
        return CachedDataset(items)

    def rebalance(self, prob: Dict[LabType, float]) -> 'LazyDataset':
        """
        Create a new LazyDataset instance with samples rebalanced according to probabilites given assigned to each value
        of the labels
        :param prob: dictionary with probabilities of inclusion in the new instance for each value of labels.
            If a label value is missing from dictionary keys, all samples with that label value will be excluded.
        :return:
        """
        def __generator__():
            for sample in self.samples:
                # TODO why this convoluted form? Wouldn't it be neater to use the commented version?
                p = prob.get(sample.label, 1)
                _p = np.random.uniform()
                if _p > p:
                    continue
                yield sample
                # if np.random.uniform() <= prob.get(sample.label, 1):
                #     yield sample

        return LazyDataset(IterGenerator(__generator__))

    def withLookback(self, lookback: int) -> 'LazyDataset':
        """
        Create a LazyDataset with features that are an array of lookback lists of samples' features.

        :param lookback: number of samples' features to look at

        :return: LazyDataset with changed samples
        """

        def __transformed_sample_generator__():
            slices = [islice(self.samples, n, None) for n in range(lookback)]
            for ss in zip(*slices):
                yield Sample(features=np.array([s.features for s in ss]), label=ss[-1].label)
        return LazyDataset(IterGenerator(__transformed_sample_generator__))


# TODO: what is the point of making this class inherit from Serializable and implementing read, write and load methods
#  instead of inheriting from DillSerializable or PickleSerializable and using theit read/write methods?

# TODO: this class' properties 'features' and 'labels' do not necessarily return a pd.DataFrame but all this class'
#  methods that call them actually assume they are. This must be addressed
class PandasDataset(Dataset[FeatType, LabType], Serializable):

    __default_type__: AllowedTypes = 'pandas'

    def __init__(self,
                 features: Union[pd.DataFrame, pd.Series],
                 labels: Optional[Union[pd.DataFrame, pd.Series]] = None) -> None:

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
    def samples(self) -> Iterator[Sample[Dict[str, Any], Any]]:
        for index, row in self.__features__.to_dict(orient="index").items():
            try:
                yield Sample(name=index, features=row, label=self.__labels__.loc[index])
            except KeyError:
                yield Sample(name=index, features=row, label=None)

    @property
    def index(self) -> pd.Index:
        return self.intersection().features.index

    # TODO: what is the point with this method?
    #  Am I missing something or this is just a convoluted way to write an identity?
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
        idx = list(self.features.index.intersection(self.labels.index)) if self.labels is not None \
            else list(self.features.index)
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
        return self.createObject(self.features.dropna(**kwargs),
                                 self.__check_none__(self.labels.dropna(**kwargs) if self.labels is not None else None))

    def intersection(self) -> 'PandasDataset':
        """
        Intersect feature and labels indices

        :return: PandasDataset with features and labels with intersected indices
        """
        idx = list(self.features.index.intersection(self.labels.index)) if self.labels is not None else list(self.features.index)
        return self.loc(idx)

    @overload
    def getFeaturesAs(self, type: Literal['array']) -> np.ndarray: ...

    @overload
    def getFeaturesAs(self, type: Literal['pandas']) -> pd.DataFrame: ...

    @overload
    def getFeaturesAs(self, type: Literal['dict']) -> Dict[str, FeatType]: ...

    @overload
    def getFeaturesAs(self, type: Literal['list']) -> List[FeatType]: ...

    def getFeaturesAs(self, type: AllowedTypes = 'array') -> FeaturesType:
        if type == 'array':
            return np.array(self.__features__)
        elif type == 'pandas':
            return self.__features__
        elif type == 'dict':
            return self.__features__.to_dict(orient="index")
        else:
            raise ValueError(f'"type" value "{type}" not allowed. Only allowed values for "type" are "array", "dict" or '
                             f'"pandas"')

    @overload
    def getLabelsAs(self, type: Literal['array']) -> np.ndarray: ...

    @overload
    def getLabelsAs(self, type: Literal['pandas']) -> pd.DataFrame: ...

    @overload
    def getLabelsAs(self, type: Literal['dict']) -> Dict[str, LabType]: ...

    @overload
    def getLabelsAs(self, type: Literal['list']) -> List[LabType]: ...

    def getLabelsAs(self, type: AllowedTypes = 'array') -> LabelsType:
        if type == 'array':
            return np.array(self.__labels__)
        elif type == 'pandas':
            return self.__labels__
        elif type == 'dict':
            return self.__labels__.to_dict(orient="index")
        else:
            raise ValueError(f'"type" value "{type}" not allowed. Only allowed values for "type" are "array", "dict" or '
                             f'"pandas"')

    def write(self, filename: PathLike, features_cols: str = "features", labels_cols: str = "labels") -> None:
        pd.concat({
            features_cols: self.getFeaturesAs("pandas"),
            labels_cols: self.getLabelsAs("pandas")
        }, axis=1).to_pickle(filename)

    @classmethod
    def read(cls, filename: PathLike, features_cols: str = "features", labels_cols: str = "labels") -> 'PandasDataset':
        _in = pd.read_pickle(filename)
        return cls.createObject(
            _in[features_cols] if features_cols in _in else None,
            _in[labels_cols] if labels_cols in _in else None
        )

    @classmethod
    def load(cls, filename: PathLike):
        return cls.read(filename)

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


