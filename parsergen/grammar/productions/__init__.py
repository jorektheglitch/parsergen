from dataclasses import dataclass

from typing import Generic, Iterable, Iterator, List, Reversible, Tuple, TypeVar, Union

from parsergen.grammar.nonterminals import NonTerminalBase


Terminal = TypeVar("Terminal")
Nonterminal = TypeVar("Nonterminal", bound=NonTerminalBase)


class Rule(Reversible[Union[Terminal, Nonterminal]], Generic[Terminal, Nonterminal]):

    symbols: Tuple[Union[Terminal, Nonterminal], ...]

    def __init__(self, symbols: Iterable[Union[Terminal, Nonterminal]]):
        self.symbols = tuple(symbols)

    def __getitem__(self, index):
        return self.symbols[index]

    def __iter__(self):
        return iter(self.symbols)
    
    def __len__(self):
        return len(self.symbols)

    def __reversed__(self) -> Iterator[Union[Terminal, Nonterminal]]:
        return reversed(self.symbols)

    def __str__(self) -> str:
        items = (
            repr(item) if isinstance(item, str) else str(item)
            for item in self.symbols
        )
        return " ".join(items)

    def __repr__(self) -> str:
        cls = type(self)
        return f"{cls.__name__}({self})"


@dataclass
class Production(Generic[Terminal, Nonterminal]):

    left: Nonterminal
    right: Rule[Terminal, Nonterminal]

    def __str__(self) -> str:
        return f"{self.left} -> {self.right}"

    def __repr__(self) -> str:
        cls = type(self)
        return f"{cls.__name__}({self})"

    @property
    def rule(self) -> Rule[Terminal, Nonterminal]:
        return self.right


class Productions(Generic[Terminal, Nonterminal], List[Production[Terminal, Nonterminal]]):

    def append(self, item: Production[Terminal, Nonterminal]) -> None:
        if item not in self:
            return super().append(item)
        return None

    def lhs_filter(self, nt: Nonterminal):
        for production in self:
            if production.left == nt:
                yield production
    
    def rhs_filter(self, symbol: Union[Terminal, Nonterminal]):
        for production in self:
            if symbol in production.right:
                yield production
