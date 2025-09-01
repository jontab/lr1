from .grammar    import Grammar, Rule # type: ignore
from collections import defaultdict
from doctest     import testmod
from itertools   import chain
from typing      import Iterable


def first_of_sequence(
    sequence: Iterable[str],
    first:    dict[str, set[str]],
    epsilon:  str,
) -> set[str]:
    out: set[str] = set()
    for symbol in sequence:
        out |= first[symbol] - {epsilon}
        if epsilon not in first[symbol]:
            return out
    out.add(epsilon)
    return out


class FirstSets:
    """
    >>> G = Grammar.create([ \
        Rule("a", ["a", "+", "i"]), \
        Rule("a", ["i"]), \
        Rule("i", ["(", "a", ")"]), \
        Rule("i", ["1"])])
    >>> F = FirstSets(G)
    >>> F.of_symbol("S") - {'1', '('}
    set()
    >>> F.of_symbol("a") - {'1', '('}
    set()
    >>> F.of_symbol("i") - {'1', '('}
    set()
    """

    def __init__(self, G: Grammar) -> None:
        self._G                          = G
        self._first: dict[str, set[str]] = defaultdict(set)
        self._build()

    def of_symbol(self, symbol: str) -> set[str]:
        return self._first[symbol]

    def of_sequence(self, sequence: Iterable[str]) -> set[str]:
        return first_of_sequence(sequence, self._first, self._G.symbol_epsilon)

    def _build(self) -> None:
        for symbol in chain(self._G.symbols.terminals, (self._G.symbol_epsilon,)):
            self._first[symbol] = {symbol}
        changed = True
        while changed:
            changed = False
            for nonterminal, rule_indices in self._G.by_lhs.items():
                before = len(self._first[nonterminal])
                for rule_index in rule_indices:
                    self._first[nonterminal] |= self.of_sequence(self._G.rules[rule_index].rhs)
                if len(self._first[nonterminal]) > before:
                    changed = True


if __name__ == "__main__":
    testmod()
