import asyncio
import unittest

from pymonad.promise import Promise
from pymonad.tools import curry

from cgnal.logging.defaults import getDefaultLogger
from cgnal.tests.core import logTest, TestCase
from cgnal.utils.dict import nestedGet
from cgnal.utils.monads import safe, async_func
from cgnal.utils.monads.either import Right, Left


class EitherTest(TestCase):

    def setUp(self):
        pass

    @logTest
    def test_getOrElse(self):
        self.assertEqual(Right(1).getOrElse(0), 1)
        self.assertEqual(Left(1).getOrElse(0), 0)

    @logTest
    def test_nestedGet(self):
        json = {"key1": {"key2": {"key3": 1}}}

        self.assertEqual(nestedGet(json, "key1.key2.key3"), Right(1))
        self.assertTrue(nestedGet(json, "key1.key2.key4").is_left())

    @logTest
    def test_map(self):
        @curry(2)
        @safe
        def unsafe_alert(thres: int, x: int) -> int:
            if x > thres:
                raise ValueError("Too High")
            return x

        self.assertTrue(Right(2).bind(unsafe_alert(3)).is_right())

        self.assertTrue(Right(2).bind(unsafe_alert(1)).is_left())

        self.assertTrue(Right(2).rightMap(lambda x: x + 1), Right(3))

        self.assertTrue(Right(2).leftMap(lambda x: x + 1), Right(2))

        self.assertTrue(Right(2).bind(unsafe_alert(1)).leftMap(lambda x: 2), Left(2))


class PromiseTest(TestCase):

    @staticmethod
    async def fakeComputation(x: int):
        await asyncio.sleep((1 + x / 3) * 0.1)
        return x

    def setUp(self):
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(None)

    @logTest
    def test_promise_combination_args(self):
        @async_func
        def add(*args):
            return sum(args)

        async def main():
            x = Promise.insert(1).map(PromiseTest.fakeComputation)

            y = Promise.insert(2).map(PromiseTest.fakeComputation)

            z = Promise.insert(3).map(PromiseTest.fakeComputation)

            promiseSum = await add(x, y, z)

            self.assertEqual(promiseSum, 6)

        self.loop.run_until_complete(main())

    @logTest
    def test_promise_combination_kwargs(self):
        @async_func
        def my_func(x: int, y: int = 1, z: int = 1):
            return (x + 2 * y) / z

        async def main():
            x = Promise.insert(1).map(PromiseTest.fakeComputation)

            y = Promise.insert(2).map(PromiseTest.fakeComputation)

            z = 1

            promiseFunc = await my_func(x, y, z=z).map(PromiseTest.fakeComputation)

            self.assertEqual(promiseFunc, (1 + 4) / 1)

        self.loop.run_until_complete(main())


if __name__ == "__main__":
    _ = getDefaultLogger("DEBUG")
    unittest.main()
