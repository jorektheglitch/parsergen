from abc import ABC


class NonTerminalBase(ABC):

    _name: str

    def __init__(self, name: str) -> None:
        self._name = name

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
