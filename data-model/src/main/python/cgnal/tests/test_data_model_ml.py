import os

import numpy as np
import pandas as pd
import unittest

from cgnal.tests.core import TestCase, logTest
from cgnal.data.model.ml import LazyDataset, IterGenerator, MultiFeatureSample, Sample, PandasDataset, \
    PandasTimeIndexedDataset
from cgnal.tests import TMP_FOLDER

class LazyDatasetTests(TestCase):

    @logTest
    def test_withLookback_MultiFeatureSample(self):
        samples = [MultiFeatureSample(features=[np.array([100., 101.]), np.array([np.NaN])], label=1.),
                   MultiFeatureSample(features=[np.array([102., 103.]), np.array([1.])], label=2.),
                   MultiFeatureSample(features=[np.array([104., 105.]), np.array([2.])], label=3.),
                   MultiFeatureSample(features=[np.array([106., 107.]), np.array([3.])], label=4.),
                   MultiFeatureSample(features=[np.array([108., 109.]), np.array([4.])], label=5.),
                   MultiFeatureSample(features=[np.array([110., 111.]), np.array([5.])], label=6.),
                   MultiFeatureSample(features=[np.array([112., 113.]), np.array([6.])], label=7.),
                   MultiFeatureSample(features=[np.array([114., 115.]), np.array([7.])], label=8.),
                   MultiFeatureSample(features=[np.array([116., 117.]), np.array([8.])], label=9.)]

        def samples_gen():
            for sample in samples:
                if not any([np.isnan(x).any() for x in sample.features]):
                    yield sample

        X1 = np.array([[[102., 103.],[104., 105.],[106., 107.]], [[104., 105.],[106., 107.],[108., 109.]],
                       [[106., 107.],[108., 109.],[110., 111.]], [[108., 109.],[110., 111.],[112., 113.]]])
        y1 = np.array([[[1.],[2.],[3.]], [[2.],[3.],[4.]], [[3.],[4.],[5.]], [[4.],[5.],[6.]]])
        lab1 = np.array([4., 5., 6., 7.])
        X2 = np.array([[[110., 111.],[112., 113.],[114., 115.]], [[112., 113.],[114., 115.],[116., 117.]]])
        y2 = np.array([[[5.],[6.],[7.]], [[6.],[7.],[8.]]])
        lab2 = np.array([8., 9.])

        lookback = 3
        batch_size = 4

        lazyDat = LazyDataset(IterGenerator(samples_gen))
        lookbackDat = lazyDat.withLookback(lookback)
        batch_gen = lookbackDat.batch(batch_size)

        batch1=next(batch_gen)
        batch2=next(batch_gen)

        tmp1 = batch1.getFeaturesAs("array")
        temp1X = np.array(list(map(lambda x: np.stack(x), tmp1[:, :, 0])))
        temp1y = np.array(list(map(lambda x: np.stack(x), tmp1[:, :, 1])))
        tmp1lab = batch1.getLabelsAs("array")

        res = [np.array_equal(temp1X, X1), np.array_equal(temp1y, y1), np.array_equal(tmp1lab, lab1)]

        tmp2 = batch2.getFeaturesAs("array")
        temp2X = np.array(list(map(lambda x: np.stack(x), tmp2[:, :, 0])))
        temp2y = np.array(list(map(lambda x: np.stack(x), tmp2[:, :, 1])))
        tmp2lab = batch2.getLabelsAs("array")

        res = res + [np.array_equal(temp2X, X2), np.array_equal(temp2y, y2), np.array_equal(tmp2lab, lab2)]
        
        self.assertTrue(all(res))

    @logTest
    def test_withLookback_ArrayFeatureSample(self):
        
        samples = [Sample(features=np.array([100, 101]), label=1),
                   Sample(features=np.array([102, 103]), label=2),
                   Sample(features=np.array([104, 105]), label=3),
                   Sample(features=np.array([106, 107]), label=4),
                   Sample(features=np.array([108, 109]), label=5),
                   Sample(features=np.array([110, 111]), label=6),
                   Sample(features=np.array([112, 113]), label=7),
                   Sample(features=np.array([114, 115]), label=8),
                   Sample(features=np.array([116, 117]), label=9)]
        
        def samples_gen():
            for sample in samples:
                if not any([np.isnan(x).any() for x in sample.features]):
                    yield sample

        X1 = np.array([[[100, 101],[102, 103],[104, 105]], [[102, 103],[104, 105],[106, 107]],
                       [[104, 105],[106, 107],[108, 109]], [[106, 107],[108, 109],[110, 111]]])
        lab1 = np.array([3, 4, 5, 6])
        X2 = np.array([[[108, 109],[110, 111],[112, 113]], [[110, 111], [112, 113],[114, 115]],
                       [[112, 113],[114, 115],[116, 117]]])
        lab2 = np.array([7, 8, 9])

        lookback = 3
        batch_size = 4

        lazyDat = LazyDataset(IterGenerator(samples_gen))
        lookbackDat = lazyDat.withLookback(lookback)
        batch_gen = lookbackDat.batch(batch_size)

        batch1 = next(batch_gen)
        batch2 = next(batch_gen)

        tmp1 = batch1.getFeaturesAs("array")
        tmp1lab = batch1.getLabelsAs("array")

        res = [np.array_equal(tmp1, X1), np.array_equal(tmp1lab, lab1)]

        tmp2 = batch2.getFeaturesAs("array")
        tmp2lab = batch2.getLabelsAs("array")

        res = res + [np.array_equal(tmp2, X2), np.array_equal(tmp2lab, lab2)]

        self.assertTrue(all(res))

    @logTest
    def test_withLookback_ListFeatureSample(self):

        samples = [Sample(features=[100, 101], label=1),
                   Sample(features=[102, 103], label=2),
                   Sample(features=[104, 105], label=3),
                   Sample(features=[106, 107], label=4),
                   Sample(features=[108, 109], label=5),
                   Sample(features=[110, 111], label=6),
                   Sample(features=[112, 113], label=7),
                   Sample(features=[114, 115], label=8),
                   Sample(features=[116, 117], label=9)]

        def samples_gen():
            for sample in samples:
                if not any([np.isnan(x).any() for x in sample.features]):
                    yield sample

        X1 = np.array([[[100, 101], [102, 103], [104, 105]], [[102, 103], [104, 105], [106, 107]],
                       [[104, 105], [106, 107], [108, 109]], [[106, 107], [108, 109], [110, 111]]])
        lab1 = np.array([3, 4, 5, 6])
        X2 = np.array([[[108, 109], [110, 111], [112, 113]], [[110, 111], [112, 113], [114, 115]],
                       [[112, 113], [114, 115], [116, 117]]])
        lab2 = np.array([7, 8, 9])

        lookback = 3
        batch_size = 4

        lazyDat = LazyDataset(IterGenerator(samples_gen))
        lookbackDat = lazyDat.withLookback(lookback)
        batch_gen = lookbackDat.batch(batch_size)

        batch1 = next(batch_gen)
        batch2 = next(batch_gen)

        tmp1 = batch1.getFeaturesAs("array")
        tmp1lab = batch1.getLabelsAs("array")

        res = [np.array_equal(tmp1, X1), np.array_equal(tmp1lab, lab1)]

        tmp2 = batch2.getFeaturesAs("array")
        tmp2lab = batch2.getLabelsAs("array")

        res = res + [np.array_equal(tmp2, X2), np.array_equal(tmp2lab, lab2)]

        self.assertTrue(all(res))


