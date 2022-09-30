from abc import ABC, abstractmethod
from typing import Generic, Iterable, TypeVar

from parsergen.grammar.nonterminals import NonTerminalBase


Terminal = TypeVar("Terminal")
Nonterminal = TypeVar("Nonterminal", bound=NonTerminalBase)


class ParsingError(Exception):
    pass


class Parser(ABC, Generic[Terminal, Nonterminal]):

    @abstractmethod
    def parse(self, incoming: Iterable[Terminal]):
        pass

    @abstractmethod
    def finalize(self):
        pass
