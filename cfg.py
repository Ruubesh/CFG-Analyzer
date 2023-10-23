class Stack:
    def __init__(self):
        self.data = []
        self.index = -1  # Current position in the stack

    def push(self, item):
        # When a new item is pushed, remove any redo data
        self.data = self.data[:self.index + 1]
        self.data.append(item)
        self.index += 1

    def undo(self):
        if self.index > 0:
            self.index -= 1
            self.printst(self.index)
            return self.data[self.index]
        else:
            print("Nothing to undo")
            return None

    def redo(self):
        if self.index < len(self.data) - 1:
            self.index += 1
            self.printst(self.index)
            return self.data[self.index]
        else:
            print("Nothing to redo")
            return None

    def current(self):
        if 0 <= self.index < len(self.data):
            return self.data[self.index]
        else:
            return None

    def printst(self, ind = ""):
        if ind:
            endval = ind + 1
        else:
            endval = len(self.data)
        for i in range(endval):
            if i == endval - 1:
                print (f"{self.data[i]}")
            else:
                print (f"{self.data[i]} -->", end = " ")


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

    def expand(self, initial_nonterminal, stack):
        if initial_nonterminal not in self.rules:
            return initial_nonterminal

        print(f"\n Choose the next expansion for '{initial_nonterminal}':")
        for i, option in enumerate(self.rules[initial_nonterminal], 1):
            print(f"{i}: {' '.join(option)}")
        choice = input("Enter the number of your choice: \n ")

        selected_expansion = self.rules[initial_nonterminal][int(choice) - 1]

        ldata = (stack.current()).replace(initial_nonterminal, "".join(selected_expansion), 1)
        stack.push(ldata)
        stack.printst()
        expansion = ""
        non_terminal = ''
        nonterminals = NonTerminals().nonterminals
        while True:
            val = [elem for elem in nonterminals if elem in list(ldata)]
            if val:
                non_terminal = input(f"\n Last expansion : {ldata} \n Choose the next non terminal for expansion or 'u' to undo or 'r' to redo : \n")
                if non_terminal == 'u' or non_terminal == 'r':
                    if non_terminal == 'u':
                        dt = stack.undo()
                    elif non_terminal == 'r':
                        dt = stack.redo()
                    if dt:
                        ldata = dt
                else:
                    break
            else:
                break
        if non_terminal in val:
            expansion = self.expand(non_terminal, stack)
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

    stack = Stack()
    nt = input(f"Choose the first non-terminal from the given list to expand \n {nonterminals} \n ")
    if nt in nonterminals:
        stack.push(nt)
        result = grammar.expand(nt, stack)
        print(f'\n {result}')
    else:
        print(f"Invalid choice")


if __name__ == "__main__":
    main()
