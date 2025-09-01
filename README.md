# lr1

This repository contains an LR(1) parser written in Python along with an example
arithmetic grammar and the result of parsing a simple arithmetic expression. It
also prints the parse-tree pretty nicely which was my cherry-on-top.

```
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

(base) jonab@Jonathans-MacBook-Pro lr1 % python -m lr1
add
└─ mul
   └─ mul
      └─ atom
         └─ int (5)
   └─ *
   └─ atom
      └─ (
      └─ add
         └─ add
            └─ add
               └─ mul
                  └─ atom
                     └─ int (1)
            └─ -
            └─ mul
               └─ atom
                  └─ int (1)
         └─ +
         └─ mul
            └─ atom
               └─ int (1)
      └─ )
Eval: 5.0
```

# Structure

```
lr1/grammar.py

Contains methods that normalizes the grammar that the user gives into one that
(1) contains a new augmented start state;
(2) contains a special end-of-file token;
(3) and, in general, organizes symbols, terminals, and non-terminals into one place.

lr1/first.py

Contains methods that take the augmented grammar and calculates the "FIRST" sets
for all terminals and non-terminals. The "FIRST" sets are the terminals that can
appear in the left-most derivation of that symbol. 
(1) For terminals, the "FIRST" set trivially contains the terminal itself.
(2) For non-terminals, the "FIRST" set contains terminals per above.

This file also contains methods to calculate the "FIRST" set of a sequence. This
is used later-on when we perform the closure of item sets, when we need to calculate
new lookahead values.

lr1/automaton.py

This file builds the graph-structure of the LR1 automaton, given the grammar and
the first sets calculated via the above modules. It starts with the closure of
the starting state, and defines edges for symbols that appear after the dot of
any given state. When the automaton is built, we have the full graph-like
structure of the LR1 automaton that can then be converted to "ACTION" and "GOTO"
tables.

lr1/tables.py

Whereas the automaton is built in automaton.py, the tables are built here. We
loop through all of the edges defined above, and populate the "ACTION" and
"GOTO" tables accordingly.
(1) The state that contains the item where the dot is at the end of the starting
rule, and the lookahead is the special end-of-file token, is defined as the
accepting state. In parsing, if we ever end up in this state, then we accept
the input and return the tree that we've constructed along the way.
(2) The states where an item is at the end of a rule and the left-hand side is
not the starting symbol, we add a "REDUCE" rule into the "ACTION" table.
(3) For any edge, if the symbol on that edge is a terminal, then we populate
the "ACTION" table with a "SHIFT" action that, in parsing, will consume a
token from the input stream and move onto the state inside of the "SHIFT"
payload.
(4) For any edge, if the symbol on that edge is a non-terminal, then we add
an entry to the "GOTO" table; we use the "GOTO" table in parsing whenever we
perform a "REDUCE" action.

lr1/parser.py

Contains the logic that executes the tables built in the above file. This
should be straightforward to read. We look up the action for the given
lookahead and the current state.

(1) If the action is "ACCEPT", we return the top of the node stack.
(2) If the action is "REDUCE", we pop off however many nodes and states off of
the node and state stacks (the length of the right-hand side of the rule pointed
to by the index within the "REDUCE" action payload). Those nodes that we popped
off become a new node that we construct that represents this rule that we've
"completed". We then move onto the new state according to the new top of the
state stack and the left-hand side of the completed rule.
(3) If the action is "SHIFT", we consume a token from the input stream and move
onto the state specified within the action payload.

lr1/__main__.py

I've put here the grammar for a simple arithmetic calculator and parse a simple
expression with it. For fun, I also interpreted (evaluated) it and print out
the resulting value. In a sense, in this repository, I've implemented both
LR1 parsing and an interpreter.
```
