from dataclasses import dataclass

from typing import Generic, Set, TypeVar

from .nonterminals import NonTerminalBase
from .productions import Productions


Terminal = TypeVar("Terminal")
Nonterminal = TypeVar("Nonterminal", bound=NonTerminalBase)


class InvalidStartSymbol(Exception):
    def __init__(self, symbol) -> None:
        msg = f"Symbol {symbol} can't be a start symbol because it is not in nonterminals set."
        super().__init__(msg)


class InvalidProduction(Exception):
    def __init__(self, production, violator):
        msg = f"Production {production} is incorrect due to contains symbol {violator} which is not in terminals and nonterminals sets."
        super().__init__(msg)


class Grammar(Generic[Terminal, Nonterminal]):
    terminals: Set[Terminal]
    nonterminals: Set[Nonterminal]
    start_symbol: Nonterminal
    productions: Productions[Terminal, Nonterminal]
