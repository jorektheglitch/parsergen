from __future__ import annotations

from typing import Any, Dict, Optional, Tuple, Type
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from parsergen.grammar.productions import Productions

from .declarative import NonTerminalMeta


_Bases = Tuple[Type, ...]
_Attrs = Dict[str, Any]


class NonTerminalBase(NonTerminalMeta):

    _name: str
    args: Tuple

    def __new__(mcls, name: str, bases: Optional[_Bases] = None, attrs: Optional[_Attrs] = None):
        bases = bases or ()
        attrs = attrs or {}
        return super().__new__(mcls, name, bases, attrs)

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


def is_epsilon_generating(nt: NonTerminalBase, productions: Productions) -> bool:
    raise NotImplementedError
