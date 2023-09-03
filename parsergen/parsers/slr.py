from typing import Generic, TypeVar

from parsergen.grammar.nonterminals import NonTerminalBase
from .lr import LR0Parser


Terminal = TypeVar("Terminal")
Nonterminal = TypeVar("Nonterminal", bound=NonTerminalBase)


class SLR1Parser(LR0Parser[Terminal, Nonterminal], Generic[Terminal, Nonterminal]):
    pass
