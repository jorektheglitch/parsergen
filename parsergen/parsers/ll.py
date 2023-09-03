from abc import ABC

from typing import ClassVar, Generic, Iterable, List, Mapping, MutableMapping, Tuple, TypeVar, Union

from parsergen.grammar import Grammar
from parsergen.grammar.nonterminals import NonTerminalBase, epsilon, is_epsilon_generating

from .base import Parser, ParsingError
from .utils import SymbolQueue, firsts


Terminal = TypeVar("Terminal")
Nonterminal = TypeVar("Nonterminal", bound=NonTerminalBase)


class IncompatibleGrammar(Exception):
    pass


class LeftRecursionFound(IncompatibleGrammar):
    pass


class LLParser(Parser[Terminal, Nonterminal], ABC, Generic[Terminal, Nonterminal]):

    parse_table: Mapping[Nonterminal, Mapping]
    stack: List[Union[Terminal, Nonterminal]]

    def __init__(self) -> None:
        super().__init__()

    def parse(self, incoming: Iterable[Terminal]):
        for symbol in incoming:
            pass


class LLkParser(LLParser[Terminal, Nonterminal], ABC, Generic[Terminal, Nonterminal]):

    k: ClassVar[int]
    parse_table: Mapping[Nonterminal, Mapping[Tuple[Terminal, ...], Tuple[Union[Terminal, Nonterminal], ...]]]


class LL1Parser(LLParser[Terminal, Nonterminal], Generic[Terminal, Nonterminal]):

    parse_table: Mapping[Nonterminal, Mapping[Terminal, Tuple[Union[Terminal, Nonterminal], ...]]]

    def parse(self, incoming: Iterable[Terminal]):
        stack = self.stack
        for terminal in incoming:
            stack_top = stack[0] if stack else None
            while isinstance(stack_top, NonTerminalBase):
                if stack_top is epsilon:
                    print("Eject", epsilon, "from stack")
                    stack.pop()
                    print("Stack:", repr(stack))
                    continue
                rule = self.parse_table[stack_top][terminal]
                stack.pop()
                self.stack.extend(reversed(rule))
            stack_top = stack[0] if stack else None
            if stack_top == terminal:
                stack.pop()
            else:
                raise ParsingError
    
    def finalize(self):
        stack = self.stack
        stack_top = stack[0] if stack else None
        while isinstance(stack_top, NonTerminalBase):
            if stack_top is epsilon:
                print("Eject", epsilon, "from stack")
                stack.pop()
                print("Stack:", repr(stack))
                continue
            rule = self.parse_table[stack_top][terminal]
            stack.pop()
            self.stack.extend(reversed(rule))
        stack_top = stack[0] if stack else None
        if stack_top == terminal:
            stack.pop()
        else:
            raise ParsingError


def LLk_parse_table(grammar: Grammar, *, k: int = 1):
    if k <= 0:
        raise ValueError(f"k must be positive non-zero integer, but {k} given.")
    if k > 1:
        raise NotImplementedError("LL(k) parse table building not implemented for k>1.")
    else:
        return LL1_parse_table(grammar)


def LL1_parse_table(grammar: Grammar[Terminal, Nonterminal]):
    if grammar.has_left_recursion:
        raise LeftRecursionFound
    parse_table: Mapping[Nonterminal, MutableMapping[Terminal, Tuple[Union[Terminal, Nonterminal], ...]]] = {
        nt: {} for nt in grammar.nonterminals
    }
    queue = SymbolQueue[Nonterminal]()
    queue.put(grammar.start_symbol)
    for nt in queue:
        for production in grammar.productions.lhs_filter(nt):
            for symbol in production.right:
                if isinstance(symbol, NonTerminalBase):
                    queue.put(symbol)
            directing_terminals: List[Terminal] = []
            for symbol in production.right:
                if not isinstance(symbol, NonTerminalBase):
                    directing_terminals.append(symbol)
                    break
                else:
                    directing_terminals.extend(firsts(symbol, grammar))
                    if is_epsilon_generating(symbol, grammar.productions):
                        pass
                    else:
                        break
            directing_terminals = [
                terminal for i, terminal in enumerate(directing_terminals)
                if i == directing_terminals.index(terminal)
            ]
            for terminal in directing_terminals:
                if parse_table.get(nt, {}).get(terminal) is not None:
                    raise IncompatibleGrammar
                stack_items = tuple(production.right)
                parse_table[nt][terminal] = stack_items
    return parse_table
