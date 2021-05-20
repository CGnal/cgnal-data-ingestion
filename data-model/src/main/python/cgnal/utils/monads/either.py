from pymonad.either import Either as CoreEither, M, T, Any


class Either(CoreEither):
    """
    Enhanced Either with extra functionalities
    """

    def getOrElse(self, default):
        if self.is_right():
            return self.value
        else:
            return default

    def leftMap(self, f):
        if self.is_left():
            return Left(f(self.value))
        else:
            return self

    def rightMap(self, f):
        if self.is_right():
            return Right(f(self.value))
        else:
            return self

    def __iter__(self):
        if self.is_right():
            yield self.value


def Left(value: M) -> 'Either[M, Any]':
    """ Creates a value of the first possible type in the Either monad. """
    return Either(None, (value, False))


def Right(value: T) -> 'Either[Any, T]':
    """ Creates a value of the second possible type in the Either monad. """
    return Either(value, (None, True))


def raiseException(x: Exception):
    """
    Function to be used when composing monads
    :param x: Exception
    :return: None, this function will be raising expection
    """
    raise x
