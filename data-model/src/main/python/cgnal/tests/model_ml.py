import numpy as np
from itertools import islice
from cgnal.data.model.ml import LazyDataset, IterGenerator, MultiFeatureSample, Sample


samples = [MultiFeatureSample(features=[np.array([100, 101]), np.array([np.NaN])], label=1),
           MultiFeatureSample(features=[np.array([102, 103]), np.array([1])], label=2),
           MultiFeatureSample(features=[np.array([104, 105]), np.array([2])], label=3),
           MultiFeatureSample(features=[np.array([106, 107]), np.array([3])], label=4),
           MultiFeatureSample(features=[np.array([108, 109]), np.array([4])], label=5),
           MultiFeatureSample(features=[np.array([110, 111]), np.array([5])], label=6),
           MultiFeatureSample(features=[np.array([112, 113]), np.array([6])], label=7),
           MultiFeatureSample(features=[np.array([114, 115]), np.array([7])], label=8),
           MultiFeatureSample(features=[np.array([116, 117]), np.array([8])], label=9)]


# samples = [Sample(features=np.array([100, 101]), label=1),
#            Sample(features=np.array([102, 103]), label=2),
#            Sample(features=np.array([104, 105]), label=3),
#            Sample(features=np.array([106, 107]), label=4),
#            Sample(features=np.array([108, 109]), label=5),
#            Sample(features=np.array([110, 111]), label=6),
#            Sample(features=np.array([112, 113]), label=7),
#            Sample(features=np.array([114, 115]), label=8),
#            Sample(features=np.array([116, 117]), label=9)]
#
#
# samples = [Sample(features=[100, 101], label=1),
#            Sample(features=[102, 103], label=2),
#            Sample(features=[104, 105], label=3),
#            Sample(features=[106, 107], label=4),
#            Sample(features=[108, 109], label=5),
#            Sample(features=[110, 111], label=6),
#            Sample(features=[112, 113], label=7),
#            Sample(features=[114, 115], label=8),
#            Sample(features=[116, 117], label=9)]


def samples_gen():
    for sample in samples:
        if not any([np.isnan(x).any() for x in sample.features]):
            yield sample


lookback = 3
batch_size = 4


lazyDat = LazyDataset(IterGenerator(samples_gen))
lookbackDat = lazyDat.withLookback(lookback)
batch_gen = lookbackDat.batch(batch_size)

tmp1=next(batch_gen)
print(tmp1.getFeaturesAs("array"))
print(tmp1.getLabelsAs("array"))
tmp2=next(batch_gen)
print(tmp2.getFeaturesAs("array"))
print(tmp2.getLabelsAs("array"))
tmp3=next(batch_gen)
tmp4=next(batch_gen)
tmp5=next(batch_gen)
tmp6=next(batch_gen)
