from .unique     import generate_unique_symbol
from collections import defaultdict
from dataclasses import dataclass
from doctest     import testmod
from typing      import Union


EBNFNode = Union[str, "Seq", "Alt", "Star", "Plus", "Maybe"]


@dataclass
class Seq:
    items: list[EBNFNode]


@dataclass
class Alt:
    items: list[EBNFNode]


@dataclass
class Star:
    item: EBNFNode


@dataclass
class Plus:
    item: EBNFNode


@dataclass
class Maybe:
    item: EBNFNode


class GenSymb:
    def __init__(self) -> None:
        self._n = 0

    def fresh(self, base: str) -> str:
        self._n += 1
        return f"__{base}_{self._n}"


def lower(node: EBNFNode, hint: str, gen: GenSymb) -> tuple[str, list["BNFRule"]]:
    out: list[BNFRule]   = []

    def go(n: EBNFNode, h: str) -> str:
        nonlocal out

        if isinstance(n, str):
            return n

        if isinstance(n, Seq):
            heads = [go(x, f"{h}_seq") for x in n.items]

            if len(heads) == 0:
                new = gen.fresh(f"{h}_eps")
                out.append(BNFRule(new, []))
                return new

            if len(heads) == 1:
                return heads[0]

            new = gen.fresh(f"{h}_seq")
            out.append(BNFRule(new, heads))
            return new

        if isinstance(n, Alt):
            new = gen.fresh(f"{h}_alt")

            for item in n.items:
                out.append(BNFRule(new, [go(item, f"{h}_alt")]))

            return new

        if isinstance(n, Star):
            body = go(n.item, f"{h}_star_body")
            new  = gen.fresh(f"{h}_star")
            out.append(BNFRule(new, [body, new]))
            out.append(BNFRule(new, []))
            return new

        if isinstance(n, Plus):
            body = go(n.item, f"{h}_plus_body")
            star = gen.fresh(f"{h}_star")
            out.append(BNFRule(star, [body, star]))
            out.append(BNFRule(star, []))

            plus = gen.fresh(f"{h}_plus")
            out.append(BNFRule(plus, [body, star]))
            return plus

        # Maybe.
        body = go(n.item, f"{h}_maybe_body")
        new  = gen.fresh(f"{h}_maybe")
        out.append(BNFRule(new, [body]))
        out.append(BNFRule(new, []))
        return new

    head = go(node, hint)
    return head, out


def expand(rules: list["Rule"]) -> list["BNFRule"]:
    gen               = GenSymb()
    final: list[BNFRule] = []

    for rule in rules:
        head, extra = lower(Seq(rule.rhs), rule.lhs, gen)
        final.append(BNFRule(rule.lhs, [head]))
        final.extend(extra)

    return final


@dataclass
class Rule:
    lhs: str
    rhs: list[EBNFNode]


@dataclass
class BNFRule:
    lhs: str
    rhs: list[str]


@dataclass
class Symbols:
    symbols:      list[str]
    nonterminals: list[str]
    terminals:    list[str]

    @classmethod
    def create(cls, user_rules: list[BNFRule]) -> "Symbols":
        """
        >>> Symbols.create([Rule("a", ["b"]), Rule("b", ["c", "d"])])
        Symbols(symbols=['a', 'b', 'c', 'd'], nonterminals=['a', 'b'], terminals=['c', 'd'])
        """
        user_symbols:      list[str] = list()
        user_nonterminals: list[str] = list()
        user_terminals:    list[str] = list()
        for rule in user_rules:
            if rule.lhs not in user_nonterminals:
                user_symbols.append(rule.lhs)
                user_nonterminals.append(rule.lhs)
        for rule in user_rules:
            for symbol in rule.rhs:
                if symbol not in user_nonterminals:
                    user_symbols.append(symbol)
                    user_terminals.append(symbol)
        return cls(
            symbols      = user_symbols,
            nonterminals = user_nonterminals,
            terminals    = user_terminals,
        )


@dataclass
class Grammar:
    symbols:        Symbols
    rules:          list[BNFRule]
    by_lhs:         dict[str, list[int]]
    symbol_start:   str
    symbol_end:     str
    symbol_epsilon: str

    @classmethod
    def create(cls, user_rules: list[BNFRule]) -> "Grammar":
        """
        >>> g = Grammar.create([Rule("S", ["e"]), Rule("e", "$")])
        >>> g.symbols
        Symbols(symbols=['S', 'e', '$', 'S1', '$1'], nonterminals=['S', 'e', 'S1'], terminals=['$', '$1'])
        >>> g.rules
        [Rule(lhs='S1', rhs=['S']), Rule(lhs='S', rhs=['e']), Rule(lhs='e', rhs='$')]
        >>> g.by_lhs
        defaultdict(<class 'list'>, {'S1': [0], 'S': [1], 'e': [2]})
        >>> g.symbol_start
        'S1'
        >>> g.symbol_end
        '$1'
        >>> g.symbol_epsilon
        'e1'
        """
        if not user_rules:
            raise ValueError("Rules list is empty")

        user_symbols   = Symbols.create(user_rules)
        symbol_start   = generate_unique_symbol("S", set(user_symbols.nonterminals))
        symbol_end     = generate_unique_symbol("$", set(user_symbols.terminals))
        symbol_epsilon = generate_unique_symbol("e", set(user_symbols.symbols))
        rules          = [BNFRule(symbol_start, [user_rules[0].lhs])] + user_rules
        symbols        = Symbols(
            symbols      = user_symbols.symbols + [symbol_start, symbol_end],
            nonterminals = user_symbols.nonterminals + [symbol_start],
            terminals    = user_symbols.terminals + [symbol_end],
        )

        by_lhs: dict[str, list[int]] = defaultdict(list)
        for i, rule in enumerate(rules):
            by_lhs[rule.lhs].append(i)

        return cls(
            symbols        = symbols,
            rules          = rules,
            by_lhs         = by_lhs,
            symbol_start   = symbol_start,
            symbol_end     = symbol_end,
            symbol_epsilon = symbol_epsilon
        )

    def print(self) -> None:
        length = max(len(rule.lhs) for rule in self.rules)
        for rule in self.rules:
            print(f"{rule.lhs:<{length}} := {' '.join(rule.rhs)}")


if __name__ == "__main__":
    testmod()
