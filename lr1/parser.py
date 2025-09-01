from .automaton  import LR1Automaton
from .first      import FirstSets
from .grammar    import Grammar, Rule
from .tables     import LR1Tables
from dataclasses import dataclass


@dataclass
class Token:
    name:  str
    value: object | None = None


@dataclass
class Node:
    name:  str
    token: Token | None
    kids:  list["Node"]

    def print(self, origin: int = 0, depth: int = 0, indent: int = 3) -> None:
        for i in range(depth):
            if (i < origin) or (i == depth - 1):
                print(" ", end="")
            elif i == origin:
                print("└", end="")
            else:
                print("─", end="")

        print(self.name, end="")
        if self.token and self.token.value is not None:
            print(f" ({self.token.value})")
        else:
            print()

        for i, kid in enumerate(self.kids):
            kid.print(depth, depth + indent, indent)


class Parser:
    def __init__(self, rules: list[Rule]) -> None:
        self._G      = Grammar.create(rules)
        self._F      = FirstSets(self._G)
        self._A      = LR1Automaton.create(self._G, self._F)
        self._tables = LR1Tables.create(self._G, self._A)

    def parse(self, tokens: list[Token]) -> Node:
        stream            = tokens + [Token(self._G.symbol_end, None)]
        states            = [0]
        nodes: list[Node] = []
        i                 = 0
        while True:
            token  = stream[i]
            action = self._tables.action.get((states[-1], token.name))
            if action is None:
                exp = self._expected_from_state(states[-1])
                msg = f"Unexpected '{token.name}'; expected one of: " + ", ".join(exp)
                raise SyntaxError(msg)

            match action[0]:
                case "accept":
                    return nodes[-1]

                case "reduce":
                    rule = self._G.rules[action[1]]
                    if len(rule.rhs):
                        kids = nodes[-len(rule.rhs) :]
                        del nodes[-len(rule.rhs) :]
                        del states[-len(rule.rhs) :]
                    else:
                        kids = []
                    if g := self._tables.goto.get((states[-1], rule.lhs)):
                        nodes.append(Node(rule.lhs, None, kids))
                        states.append(g)
                    else:
                        raise RuntimeError(f"Missing goto from state: {states[-1]}")

                case "shift":
                    nodes.append(Node(token.name, token, []))
                    states.append(action[1])
                    i += 1

    def _expected_from_state(self, state: int) -> list[str]:
        return sorted(name for i, name in self._tables.action if i == state)
