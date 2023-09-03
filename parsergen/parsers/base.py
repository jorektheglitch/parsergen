from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Generic, Iterable, List, Mapping, Tuple, TypeVar, Union
from parsergen.grammar import Grammar

from parsergen.grammar.nonterminals import NonTerminalBase, SpecialNonterminal, epsilon, eof
from parsergen.grammar.productions import Production, Rule


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


class LL1Parser(Parser, Generic[Terminal, Nonterminal]):

    parse_table: Mapping[Nonterminal, Mapping[Terminal, Production[Terminal, Nonterminal]]]

    def __init__(self, grammar: Grammar[Terminal, Nonterminal]) -> None:
        super().__init__()
        self.grammar = grammar
        self.parse_table = self._get_parse_table(grammar)

    def parse(self, incoming: Iterable[Terminal]) -> Nonterminal:
        runtime = self.iterative_parse()
        for symbol in incoming:
            runtime.push(symbol)
        runtime.finalize()
        return runtime.result

    def iterative_parse(self) -> LL1Runtime[Terminal, Nonterminal]:
        return LL1Runtime(self.parse_table, self.grammar.start_symbol)

    def _get_parse_table(
        self,
        grammar: Grammar[Terminal, Nonterminal]
    ) -> Mapping[Nonterminal, Mapping[Terminal, Production[Terminal, Nonterminal]]]:
        pass


class LL1Runtime(ParserRuntime[Terminal, Nonterminal], Generic[Terminal, Nonterminal]):

    parse_table: Mapping[Nonterminal, Mapping[Terminal, Production[Terminal, Nonterminal]]]
    parse_stack: List[Union[Terminal, Nonterminal, SpecialNonterminal]]
    recognize_stack: List[Tuple[Nonterminal, int, List[Union[Terminal, Nonterminal, None]]]]

    def __init__(
        self,
        parse_table: Mapping[Nonterminal, Mapping[Terminal, Production[Terminal, Nonterminal]]],
        start_symbol: Nonterminal
    ) -> None:
        super().__init__()
        self.parse_table = parse_table
        self.parse_stack = [eof, start_symbol]
        self.recognize_stack = []

    @property
    def result(self) -> Nonterminal:
        result = getattr(self, "_result", None)
        if not result:
            raise RuntimeError
        return result

    def push(self, terminal: Terminal):
        stack = self.parse_stack
        stack_top = stack.pop()
        while isinstance(stack_top, NonTerminalBase):
            if stack_top is epsilon:
                print("Eject", epsilon, "from stack")
                print("Stack:", repr(stack))
                self.recognize_stack[-1][2].append(None)
            else:
                production = self.parse_table[stack_top][terminal]
                stack.extend(reversed(production.rule))
                self.recognize_stack.append((production.left, len(production.rule), []))
            if len(self.recognize_stack[-1][2]) == self.recognize_stack[-1][1]:
                NonterminalType, _, args = self.recognize_stack.pop()
                nonterminal = NonterminalType(*args)
                self.recognize_stack[-1][2].append(nonterminal)
            stack_top = stack.pop()
        if stack_top != terminal:
            raise ParsingError
        self.recognize_stack[-1][2].append(stack_top)

    def finalize(self):
        stack = self.parse_stack
        stack_top = stack.pop()
        while isinstance(stack_top, NonTerminalBase):
            if stack_top is epsilon:
                print("Eject", epsilon, "from stack")
                print("Stack:", repr(stack))
                self.recognize_stack[-1][2].append(None)
            else:
                production = self.parse_table[stack_top][eof]
                stack.extend(reversed(production.rule))
                self.recognize_stack.append((production.left, len(production.rule), []))
            if len(self.recognize_stack[-1][2]) == self.recognize_stack[-1][1]:
                NonterminalType, _, args = self.recognize_stack.pop()
                nonterminal = NonterminalType(*args)
                self.recognize_stack[-1][2].append(nonterminal)
            stack_top = stack.pop()
        if stack_top != eof:
            raise ParsingError
        self.recognize_stack[-1][2].append(stack_top)
