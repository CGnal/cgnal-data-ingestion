import os
from typing import Union, Any
from typing_extensions import Protocol
from cgnal._version import __version__

PathLike = Union[str, 'os.PathLike[str]']


class SupportsLessThan(Protocol):
    def __lt__(self, __other: Any) -> bool: ...
