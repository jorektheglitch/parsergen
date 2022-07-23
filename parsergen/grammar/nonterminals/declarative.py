from __future__ import annotations

import sys

from typing import Any, Dict, Iterable, Tuple, Type, get_type_hints
from typing import Union
if sys.version_info >= (3, 8):
    from typing import get_args, get_origin
    from typing import Literal
else:
    from typing_extensions import get_args, get_origin
    from typing_extensions import Literal


def subclasses(cls, recursive=False):
    for subclass in cls.__subclasses__():
        yield subclass
        if recursive:
            yield from subclasses(subclass, recursive=True)


def get_lefts(generalized: Iterable):
    if not generalized:
        yield ()
        return
    item, *generalized_tail = generalized
    if isinstance(item, tuple):
        for variant in item:
            for tail in get_lefts(generalized_tail):
                yield (variant, *tail)
    else:
        for tail in get_lefts(generalized_tail):
            yield (item, *tail)


class NonTerminalMeta(type):

    __abstract: bool
    __root: bool

    def __new__(mcls, name: str, bases: Tuple[Type, ...], attrs: Dict[str, Any]):
        # print("new nt", name, bases)
        is_abstract = attrs.get("__abstract__", False)
        is_root = attrs.get("__root__", False)
        for attr_name in "__abstract__", "__root__":
            if attr_name in attrs:
                del attrs[attr_name]
        cls = super().__new__(mcls, name, bases, attrs)
        cls.__abstract = is_abstract
        cls.__root = is_root
        return cls

    def __call__(cls, *args, **kwargs):
        # TODO? make dataclasses-like __init__ work
        return super().__call__(*args, **kwargs)

    def __str__(cls):
        return cls.__name__

    @property
    def is_abstract(cls):
        return cls.__abstract

    @property
    def is_root(cls):
        return cls.__root

    def get_productions(cls):
        if not cls.is_root:
            TypeError(f"Can't call get_prosuctions on non-root nonterminal class {cls}")
        productions = []
        for nonterminal in subclasses(cls, recursive=True):
            annotations = get_type_hints(nonterminal)
            print(nonterminal.__name__)
            generalized_rule = []
            variative = (Union, Literal)
            for name, hint in annotations.items():
                origin = get_origin(hint)
                args = get_args(hint)
                _args = ", ".join(
                    arg if isinstance(arg, str) else arg.__name__ for arg in args
                )
                args_repr = f"[{_args}]" if args else ""
                print(f"  {name}: {origin}{args_repr}")
                if isinstance(hint, NonTerminalMeta):
                    generalized_rule.append(hint)
                elif origin in variative:
                    generalized_rule.append(args)
            for left in get_lefts(generalized_rule):
                productions.append((nonterminal, left))
            print()
        return productions


def nonterminal_base():
    return NonTerminalMeta(
        "RootNonTerminal", (), {"__root__": True}
    )


NonTerminal = nonterminal_base()


class Expr(NonTerminal):
    expr: Union[Add, Mul, Unary, Exp, Operand]


class Add(NonTerminal):
    left: Union[Add, Mul, Unary, Exp, Operand]
    op: Literal["+"]
    right: Union[Mul, Unary, Exp, Operand]


class Mul(NonTerminal):
    left: Union[Mul, Unary, Exp, Operand]
    op: Literal["*"]
    right: Union[Unary, Exp, Operand]


class Unary(NonTerminal):
    sign: Literal["-"]
    operand: Union[Operand, Exp]


class Exp(NonTerminal):
    left: Operand
    op: Literal["**"]
    right: Union[Exp, Unary, Operand]


class Operand(NonTerminal):
    means: Union[Number, Parenthised]


class Parenthised(NonTerminal):
    left_paren: Literal["("]
    expr: Expr
    right_paren: Literal[")"]


class Number:
    pass


for nt, rule in NonTerminal.get_productions():
    print(nt, "->", " ".join(map(str, rule)))

# e = Expr(Operand(Number()))
