from dataclasses import dataclass

from typing import Generic, Set, TypeVar

from .nonterminals import NonTerminalBase
from .productions import Productions


Terminal = TypeVar("Terminal")
Nonterminal = TypeVar("Nonterminal", bound=NonTerminalBase)


@dataclass
class Grammar(Generic[Terminal, Nonterminal]):
    terminals: Set[Terminal]
    nonterminals: Set[Nonterminal]
    start_symbol: Nonterminal
    productions: Productions[Terminal, Nonterminal]
