import os
from typing import Union, Any, TypeVar, Hashable
from typing_extensions import Protocol

PathLike = Union[str, 'os.PathLike[str]']
T = TypeVar('T')
T_co = TypeVar('T_co', covariant=True)


class SupportsLessThan(Protocol):
    def __lt__(self, __other: Any) -> bool: ...
