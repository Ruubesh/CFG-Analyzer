import re
import configparser


class CaseSensitiveConfigParser(configparser.ConfigParser):
    def optionxform(self, optionstr):
        return optionstr


class Stack:
    def __init__(self):
        self.data = []
        self.index = -1

    def push(self, item):
        self.data = self.data[:self.index + 1]
        self.data.append(item)
        self.index += 1

    def undo(self, format, nonterminals):
        if self.index > 0:
            self.index -= 1
            if format == "S":
                self.printst(self.index)
            if format == "T":
                new_st = Stack()
                new_st.data = self.data[0:self.index + 1]
                CFG().build_tree(new_st, nonterminals)
            return self.data[self.index]
        else:
            print("Nothing to undo")
            return None

    def redo(self, format, nonterminals):
        if self.index < len(self.data) - 1:
            self.index += 1
            if format == "S":
                self.printst(self.index)
            if format == "T":
                new_st = Stack()
                new_st.data = self.data[0:self.index + 1]
                CFG().build_tree(new_st, nonterminals)
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

    def print_tree(self, indent=""):
        prefix = indent[:-3] + "|_ "*bool(indent)
        if self.data == "":
            print(f'{prefix}\u03B5')
        else:
            print(prefix + self.data)
        for more, child in enumerate(self.children, 1-len(self.children)):
            childIndent = "|  " if more else "   "
            child.print_tree(indent+childIndent)

    def add_child(self, child):
        child.parent = self
        self.children.append(child)


class CFG:
    def __init__(self):
        self.rules = {}
        self.nonterminals = []
        self.terminals = []
        self.initial_nonterminal = ''
        self.stack = Stack()
        self.stack_tree = Stack()

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

    def create_class(self, class_names):
        for class_name in class_names:
            globals()[class_name] = type(class_name, (), {'attribute': class_name})

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

    def build_tree(self, stack_tree, nonterminals):
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

    def write_to_config(self, config):
        with open('grammar.txt', 'w') as cf:
            config.write(cf)

    def add_rule_to_config(self, config, val):
        nt, rule = val.split("=")
        if nt in config['rules']:
            nt_rule = config['rules'][nt].split(',')
            nt_rule.append(rule)
            nt_rule = ",".join(nt_rule)
        else:
            nt_rule = rule
        config.set('rules', nt, nt_rule)
        self.write_to_config(config)

    def add_value(self, config, val_type, val):
        data = config['input'][val_type].split(',')
        if val not in data:
            data.append(val)
            new_val = ','.join(data)
            config.set('input', val_type, new_val)
            self.write_to_config(config)
        else:
            print(f'{val_type} {val} already exists')

    def get_dependent_rules(self, val):
        dlist = []
        for nt in self.rules:
            for rlist in self.rules[nt]:
                if val in rlist:
                    print(f'Rule {nt} has dependency on {val}: {"".join(rlist)}')
                    dlist.append("".join(rlist))
        return dlist

    def remove_rule(self, config, val):
        if val in config['rules']:
            config.remove_option('rules', val)
            self.write_to_config(config)
        for nt in config['rules']:
            if val in config['rules'][nt].split(','):
                data = config['rules'][nt].split(',')
                data.remove(val)
                new_val = ','.join(data)
                config.set('rules', nt, new_val)
                self.write_to_config(config)

    def remove_value(self, config, val_type, val):
        data = config['input'][val_type].split(',')
        if val in data:
            dlist = self.get_dependent_rules(val)
            for rule in dlist:
                self.remove_rule(config, rule)

            self.remove_rule(config, val)
            data.remove(val)
            new_val = ','.join(data)
            config.set('input', val_type, new_val)
            self.write_to_config(config)
        else:
            print(f'{val_type} {val} does not exist')

    def expand(self, initial_nonterminal, stack, stack_tree, nonterminals):
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
        self.build_tree(stack_tree, nonterminals)
        non_terminal = ''
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
                        dt = stack.undo('S', nonterminals)
                        stack_tree.undo('T', nonterminals)
                    elif non_terminal == 'r':
                        dt = stack.redo('S', nonterminals)
                        stack_tree.redo('T', nonterminals)
                    if dt:
                        ldata = dt
                else:
                    break
            else:
                break
        if non_terminal in val:
            self.expand(non_terminal, stack, stack_tree, nonterminals)
        return stack.data[-1]


def main():
    config = CaseSensitiveConfigParser(interpolation=configparser.ExtendedInterpolation())
    config.read('grammar.txt')
    grammar = CFG()
    grammar.nonterminals = (config['input']['nonterminals']).split(',')
    grammar.terminals = (config['input']['terminals']).split(',')
    grammar.initial_nonterminal = config['input']['initial_nonterminal']
    grammar.create_class(grammar.nonterminals)
    grammar.create_class(grammar.terminals)
    for nt in grammar.nonterminals:
        nlist = []
        if nt in config['rules']:
            for elem in (config['rules'][nt]).split(','):
                if elem == 'epsilon':
                    elem = ['']
                else:
                    elem = list(elem)
                nlist.append(elem)
            grammar.add_rule(globals()[nt]().attribute, nlist)

    grammar.stack.push(grammar.initial_nonterminal)
    result = grammar.expand(grammar.initial_nonterminal, grammar.stack, grammar.stack_tree, grammar.nonterminals)
    print(f"\n{result.replace(' ', '')}")


if __name__ == "__main__":
    main()
