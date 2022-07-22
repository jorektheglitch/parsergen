from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Generic, TypeVar
from typing import Any, Iterable, List, Mapping, NewType, Tuple, Union

from parsergen.grammar import Grammar
from parsergen.grammar.nonterminals import NonTerminalBase, epsilon, eof
from parsergen.grammar.productions import Production


StateNo = NewType("StateNo", int)
Terminal = TypeVar("Terminal")
Nonterminal = TypeVar("Nonterminal", bound=NonTerminalBase)
T = TypeVar("T")
NT = TypeVar("NT", bound=NonTerminalBase)


class ParsingError(Exception):
    pass


class Action(ABC):
    pass


@dataclass
class Shift(Action):

    state: StateNo

    def __repr__(self):
        cls = type(self)
        return f"{cls.__name__}({self.state})"


@dataclass
class Reduce(Action):

    production: Production

    def __repr__(self):
        cls = type(self)
        production = self.production
        return f"{cls.__name__}({production!r})"


@dataclass
class Result(Action, Generic[Nonterminal]):

    value: Union[Nonterminal, ParsingError]

    def __str__(self):
        if isinstance(self.value, ParsingError):
            return "Error"
        return "Accept"


class LRParser(ABC, Generic[Terminal, Nonterminal]):

    actions_table: Mapping[StateNo, Mapping[Terminal, Any]]
    goto_table: Mapping[StateNo, Mapping[Nonterminal, Any]]

    stack: List[Tuple[StateNo, Union[Terminal, Nonterminal, Tuple[Nonterminal, Tuple[Union[Terminal, Nonterminal], ...]]]]]
    state: StateNo

    def __init__(
        self,
        actions: Mapping[StateNo, Mapping[Terminal, Any]],
        gotos: Mapping[StateNo, Mapping[Nonterminal, Any]],
        stack: Iterable[Tuple[StateNo, Union[Terminal, Nonterminal]]] = (),
        state: StateNo = StateNo(0)
    ):
        self.actions_table = actions
        self.goto_table = gotos
        self.stack = [*stack]
        self.state = state

    @abstractmethod
    @classmethod
    def get_tables(
        cls, grammar: Grammar[T, NT]
    ) -> Tuple[Mapping[StateNo, Mapping[T, Any]], Mapping[StateNo, Mapping[NT, Any]]]:
        pass

    @abstractmethod
    def parse(self, incoming: Iterable[Terminal]):
        pass

    @abstractmethod
    def finalize(self):
        pass


class LR0Parser(LRParser[Terminal, Nonterminal], Generic[Terminal, Nonterminal]):

    actions_table: Mapping[StateNo, Mapping[Terminal, Union[Shift, Reduce]]]
    goto_table: Mapping[StateNo, Mapping[Nonterminal, StateNo]]

    @classmethod
    def get_tables(cls, grammar: Grammar):  # TODO
        pass

    def parse(self, stream: Iterable[Terminal]) -> None:
        stream = iter(stream)
        for symbol in stream:
            accept_incoming = False
            while not accept_incoming:
                accept_incoming = self._parsing_step(symbol)

    def _parsing_step(self, incoming: Terminal):
        accept_incoming = False
        stack = self.stack
        state = self.state
        print(f"Symbol {repr(incoming)}, state {state}")
        action = self.actions_table.get(state, {}).get(incoming)
        if action is None:
            raise ParsingError(f"Unrecognizable terminal {repr(incoming)} on state {state}")  # noqa
        print(f"Action: {action}")
        if isinstance(action, Shift):
            stack.append((state, incoming))
            print("Stack", stack)
            self.state = action.state
            accept_incoming = True
        elif isinstance(action, Reduce):
            nt, rule = action.production.left, action.production.right
            buff = []
            for _ in rule:
                state, symbol = stack.pop()
                buff.append(symbol)
            new = nt, tuple(reversed(buff))  # noqa
            stack.append((state, nt))
            print(self.state, "->", state)
            self.state = self.goto_table[state][nt]
            print(state, "->", self.state)
            print("Stack:", stack)
        return accept_incoming

    def finalize(self):
        self.parse((eof, ))


class LR1Parser(LRParser):
    pass
