import sys

from typing import Any, Dict, Optional, Tuple, Type, overload

if sys.version_info >= (3, 11):
    from typing import Self
else:
    from typing_extensions import Self

from .declarative import NonTerminalMeta


_Bases = Tuple[Type, ...]
_Attrs = Dict[str, Any]


class NonTerminalBase(NonTerminalMeta):

    _name: str
    args: Tuple

    @overload
    def __new__(mcls: Type[Self], name: str, bases: Tuple[Type, ...], attrs: Dict[str, Any]) -> Self: ...
    @overload
    def __new__(mcls: Type[Self], name: str) -> Self: ...
    def __new__(mcls, name: str, bases: Optional[_Bases] = None, attrs: Optional[_Attrs] = None):
        bases = bases or ()
        attrs = attrs or {}
        return super().__new__(mcls, name, bases, attrs)

    @overload
    def __init__(self, name: str, bases: Tuple[Type, ...], attrs: Dict[str, Any]): ...
    @overload
    def __init__(self, name: str): ...
    def __init__(self, name: str, bases: Optional[_Bases] = None, attrs: Optional[_Attrs] = None) -> None:
        bases = bases or ()
        attrs = attrs or {}
        super().__init__(name, bases, attrs)
        self._name = name

    def __call__(cls, *args):
        obj = super().__call__()
        obj.args = args
        return obj

    def __hash__(self) -> int:
        return hash(self._name)

    def __str__(self) -> str:
        return self._name

    def __repr__(self) -> str:
        cls = type(self)
        return f"{cls.__name__}({self})"


class SpecialNonterminal(NonTerminalBase):

    def __eq__(self, other: object) -> bool:
        if isinstance(other, SpecialNonterminal):
            return self is other
        return NotImplemented


class Nonterminal(NonTerminalBase):

    def __eq__(self, other: object) -> bool:
        if isinstance(other, Nonterminal):
            return (self._name == other._name)
        return NotImplemented


start = SpecialNonterminal("S")
epsilon = SpecialNonterminal("ε")
eof = SpecialNonterminal("EOF")
