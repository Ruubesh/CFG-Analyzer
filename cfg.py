import re


class Stack:
    def __init__(self):
        self.data = []
        self.index = -1

    def push(self, item):
        self.data = self.data[:self.index + 1]
        self.data.append(item)
        self.index += 1

    def undo(self, format):
        if self.index > 0:
            self.index -= 1
            if format == "S":
                self.printst(self.index)
            if format == "T":
                new_st = Stack()
                new_st.data = self.data[0:self.index + 1]
                CFG().build_tree(new_st)
            return self.data[self.index]
        else:
            print("Nothing to undo")
            return None

    def redo(self, format):
        if self.index < len(self.data) - 1:
            self.index += 1
            if format == "S":
                self.printst(self.index)
            if format == "T":
                new_st = Stack()
                new_st.data = self.data[0:self.index + 1]
                CFG().build_tree(new_st)
            return self.data[self.index]
        else:
            if format == "S":
                print("Nothing to redo")
            return None

    def current(self):
        if 0 <= self.index < len(self.data):
            return self.data[self.index]
        else:
            return None

    def printst(self, ind=""):
        if ind:
            endval = ind + 1
        else:
            endval = len(self.data)
        for i in range(endval):
            if i == endval - 1:
                print(f"{self.data[i]}")
            else:
                print(f"{self.data[i]} -->", end=" ")


