from __future__ import annotations

from typing import Dict, Iterable, Optional, Set, Tuple, Union

from typing import TYPE_CHECKING

from parsergen.grammar import TerminalsSet
from parsergen.grammar.nonterminals import NonTerminalBase, SpecialNonterminal, epsilon
from parsergen.grammar.productions import Production
if TYPE_CHECKING:
    from . import Grammar, TerminalSets
    from . import Terminal, Nonterminal


def clean_grammar(
    grammar: Grammar[Terminal, Nonterminal]
) -> Grammar[Terminal, Nonterminal]:
    productions = set(grammar.productions)
    generating_nts = get_generating_nts(grammar)
    nongenerating_nts = grammar.nonterminals.difference(generating_nts)
    generating_productions = {
        production for production in productions
        if not (
            any(symbol in nongenerating_nts for symbol in production.rule)
            or
            production.left in nongenerating_nts
        )
    }
    reachable_nts = get_reachable_nts(grammar.start_symbol, generating_productions)
    unreachable_nts = grammar.nonterminals.difference(reachable_nts)
    reachable_productions = {
        production for production in productions
        if not (
            any(symbol in unreachable_nts for symbol in production.rule)
            or
            production.left in unreachable_nts
        )
    }
    cleaned_grammar = Grammar(
        grammar.terminals,
        reachable_nts,
        grammar.start_symbol,
        reachable_productions
    )
    return cleaned_grammar


def get_epsilonless_grammar(
    grammar: Grammar[Terminal, Nonterminal]
) -> Grammar[Terminal, Nonterminal]:
    raise NotImplementedError


def get_nonleftrecursive_grammar(
    grammar: Grammar[Terminal, Nonterminal]
) -> Grammar[Terminal, Nonterminal]:
    raise NotImplementedError


def get_nonlong_grammar(
    grammar: Grammar[Terminal, Nonterminal]
) -> Grammar[Terminal, Nonterminal]:
    raise NotImplementedError


def get_generating_nts(
    grammar: Grammar[Terminal, Nonterminal]
) -> Set[Nonterminal]:
    productions = grammar.productions
    counters = {
        production: sum(not isinstance(s, NonTerminalBase) for s in production.rule)
        for production in productions
    }
    concerned_productions = {
        nt: [production for production in productions if nt in production.rule]
        for nt in grammar.nonterminals
    }
    generating_nts = [
        production.left
        for production, counter in counters.items()
        if counter == 0
    ]
    for nt in generating_nts:
        concerned = concerned_productions[nt]
        for production in concerned:
            counters[production] -= 1
            if counters[production] == 0:
                generating_nts.append(production.left)
    return set(generating_nts)


def get_reachable_nts(
    start_symbol: Nonterminal, productions: Iterable[Production[Terminal, Nonterminal]]
) -> Set[Nonterminal]:
    reachable_nts = [start_symbol]
    for nt in reachable_nts:
        new_reachables = [
            symbol
            for production in productions
            for symbol in production.right
            if production.left == nt and isinstance(symbol, NonTerminalBase)
        ]
        for reachable in new_reachables:
            if reachable not in reachable_nts:
                reachable_nts.append(reachable)
    return set(reachable_nts)


def get_epsilon_generatings(grammar: Grammar[Terminal, Nonterminal]) -> Set[Nonterminal]:
    epsilon_generatings: Set[Nonterminal] = {epsilon}
    changed = True
    while changed:
        changed = False
        for production in grammar.productions:
            if production.left in epsilon_generatings:
                continue
            if all(symbol in epsilon_generatings for symbol in production.rule):
                changed = True
                epsilon_generatings.add(production.left)
    return epsilon_generatings


def get_firsts_follows(
    grammar: Grammar[Terminal, Nonterminal]
) -> Tuple[Dict[Nonterminal, TerminalsSet[Terminal]], Dict[Nonterminal, TerminalsSet[Terminal]]]:
    grammar = clean_grammar(grammar)
    firsts = get_firsts(grammar)
    follows = get_follows(grammar, firsts)
    return firsts, follows


