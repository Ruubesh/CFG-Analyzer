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
    grammar.add_rule("A", [["a", "B", "B", "b"], ["A", "a", "A"]])
    grammar.add_rule("B", [[""], ["b", "C", "A"]])
    grammar.add_rule("C", [["A", "B"], ["a"], ["b"]])
    result = grammar.expand("A")
    print(result)


if __name__ == "__main__":
    main()