class PandasDatasetTests(TestCase):

    dataset = PandasDataset(features=pd.concat([pd.Series([1, np.nan, 2, 3], name="feat1"),
                                                pd.Series([1, 2, 3, 4], name="feat2")], axis=1))

    @logTest
    def test_dropna_none_labels(self):

        res = pd.concat([pd.Series([1, 2, 3], name="feat1"), pd.Series([1, 3, 4], name="feat2")], axis=1)

        self.assertTrue((self.dataset.dropna(subset=["feat1"]).features.reset_index(drop=True) == res).all().all())

    @logTest
    def test_from_sequence(self):
        features_1 = pd.DataFrame({'feat1': [1, 2, 3, 4], 'feat2': [100, 200, 300, 400]}, index=[1, 2, 3, 4])
        features_2 = pd.DataFrame({'feat1': [9, 11, 13, 14], 'feat2': [90, 110, 130, 140]}, index=[10, 11, 12, 13])
        features_3 = pd.DataFrame({'feat1': [90, 10, 10, 1400], 'feat2': [.9, .11, .13, .14]}, index=[15, 16, 17, 18])
        labels_1 = pd.DataFrame({'target': [1, 0, 1, 1]}, index=[1, 2, 3, 4])
        labels_2 = pd.DataFrame({'target': [1, 1, 1, 0]}, index=[10, 11, 12, 13])
        labels_3 = pd.DataFrame({'target': [0, 1, 1, 0]}, index=[15, 16, 17, 18])
        dataset_1 = PandasDataset(features_1, labels_1)
        dataset_2 = PandasDataset(features_2, labels_2)
        dataset_3 = PandasDataset(features_3, labels_3)
        dataset_merged = PandasDataset.from_sequence([dataset_1, dataset_2, dataset_3])
        self.assertEqual(pd.concat([features_1, features_2, features_3]), dataset_merged.features)
        self.assertEqual(pd.concat([labels_1, labels_2, labels_3]), dataset_merged.labels)

    @logTest
    def test_serialization(self):
        filename = os.path.join(TMP_FOLDER, "my_dataset.p")

        self.dataset.write(filename)

        newDataset: PandasDataset = PandasDataset.load(filename)

        self.assertTrue(isinstance(newDataset, PandasDataset))

        self.assertTrue((self.dataset.features.fillna("NaN") == newDataset.features.fillna("NaN")).all().all())


class PandasTimeIndexedDatasetTests(TestCase):

    dates = pd.date_range("2010-01-01", "2010-01-04")

    dateStr = [str(x) for x in dates]

    dataset = PandasTimeIndexedDataset(
        features=pd.concat([
            pd.Series([1, np.nan, 2, 3], index=dateStr, name="feat1"),
            pd.Series([1, 2, 3, 4], index=dateStr, name="feat2")
        ], axis=1))


    @logTest
    def test_time_index(self):

        #duck-typing check
        days = [x.day for x in self.dataset.features.index]

        self.assertTrue(set(days), set(range(4)))

    @logTest
    def test_serialization(self):
        filename = os.path.join(TMP_FOLDER, "my_dataset.p")

        self.dataset.write(filename)

        newDataset = type(self.dataset).load(filename)

        self.assertTrue(isinstance(newDataset, PandasTimeIndexedDataset))
        self.assertTrue((self.dataset.features.fillna("NaN") == newDataset.features.fillna("NaN")).all().all())



if __name__ == "__main__":
    unittest.main()