def get_firsts(
    grammar: Grammar[Terminal, Nonterminal]
) -> Dict[Nonterminal, TerminalsSet[Terminal]]:
    """
    FIRST(A) = {c ∣ A⇒∗cβ} ∪ {ε if A⇒∗ε}

    Lemma: FIRST(αβ) = FIRST(α) ∪ (FIRST(β) if ε∈FIRST(α))
    Lemma: FIRST(cα) = {c}; FIRST(ε) = {ε}
    """
    raw_firsts: Dict[Nonterminal, Set[Union[Terminal, Nonterminal]]] = {
        nonterminal: set() for nonterminal in grammar.nonterminals
    }
    epsilon_generatings = get_epsilon_generatings(grammar)
    for production in grammar.productions:
        nt = production.left
        rule = production.rule
        nt_firsts = raw_firsts[nt]
        for symbol in rule:
            nt_firsts.add(symbol)
            if symbol not in epsilon_generatings:
                break
    clean_firsts: Dict[Nonterminal, Set[Terminal]] = {
        nt: {terminal for terminal in terminals if not isinstance(terminal, NonTerminalBase)}
        for nt, terminals in raw_firsts.items()
    }
    updates: Dict[Nonterminal, Tuple[Set[Terminal], Set[Nonterminal]]] = {
        nt: (
            {symbol for symbol in symbols if not isinstance(symbol, NonTerminalBase)},
            {symbol for symbol in symbols if isinstance(symbol, NonTerminalBase)}
        )
        for nt, symbols in raw_firsts.items()
    }
    while updates:
        new_updates: Dict[Nonterminal, Tuple[Set[Terminal], Set[Nonterminal]]] = {}
        for nt, (terminals, nonterminals) in updates.items():
            firsts = clean_firsts[nt]
            firsts.update(terminals)
            firsts_nts = raw_firsts[nt]
            firsts_nts.update(nonterminals)
            new_terminals = {
                symbol
                for nonterminal in nonterminals
                for symbol in clean_firsts[nonterminal]
            }.difference(firsts)
            new_nonterminals = {
                nonterminal
                for nt in nonterminals
                for nonterminal in updates[nt][1]
            }.difference(firsts_nts)
            if new_terminals or new_nonterminals:
                new_updates[nt] = (new_terminals, new_nonterminals)
        updates = new_updates
    return clean_firsts


def get_follows(
    grammar: Grammar[Terminal, Nonterminal],
    firsts: Optional[TerminalSets[Terminal, Nonterminal]] = None
) -> Dict[Nonterminal, TerminalsSet[Terminal]]:
    """
    FOLLOW(A) = {c ∣ S⇒∗αAcβ} ∪ {$ if S⇒∗αA}

    Lemma: A→αBβ ∈ P                   ⇒ (FIRST(β)∖{ε}) ⊂ FOLLOW(B)
    Lemma: A→αB ∈ P                    ⇒ FOLLOW(A) ⊂ FOLLOW(B)
    Lemma: A→αBβ ∈ P ∧ (ε ∈ FIRST(β))  ⇒ FOLLOW(A) ⊂ FOLLOW(B)
    """
    firsts = firsts or get_firsts(grammar)
    raw_follows: Dict[Nonterminal, Set[Union[Terminal, Nonterminal, SpecialNonterminal]]] = {
        nonterminal: set() for nonterminal in grammar.nonterminals
    }
    epsilon_generatings = get_epsilon_generatings(grammar)
    for production in grammar.productions:
        nt = production.left
        rule = production.rule
        for symbol in reversed(rule):
            if isinstance(symbol, NonTerminalBase):
                raw_follows[symbol].add(nt)
            if symbol not in epsilon_generatings:
                break
        *rule_, follower = rule
        for symbol in reversed(rule_):
            if isinstance(follower, NonTerminalBase):
                raw_follows[symbol].update(firsts[follower])
            else:
                raw_follows[symbol].add(follower)
            follower = symbol
    clean_follows: Dict[Nonterminal, Set[Terminal]] = {
        nt: {terminal for terminal in terminals if not isinstance(terminal, NonTerminalBase)}
        for nt, terminals in raw_follows.items()
    }
    updates: Dict[Nonterminal, Tuple[Set[Terminal], Set[Nonterminal]]] = {
        nt: (
            {symbol for symbol in symbols if not isinstance(symbol, NonTerminalBase)},
            {symbol for symbol in symbols if isinstance(symbol, NonTerminalBase)}
        )
        for nt, symbols in raw_follows.items()
    }
    while updates:
        new_updates: Dict[Nonterminal, Tuple[Set[Terminal], Set[Nonterminal]]] = {}
        for nt, (terminals, nonterminals) in updates.items():
            follows = clean_follows[nt]
            follows.update(terminals)
            follows_nts = raw_follows[nt]
            follows_nts.update(nonterminals)
            new_terminals = {
                symbol
                for nonterminal in nonterminals
                for symbol in clean_follows[nonterminal]
            }.difference(follows)
            new_nonterminals = {
                nonterminal
                for nt in nonterminals
                for nonterminal in updates[nt][1]
            }.difference(follows_nts)
            if new_terminals or new_nonterminals:
                new_updates[nt] = (new_terminals, new_nonterminals)
        updates = new_updates
    return clean_follows
