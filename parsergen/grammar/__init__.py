from abc import abstractmethod
from types import MappingProxyType
from typing import Collection, FrozenSet, Generic, Iterable, Protocol, Tuple, TypeVar, Union, overload

from .algorythms import get_firsts_follows
from .nonterminals import NonTerminalBase, SpecialNonterminal, is_epsilon_generating
from .productions import Production, Productions


T = TypeVar("T")
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


class TerminalsSet(
    # TODO: fix mypy warning:
    #       Invariant type variable "Terminal" used in protocol where covariant
    #       one is expected
    Collection[Union[Terminal, SpecialNonterminal]],
    Iterable[Union[Terminal, SpecialNonterminal]],
    Protocol[Terminal]
):
    pass


class TerminalSets(
    Protocol[Terminal, Nonterminal]
):
    # It is actually a copy-paste from typing.Mapping class
    # MUST be same as Mapping[Nonterminal, FirstsSet[Terminal]]
    @abstractmethod
    def __getitem__(self, __key: Nonterminal) -> TerminalsSet[Terminal]: ...
    @overload
    def get(self, __key: Nonterminal) -> Union[TerminalsSet[Terminal], None]: ...
    @overload
    def get(self, __key: Nonterminal, default: Union[TerminalsSet[Terminal], T]) -> Union[TerminalsSet[Terminal], T]: ...
    def items(self) -> Iterable[Tuple[Nonterminal, TerminalsSet[Terminal]]]: ...
    def keys(self) -> Iterable[Nonterminal]: ...
    def values(self) -> Iterable[TerminalsSet[Terminal]]: ...
    def __contains__(self, __o: object) -> bool: ...


class Grammar(Generic[Terminal, Nonterminal]):

    terminals: FrozenSet[Terminal]
    nonterminals: FrozenSet[Nonterminal]
    start_symbol: Nonterminal
    productions: Productions[Terminal, Nonterminal]
    firsts: TerminalSets[Terminal, Nonterminal]
    follows: TerminalSets[Terminal, Nonterminal]

    def __init__(
        self,
        terminals: Iterable[Terminal],
        nonterminals: Iterable[Nonterminal],
        start_symbol: Nonterminal,
        productions: Iterable[Production[Terminal, Nonterminal]]
    ) -> None:
        super().__init__()
        self.terminals = frozenset(terminals)
        self.nonterminals = frozenset(nonterminals)
        self.start_symbol = start_symbol
        self.productions = Productions(productions)
        self._validate()
        firsts, follows = get_firsts_follows(self)
        self.firsts = MappingProxyType(firsts)
        self.follows = MappingProxyType(follows)

    def _validate(self) -> None:
        symbols = self.terminals | self.nonterminals
        if self.start_symbol not in self.nonterminals:
            raise InvalidStartSymbol(self.start_symbol)
        for production in self.productions:
            if production.left not in self.nonterminals:
                raise InvalidProduction(production, production.left)
            for symbol in production.right:
                if symbol not in symbols:
                    raise InvalidProduction(production, symbol)

    @property
    def has_left_recursion(self) -> bool:
        for nonterminal in self.nonterminals:
            derivations_leads = []
            for production in self.productions.lhs_filter(nonterminal):
                for symbol in production.right:
                    if isinstance(symbol, NonTerminalBase):
                        if symbol not in derivations_leads:
                            derivations_leads.append(symbol)
                        if not is_epsilon_generating(symbol, self.productions):
                            break
                    else:
                        break
            if nonterminal in derivations_leads:
                return True
        return False
