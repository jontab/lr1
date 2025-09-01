from .automaton  import LR1Automaton
from .grammar    import Grammar
from dataclasses import dataclass
from typing      import Literal


@dataclass
class LR1Tables:
    action: dict[tuple[int, str], tuple[Literal["accept", "reduce", "shift"], int]]
    goto:   dict[tuple[int, str], int]

    @classmethod
    def create(cls, G: Grammar, A: LR1Automaton) -> "LR1Tables":
        action: dict[tuple[int, str], tuple[Literal["accept", "reduce", "shift"], int]] = dict()
        goto:   dict[tuple[int, str], int]                                              = dict()

        for (i, X), j in A.edges.items():
            if X in G.symbols.terminals:
                # TODO: Warn about shift-reduce conflict.
                action[(i, X)] = ("shift", j)
            else:
                goto[(i, X)] = j

        for (I, i) in A.states.items():
            for item in I:
                # Accept.
                rule = G.rules[item.rule_index]
                if (
                    rule.lhs == G.symbol_start
                    and item.dot == len(rule.rhs)
                    and item.lookahead == G.symbol_end
                ):
                    action[(i, G.symbol_end)] = ("accept", 0)

                # Reduce.
                if item.dot == len(rule.rhs) and rule.lhs != G.symbol_start:
                    # TODO: Warn about shift-reduce or reduce-reduce conflicts.
                    action[(i, item.lookahead)] = ("reduce", item.rule_index)

        return cls(action, goto)