class TreeNode:
    def __init__(self, data):
        self.data = data
        self.children = []
        self.parent = None

    def get_level(self):
        level = 0
        p = self.parent
        while p:
            level += 1
            p = p.parent
        return level

    def print_tree(self):
        spaces = ' ' * self.get_level() * 3
        prefix = spaces + "|__" if self.parent else "   "
        if self.data == "":
            print(f'{prefix}\u03B5')
        else:
            print(prefix + self.data)
        for child in self.children:
            child.print_tree()

    def add_child(self, child):
        child.parent = self
        self.children.append(child)


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

    def replacer(self, string, sub, wanted, n):
        where = [m.start() for m in re.finditer(sub, string)][n - 1]
        before = string[:where]
        after = string[where:]
        after = after.replace(sub, wanted, 1)
        newString = before + after
        return newString

    def create_sentential_form(self, st, nt, exp, pos):
        new_st = Stack()
        if len(st) > 1:
            for i in range(len(st) - 2):
                new_st.push(st[i])
            nt_elem = self.replacer(st[-2], nt, f"[{nt}]", pos)
            if exp == "":
                exp_elem = self.replacer(st[-2], nt, "[]", pos)
            else:
                exp_elem = self.replacer(st[-2], nt, f"[{exp}]", pos)
            new_st.push(nt_elem)
            new_st.push(exp_elem)
        new_st.printst()

    def build_tree(self, stack_tree):
        nonterminals = NonTerminals().nonterminals
        root_nt = list(stack_tree.data[0].keys())
        root = TreeNode(root_nt[0])
        nt_dict = {}
        for nt in nonterminals:
            nt_dict[nt] = 0
        nodes = {}
        node_st = Stack()
        node_st.push(root_nt[0])
        for data in stack_tree.data:
            for nt, expansion in data.items():
                if nt != 'position':
                    pos = data['position']
                    if len(nodes) == 0:
                        value = []
                        for elem in expansion:
                            if elem in nonterminals:
                                nt_dict[elem] += 1
                                nodes[f'{elem}{nt_dict[elem]}'] = TreeNode(elem)
                                value.append(f'{elem}{nt_dict[elem]}')
                                root.add_child(nodes[f'{elem}{nt_dict[elem]}'])
                            else:
                                value.append(elem)
                                root.add_child(TreeNode(elem))

                        d = self.replacer(node_st.current(), root_nt[0], " ".join(value), 1)
                        node_st.push(d)
                    else:
                        value = []
                        count = 0
                        for elem in expansion:
                            if elem in nonterminals:
                                nt_dict[elem] += 1
                                nodes[f'{elem}{nt_dict[elem]}'] = TreeNode(elem)
                                value.append(f'{elem}{nt_dict[elem]}')
                                for i in node_st.current().split():
                                    if nt in i:
                                        count += 1
                                        if count == pos:
                                            p_node = i

                                nodes[p_node].add_child(nodes[f'{elem}{nt_dict[elem]}'])
                            else:
                                value.append(elem)
                                for i in node_st.current().split():
                                    if nt in i:
                                        count += 1
                                        if count == pos:
                                            p_node = i

                                nodes[p_node].add_child(TreeNode(elem))

                        d = self.replacer(node_st.current(), p_node, " ".join(value), 1)
                        node_st.push(d)
        root.print_tree()

    def expand(self, initial_nonterminal, stack, stack_tree):
        if initial_nonterminal not in self.rules:
            return initial_nonterminal

        while True:
            try:
                print(f"Choose the next expansion for '{initial_nonterminal}':")
                for i, option in enumerate(self.rules[initial_nonterminal], 1):
                    if option[0] == '':
                        print(f"{i}: \u03B5")
                    else:
                        print(f"{i}: {' '.join(option)}")

                choice = int(input("Enter the number of your choice: \n "))
                selected_expansion = self.rules[initial_nonterminal][choice - 1]
                break
            except:
                print("Invalid choice!")

        while True:
            try:
                if stack.current().count(initial_nonterminal) > 1:
                    position = int(input(f"Enter the occurrence of '{initial_nonterminal}' to expand in '{stack.current()}' : \n "))
                else:
                    position = 1

                ldata = self.replacer(stack.current(), initial_nonterminal, " ".join(selected_expansion), position)
                break
            except:
                print("Invalid choice!")

        ldata = " ".join(ldata.split())
        stack.push(ldata)
        self.create_sentential_form(stack.data, initial_nonterminal, "".join(selected_expansion), position)
        stack_tree.push({initial_nonterminal: selected_expansion, "position": position})
        self.build_tree(stack_tree)
        non_terminal = ''
        nonterminals = NonTerminals().nonterminals
        while True:
            val = [elem for elem in nonterminals if elem in ldata.split(" ")]
            if val:
                if len(val) == 1:
                    while True:
                        non_terminal = input(
                            f"\nChosen nonterminal : {val[0]} \nPress 'ENTER' to continue or 'u' to undo or 'r' to redo : \n ")
                        if non_terminal == '':
                            non_terminal = val[0]
                        if non_terminal in val or non_terminal == 'u' or non_terminal == 'r':
                            break
                        else:
                            print("Invalid choice!")
                else:
                    while True:
                        non_terminal = input(
                            f"\nLast expansion : {ldata} \nChoose the next non terminal for expansion or 'u' to undo or 'r' to redo : \n ")
                        if non_terminal in val or non_terminal == 'u' or non_terminal == 'r':
                            break
                        else:
                            print("Invalid choice!")

                if non_terminal == 'u' or non_terminal == 'r':
                    if non_terminal == 'u':
                        dt = stack.undo('S')
                        stack_tree.undo('T')
                    elif non_terminal == 'r':
                        dt = stack.redo('S')
                        stack_tree.redo('T')
                    if dt:
                        ldata = dt
                else:
                    break
            else:
                break
        if non_terminal in val:
            self.expand(non_terminal, stack, stack_tree)
        return stack.data[-1]


def main():
    grammar = CFG()
    nonterminals = NonTerminals().nonterminals
    terminals = Terminals().terminals

    grammar.add_rule(nonterminals[0],
                     [[terminals[0], nonterminals[1], nonterminals[1], terminals[1]],
                      [nonterminals[0], terminals[0], nonterminals[0]]])
    grammar.add_rule(nonterminals[1],
                     [[''],
                      [terminals[1], nonterminals[2], nonterminals[0]]])
    grammar.add_rule(nonterminals[2],
                     [[nonterminals[0], nonterminals[1]],
                      [terminals[0]],
                      [terminals[1]]])

    stack = Stack()
    stack_tree = Stack()
    nt = input(f"Choose the first non-terminal from the given list to expand \n {nonterminals} \n ")
    if nt in nonterminals:
        stack.push(nt)
        result = grammar.expand(nt, stack, stack_tree)
        print(f"\n{result.replace(' ', '')}")
    else:
        print(f"Invalid choice")


if __name__ == "__main__":
    main()
