from .unique     import generate_unique_symbol
from collections import defaultdict
from dataclasses import dataclass
from doctest     import testmod


@dataclass
class Rule:
    lhs: str
    rhs: list[str]


@dataclass
class Symbols:
    symbols:      list[str]
    nonterminals: list[str]
    terminals:    list[str]

    @classmethod
    def create(cls, user_rules: list[Rule]) -> "Symbols":
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
    rules:          list[Rule]
    by_lhs:         dict[str, list[int]]
    symbol_start:   str
    symbol_end:     str
    symbol_epsilon: str

    @classmethod
    def create(cls, user_rules: list[Rule]) -> "Grammar":
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
        rules          = [Rule(symbol_start, [user_rules[0].lhs])] + user_rules
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


if __name__ == "__main__":
    testmod()
