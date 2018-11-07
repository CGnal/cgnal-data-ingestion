import numpy as np
import unittest
from cgnal.data.model.ml import LazyDataset, IterGenerator, MultiFeatureSample, Sample


class LazyDatasetTests(unittest.TestCase):

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


if __name__ == "__main__":
    unittest.main()
