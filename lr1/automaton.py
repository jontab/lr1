from .first      import FirstSets
from .grammar    import Grammar, Rule # type: ignore
from collections import deque
from dataclasses import dataclass
from doctest     import testmod


@dataclass(frozen=True, order=True)
class LR1Item:
    rule_index: int
    dot:        int
    lookahead:  str

    def __repr__(self) -> str:
        return f"I({self.rule_index}, {self.dot}, '{self.lookahead}')"


def closure(G: Grammar, F: FirstSets, kernel: set[LR1Item]) -> frozenset[LR1Item]:
    """
    >>> G = Grammar.create([ \
        Rule("a", ["a", "+", "i"]), \
        Rule("a", ["i"]), \
        Rule("i", ["(", "a", ")"]), \
        Rule("i", ["1"])])
    >>> F = FirstSets(G)
    >>> sorted(closure(G, F, {LR1Item(0, 0, G.symbol_end)}))
    [I(0, 0, '$'), I(1, 0, '$'), I(1, 0, '+'), I(2, 0, '$'), I(2, 0, '+'), I(3, 0, '$'), I(3, 0, '+'), I(4, 0, '$'), I(4, 0, '+')]
    """
    if not kernel:
        return frozenset()

    items = set(kernel)

    # Like in `first`, we do a "fixed-point" algorithm (the `changed`)
    # condition.
    changed = True
    while changed:
        changed = False
        for item in list(items):  # This might change as we iterate.
            rule = G.rules[item.rule_index]

            # Some of these items might be "reductions" - when the dot is at
            # the end of the right-hand side. We have nothing to do for these.
            if item.dot >= len(rule.rhs):
                continue

            symbol = rule.rhs[item.dot]

            # And if the dot is before a terminal, then we also have nothing
            # to do.
            if symbol in G.symbols.terminals:
                continue

            # `beta` will be everything that comes after the current symbol. We
            # use `beta` to calculate all the possible lookaheads that come
            # after the symbol we're looking at.
            beta       = rule.rhs[item.dot + 1 :]
            lookaheads = F.of_sequence(beta + [item.lookahead]) - {G.symbol_epsilon}

            # And for every lookahead that comes after the `symbol`, we add
            # (rule, lookahead) for every rule where `symbol` is on the
            # left-hand side (and with the dot at the beginning).
            for rule_index in G.by_lhs[symbol]:
                for lookahead in lookaheads:
                    new = LR1Item(rule_index, 0, lookahead)
                    if new not in items:
                        items.add(new)
                        changed = True

    return frozenset(items)


def goto(
    G: Grammar,
    F: FirstSets,
    state: frozenset[LR1Item],
    symbol: str,
) -> frozenset[LR1Item]:
    kernel: set[LR1Item] = set()
    for item in state:
        rule = G.rules[item.rule_index]
        if item.dot < len(rule.rhs) and rule.rhs[item.dot] == symbol:
            kernel.add(LR1Item(item.rule_index, item.dot + 1, item.lookahead))
    return closure(G, F, kernel)


def frontier(G: Grammar, state: frozenset[LR1Item]) -> set[str]:
    """
    >>> G = Grammar.create([ \
        Rule("a", ["a", "+", "i"]), \
        Rule("a", ["i"]), \
        Rule("i", ["(", "a", ")"]), \
        Rule("i", ["1"])])
    >>> frontier(G, frozenset({LR1Item(1, 1, G.symbol_end)}))
    {'+'}
    """
    frontier: set[str] = set()
    for item in state:
        rule = G.rules[item.rule_index]
        if item.dot < len(rule.rhs):
            frontier.add(rule.rhs[item.dot])
    return frontier


@dataclass
class LR1Automaton:
    states: dict[frozenset[LR1Item], int]
    edges:  dict[tuple[int, str], int]

    @classmethod
    def create(cls, G: Grammar, F: FirstSets) -> "LR1Automaton":
        """
        >>> G = Grammar.create([ \
            Rule("a", ["a", "+", "i"]), \
            Rule("a", ["i"]), \
            Rule("i", ["(", "a", ")"]), \
            Rule("i", ["1"])])
        >>> F = FirstSets(G)
        >>> A = LR1Automaton.create(G, F)
        >>> len(A.states), len(A.edges)
        (16, 23)
        """
        I0                                = closure(G, F, {LR1Item(0, 0, G.symbol_end)})
        states                            = { I0: 0 }
        edges: dict[tuple[int, str], int] = dict()
        work                              = deque([I0])
        while work:
            I = work.popleft()
            i = states[I]
            for symbol in sorted(frontier(G, I)):
                J = goto(G, F, I, symbol)
                if not J:
                    continue
                j = states.get(J)
                if j is None:
                    states[J] = (j := len(states))
                    work.append(J)
                edges[(i, symbol)] = j
        return cls(states, edges)


if __name__ == "__main__":
    testmod()
