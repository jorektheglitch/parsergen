from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Generic, Iterable, TypeVar

from parsergen.grammar.nonterminals import NonTerminalBase


Terminal = TypeVar("Terminal")
Nonterminal = TypeVar("Nonterminal", bound=NonTerminalBase)


class ParsingError(Exception):
    pass


class Parser(ABC, Generic[Terminal, Nonterminal]):

    @abstractmethod
    def parse(self, incoming: Iterable[Terminal]) -> Nonterminal:
        pass

    def iterative_parse(self) -> ParserRuntime:
        pass


class ParserRuntime(ABC, Generic[Terminal, Nonterminal]):

    @property
    @abstractmethod
    def result(self) -> Nonterminal:
        pass

    @abstractmethod
    def push(self, symbol: Terminal) -> None:
        pass

    @abstractmethod
    def finalize(self):
        pass
