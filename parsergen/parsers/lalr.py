from typing import Generic, TypeVar

from parsergen.grammar.nonterminals import NonTerminalBase
from .slr import SLR1Parser


Terminal = TypeVar("Terminal")
Nonterminal = TypeVar("Nonterminal", bound=NonTerminalBase)


class LALR1Parser(
    SLR1Parser[Terminal, Nonterminal], Generic[Terminal, Nonterminal]
):
    pass
