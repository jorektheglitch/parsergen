from queue import Queue

from typing import Generic, List, Optional, Sequence, Set, TypeVar, Union

from parsergen.grammar import Grammar
from parsergen.grammar.nonterminals import NonTerminalBase, eof, is_epsilon_generating


T = TypeVar("T")
Terminal = TypeVar("Terminal")
Nonterminal = TypeVar("Nonterminal", bound=NonTerminalBase)


class SymbolQueue(Queue, Generic[T]):
    # this queue is not thread-safe!

    queue: Sequence[T]
    visited: Set[T]

    def __init__(self, maxsize: int = 0) -> None:
        self.visited = set()
        super().__init__(maxsize)

    def put(self, item: T, block: bool = True, timeout: Optional[float] = None) -> None:
        if item not in self.visited:
            return super().put(item, block, timeout)

    def put_nowait(self, item: T) -> None:
        if item not in self.visited:
            return super().put_nowait(item)

    def get(self, block: bool = True, timeout: Optional[float] = None) -> T:
        return super().get(block, timeout)

    def __iter__(self):
        while not self.empty():
            yield self.get()


def firsts(nt: Nonterminal, grammar: Grammar[Terminal, Nonterminal]) -> List[Terminal]:
    firsts_list: List[Terminal] = []
    productions = grammar.productions
    queue = SymbolQueue[Union[Terminal, Nonterminal]]()
    queue.put(nt)
    for symbol in queue:
        # if terminal symbol
        if not isinstance(symbol, NonTerminalBase):
            firsts_list.append(symbol)
            continue
        # if nonterminal symbol
        for production in productions.lhs_filter(symbol):
            # for each production where symbol in left half statement
            for starter in production.rule:
                queue.put(starter)
                if not isinstance(starter, NonTerminalBase):
                    break
                if not is_epsilon_generating(starter, productions):
                    break
    return firsts_list


def follows(nt: Nonterminal, grammar: Grammar[Terminal, Nonterminal]) -> List[Terminal]:
    follows_list: List[Terminal] = []
    productions = grammar.productions
    queue = SymbolQueue[Union[Terminal, Nonterminal]]()
    queue.put(nt)
    for symbol in queue:
        # if terminal symbol
        if not isinstance(symbol, NonTerminalBase):
            follows_list.append(symbol)
            continue
        # if nonterminal symbol
        for production in productions.rhs_filter(symbol):
            # for each production where symbol in right half statement
            symbol_found = False
            followers = []
            for s in production.right:
                if isinstance(s, NonTerminalBase) and s == symbol:
                    symbol_found = True
                elif symbol_found:
                    followers.append(s)
                    symbol_found = False
                    if isinstance(s, NonTerminalBase):
                        if is_epsilon_generating(s, productions):
                            symbol_found = True
            if symbol_found:
                queue.put(production.left)
            followers = [
                follower for i, follower in enumerate(followers)
                if i == followers.index(follower)
            ]
            for follower in followers:
                if not isinstance(follower, NonTerminalBase):
                    queue.put(follower)
                else:
                    if follower == eof:
                        continue
                    for first in firsts(follower, grammar):
                        queue.put(first)
    return follows_list
