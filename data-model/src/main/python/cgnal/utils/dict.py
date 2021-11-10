import sys
if sys.version_info[0] < 3:
    from itertools import izip as zip
else:
    from functools import reduce

from itertools import islice, tee, groupby
from typing import Iterator, Iterable, List, Tuple, Dict, Any, Callable, Optional
from copy import deepcopy as copy
from collections import Mapping
from operator import add
from cgnal.typing import SupportsLessThan, T


def groupIterable(iterable: Iterable[T], batch_size: int = 10000) -> Iterator[List[T]]:
    iterable = iter(iterable)
    return iter(lambda: list(islice(iterable, batch_size)), [])


def pairwise(iterable: Iterable[T]) -> zip:
    """s -> (s0,s1), (s1,s2), (s2, s3), ..."""
    a, b = tee(iterable)
    next(b, None)
    return zip(a, b)


def union(*dicts: dict) -> dict:
    def __dict_merge(dct: dict, merge_dct: dict):
        """ Recursive dict merge. Inspired by :meth:``dict.update()``, instead of
        updating only top-level keys, dict_merge recurses down into dicts nested
        to an arbitrary depth, updating keys. The ``merge_dct`` is merged into
        ``dct``.
        :param dct: dict onto which the merge is executed
        :param merge_dct: dct merged into dct
        :return: None
        """
        merged = copy(dct)
        for k, v in merge_dct.items():
            if (k in dct and isinstance(dct[k], dict)
                    and isinstance(merge_dct[k], Mapping)):
                merged[k] = __dict_merge(dct[k], merge_dct[k])
            else:
                merged[k] = merge_dct[k]
        return merged

    return reduce(__dict_merge, dicts)


def flattenKeys(input_dict: Dict[str, T], sep: str = ".") -> Dict[str, T]:
    def _flatten_(key: str, value: T) -> List[Tuple[str, T]]:
        if isinstance(value, dict) and (len(value) > 0):
            return reduce(add, [_flatten_(sep.join([key, name]), item) for name, item in value.items()])
        else:
            return [(key, value)]
    return union(*[dict(_flatten_(key, value)) for key, value in input_dict.items()])


def unflattenKeys(input_dict: Dict[str, Any], sep: str = ".") -> Dict[str, Any]:
    def __translate(key: str, value: Any) -> Dict[str, Any]:
        levels = key.split(sep)
        out = value
        for level in reversed(levels):
            out = {level: out}
        return out
    return union(*[__translate(key, value) for key, value in input_dict.items()])


def __check(value: Optional[T]) -> bool:
    return False if value is None else True


def filterNones(_dict: Dict[T, Any]) -> Dict[T, Any]:
    agg = {}
    for k, v in _dict.items():
        if isinstance(v, dict):
            agg[k] = filterNones(v)
        elif __check(v):
            agg[k] = v
    return agg


def groupBy(lst: Iterable[T], key: Callable[[T], SupportsLessThan]) -> Iterator[Tuple[SupportsLessThan, List[T]]]:
    for k, it in groupby(sorted(lst, key=key), key=key):
        yield k, list(it)
