from __future__ import annotations
import string
from typing import Optional, Set, Type
from typing_extensions import Literal

import parsergen
from parsergen.grammar.nonterminals import NonTerminalBase
from parsergen.grammar import Grammar


class Nonterminal(parsergen.grammar.nonterminals.declarative.nonterminal_base()):
    __root__ = True

# Expression -> Term ExpressionTail
# ExpressionTail -> epsilon
# ExpressionTail -> "+" Term ExpressionTail
# ExpressionTail -> "-" Term ExpressionTail
#
# Term -> Operand TermTail
# TermTail -> epsilon
# TermTail -> "*" Operand TermTail
# TermTail -> "/" Operand TermTail
#
# Operand -> Number
# Operand -> "(" Expr ")"
# Operand -> Sign Operand
#
# Sign -> "+"
# Sign -> "-"


class Expression(Nonterminal):
    term: Term
    tail: Optional[ExpressionTail]


class ExpressionTail(Nonterminal):
    action: Literal["+", "-"]
    term: Term
    tail: Optional[ExpressionTail]


class Term(Nonterminal):
    operand: Operand
    tail: Optional[TermTail]


class TermTail(Nonterminal):
    action: Literal["*", "/"]
    operand: Operand
    tail: Optional[TermTail]


class Operand(Nonterminal):
    __abstract__ = True


class Parenthised(Operand):
    open_paren: Literal["("]
    expr: Expression
    close_paren: Literal[")"]


class Signed(Operand):
    sign: Literal["+", "-"]
    operand: Operand


class Number(Operand):
    digit: Literal["0", "1", "2", "3", "4", "5", "6", "7", "8", "9"]
    digits: Optional[digits]


class digits(Nonterminal):
    digit: Literal["0", "1", "2", "3", "4", "5", "6", "7", "8", "9"]
    digits: Optional[digits]


math_terminals: Set[str] = {*string.digits, *"+-*/()"}
math_nterminals: Set[Type[Nonterminal]] = {*Nonterminal.get_nonterminals()}
math_productions = Nonterminal.get_productions()
math_grammar = Grammar(
    math_terminals, math_nterminals, Expression, math_productions
)
