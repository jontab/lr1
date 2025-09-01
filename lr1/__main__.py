from .grammar import Rule
from .parser  import Node, Parser, Token


def evaluate(node: Node) -> float:
    match node.name:
        case "add":
            if len(node.kids) == 3:
                l  = evaluate(node.kids[0])
                r  = evaluate(node.kids[2])
                op = node.kids[1].name
                return l + r if op == "+" else l - r
            else:
                return evaluate(node.kids[0])

        case "mul":
            if len(node.kids) == 3:
                l  = evaluate(node.kids[0])
                r  = evaluate(node.kids[2])
                op = node.kids[1].name
                return l * r if op == "*" else l / r
            else:
                return evaluate(node.kids[0])

        case "atom":
            if len(node.kids) == 3:
                return evaluate(node.kids[1])
            else:
                return evaluate(node.kids[0])

        case "int":
            return float(node.token.value) # type: ignore

        case _:
            raise ValueError("Unexpected node type: " + node.name)


def main() -> None:
    parser = Parser(
        [
            Rule("add", ["add", "+", "mul"]),
            Rule("add", ["add", "-", "mul"]),
            Rule("add", ["mul"]),
            Rule("mul", ["mul", "*", "atom"]),
            Rule("mul", ["mul", "/", "atom"]),
            Rule("mul", ["atom"]),
            Rule("atom", ["(", "add", ")"]),
            Rule("atom", ["int"]),
        ]
    )
    root = parser.parse(
        [
            Token("int", 5),
            Token("*"),
            Token("("),
            Token("int", 1),
            Token("-"),
            Token("int", 1),
            Token("+"),
            Token("int", 1),
            Token(")"),
        ]
    )
    root.print()
    print("Eval: " + str(evaluate(root)))


if __name__ == "__main__":
    main()
