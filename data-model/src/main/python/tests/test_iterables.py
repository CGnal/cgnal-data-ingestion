import unittest

from cgnal.data.model.core import CachedIterable, LazyIterable, IterGenerator, BaseIterable
from cgnal.data.model.text import Document, CachedDocuments, LazyDocuments
from cgnal.logging.defaults import getDefaultLogger
from cgnal.tests.core import logTest, TestCase

logger = getDefaultLogger()

n = 10


def generator():
    for i in range(n):
        yield i


class TestIterables(TestCase):
    cached = CachedIterable([i for i in range(n)])

    lazy = LazyIterable(IterGenerator(generator))

    @logTest
    def test_map(self):

        plusOne = self.cached.map(lambda x: x + 1)

        self.assertTrue(isinstance(plusOne, BaseIterable))

        self.assertEqual(len(plusOne.asCached), n)

    @logTest
    def test_filter(self):

        half = self.cached.map(lambda x: x + 1).filter(lambda x: x % 2 == 0)

        self.assertEqual(len(half.asCached), n / 2)

    @logTest
    def test_batch(self):

        batch_size = 2

        batches = self.cached.map(lambda x: x + 1).batch(batch_size)

        for batch in batches:
            self.assertTrue(isinstance(batch, CachedIterable))

    @staticmethod
    def functionWithSideEffect(lst):
        def function(x):
            lst.append(1)
            return x

        return function

    @logTest
    def test_laziness(self):

        batch_size = 2
        lst = []

        batches = self.cached.map(TestIterables.functionWithSideEffect(lst)).batch(batch_size)

        cnt2 = 0
        for batch in batches:
            cnt2 += len(batch)
            self.assertEqual(len(lst), cnt2)

    @logTest
    def test_sudden_computation(self):

        batch_size = 2
        lst = []

        batches = self.cached.map(TestIterables.functionWithSideEffect(lst)).asCached.batch(batch_size)

        for _ in batches:
            self.assertEqual(len(lst), n)

    @logTest
    def test_conversion_to_lazy(self):
        lazy = self.cached.asLazy
        self.assertTrue(isinstance(lazy, LazyIterable))
        self.assertEqual([i for i in lazy], [i for i in self.cached])

    @logTest
    def test_conversion_to_cached(self):
        cached = self.lazy.asCached
        self.assertTrue(isinstance(cached, CachedIterable))
        self.assertEqual([i for i in cached], [i for i in self.lazy])


def createCorpus(n):
    for i in range(n):
        yield Document(str(i), {"text": "my text 1"})


class TestDocuments(TestCase):
    docs = CachedDocuments(createCorpus(n)) \
        .map(lambda x: x.addProperty("tags", {"1": "1"})) \
        .map(lambda x: x.addProperty("tags", {"2": "2"}))

    @logTest
    def test_documents_parsing(self):
        filteredDocs = self.docs.filter(lambda x: int(x.uuid) % 2)
        self.assertTrue(isinstance(filteredDocs, LazyDocuments))
        self.assertEqual(len(filteredDocs.asCached), n / 2)

    @logTest
    def test_documents_cached(self):
        filteredDocs = self.docs.filter(lambda x: int(x.uuid) % 2).asCached
        self.assertTrue(isinstance(filteredDocs, CachedDocuments))


if __name__ == "__main__":
    unittest.main()
