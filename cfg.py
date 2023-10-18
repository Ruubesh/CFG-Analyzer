class NonTerminals:
    def __init__(self):
        self.nonterminals = ["A", "B", "C"]


class Terminals:
    def __init__(self):
        self.terminals = ["a", "b"]


class CFG:
    def __init__(self):
        self.rules = {}

    def add_rule(self, nonterminal, expansions):
        if nonterminal not in self.rules:
            self.rules[nonterminal] = []
        self.rules[nonterminal].extend(expansions)

    def expand(self, initial_nonterminal):
        if initial_nonterminal not in self.rules:
            return initial_nonterminal

        print(f"Choose the next expansion for '{initial_nonterminal}':")
        for i, option in enumerate(self.rules[initial_nonterminal], 1):
            print(f"{i}: {' '.join(option)}")
        choice = int(input("Enter the number of your choice: "))
        selected_expansion = self.rules[initial_nonterminal][choice - 1]

        expansion = [self.expand(item) for item in selected_expansion]

        return "".join(expansion)


def main():
    grammar = CFG()
    nonterminals = NonTerminals().nonterminals
    terminals = Terminals().terminals

    grammar.add_rule(nonterminals[0],
                     [[terminals[0], nonterminals[1], nonterminals[1], terminals[1]],
                      [nonterminals[0], terminals[0], nonterminals[0]]])
    grammar.add_rule(nonterminals[1],
                     [[""],
                      [terminals[1], nonterminals[2], nonterminals[0]]])
    grammar.add_rule(nonterminals[2],
                     [[nonterminals[0], nonterminals[1]],
                      [terminals[0]],
                      [terminals[1]]])
    result = grammar.expand(nonterminals[0])
    print(result)


if __name__ == "__main__":
    main()
