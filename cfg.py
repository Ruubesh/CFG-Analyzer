import re
import configparser
import os


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
                return self.printst(self.index), self.data[self.index]
            if format == "T":
                new_st = Stack()
                new_st.data = self.data[0:self.index + 1]
                return CFG().build_tree(new_st, nonterminals)
        elif self.index == 0:
            if format == 'S':
                return self.data[self.index], self.data[self.index]
            if format == 'T':
                self.index = -1
                return self.data[self.index]
        else:
            print("Nothing to undo")
            return None

    def redo(self, format, nonterminals):
        if self.index < len(self.data) - 1:
            self.index += 1
            if format == "S":
                return self.printst(self.index), self.data[self.index]
            if format == "T":
                new_st = Stack()
                new_st.data = self.data[0:self.index + 1]
                return CFG().build_tree(new_st, nonterminals)
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
        sentence = ''
        for i in range(endval):
            if i == endval - 1:
                print(f"{self.data[i]}")
                sentence += f"{self.data[i]}"
            else:
                print(f"{self.data[i]} ==>", end=" ")
                sentence += f"{self.data[i]} ==>"

        return sentence


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

    def print_tree(self, tree='', indent=""):
        prefix = indent[:-3] + "|_ " * bool(indent)
        if self.data == "":
            print(f'{prefix}\u03B5')
            tree += f'{prefix}\u03B5\n'
        else:
            print(prefix + self.data)
            tree += prefix + self.data + "\n"
        for more, child in enumerate(self.children, 1 - len(self.children)):
            childIndent = " |  " if more else "    "
            tree = child.print_tree(tree, indent + childIndent)

        return tree

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

    def set_to_list(self, set_temp, set_list):
        for temp in set_temp:
            if temp not in set_list:
                set_list.append(temp)

    def generate_grammar_text(self, file, rules):
        config = self.read_config(file)
        red = "ஆ"
        grammar_text = ''

        for section in config.sections():
            if section == 'rules':
                grammar_text += f"[{section}]\n"
                for nt in config[section]:
                    grammar_text += f"{nt} = "
                    rule_list = config[section][nt].split(',')
                    for index, rule in enumerate(rule_list):
                        if index == len(rule_list) - 1:
                            if rule in rules:
                                grammar_text += f"{red + rule + red}\n"
                            else:
                                grammar_text += f"{rule}\n"
                        else:
                            if rule in rules:
                                grammar_text += f"{red + rule + red},"
                            else:
                                grammar_text += f"{rule},"
            else:
                grammar_text += f"[{section}]\n"
                for key, value in config.items(section):
                    grammar_text += f"{key} = {value}\n"
                grammar_text += '\n'

        return grammar_text

    def reduce_phase1(self, file, config, grammar, reduction_stack, set_t, set_list, i):
        not_set_t = set(grammar.nonterminals) - set_t
        set_temp = set_t.copy()

        explain_text = f"Nonterminals generating terminal words"
        rules = []
        for nt in not_set_t:
            if nt in config['rules']:
                for rule in config['rules'][nt].split(','):
                    found = False
                    for not_t in not_set_t:
                        if not_t not in rule:
                            continue
                        else:
                            found = True
                    if not found:
                        set_t.add(nt)
                        if rule not in rules:
                            rules.append(rule)
                        explain_text += f"\n{nt} = {rule}"

        if set_temp != set_t:
            grammar_text = self.generate_grammar_text(file, rules)
            self.set_to_list(set_t, set_list)
            reduction_text = f"T{i} = {set_list}"
            reduction_stack.push({"grammar_text": grammar_text, "transform_text": reduction_text,
                                  "explain_text": explain_text})
            i_int = ord(i) + 1
            i = chr(i_int)
            self.reduce_phase1(file, config, grammar, reduction_stack, set_t, set_list, i)

    def reduce_phase2(self, file, config, grammar, reduction_stack, set_t, set_d, set_list, i):
        set_temp = set_d.copy()
        rules = []
        for nt in set_temp:
            for rule in config['rules'][nt].split(','):
                for t in set_t:
                    if t in rule and t not in set_d:
                        set_d.add(t)
                        if rule not in rules:
                            rules.append(rule)

        if set_temp != set_d:
            grammar_text = self.generate_grammar_text(file, rules)
            self.set_to_list(set_d, set_list)
            reduction_text = f"D{i} = {set_list}"
            explain_text = f"Nonterminals that can be reached from {grammar.initial_nonterminal}\n{set_d - set_temp}"
            reduction_stack.push({"grammar_text": grammar_text, "transform_text": reduction_text,
                                  "explain_text": explain_text})
            i_int = ord(i) + 1
            i = chr(i_int)
            self.reduce_phase2(file, config, grammar, reduction_stack, set_t, set_d, set_list, i)

    def remove_epsilon_rules(self, file, config, stack_transformation, set_e, set_list, i):
        not_set_e = set(config['input']['nonterminals'].split(',') + config['input']['terminals'].split(',')) - set_e
        set_temp = set_e.copy()

        explain_text = f"Nonterminals that can generate epsilon"
        rules = []
        for nt in config['rules']:
            for rule in config['rules'][nt].split(','):
                if 'epsilon' == rule:
                    set_e.add(nt)
                    if rule not in rules and nt not in set_temp:
                        rules.append(rule)
                        explain_text += f"\n{nt} = {rule}"
                else:
                    found = False
                    for not_e in not_set_e:
                        if not_e not in rule:
                            continue
                        else:
                            found = True
                    if not found:
                        set_e.add(nt)
                        if rule not in rules and nt not in set_temp:
                            rules.append(rule)
                            explain_text += f"\n{nt} = {rule}"

        if set_temp != set_e:
            grammar_text = self.generate_grammar_text(file, rules)
            self.set_to_list(set_e, set_list)
            transformation_text = f"\u2107{i} = {set_list}"
            stack_transformation.push({"grammar_text": grammar_text, "transform_text": transformation_text,
                                       "explain_text": explain_text})
            i_int = ord(i) + 1
            i = chr(i_int)
            self.remove_epsilon_rules(file, config, stack_transformation, set_e, set_list, i)

    def remove_unit_rules(self, file, config, stack_transformation, set_nt, set_list, i):
        set_temp = set_nt.copy()

        explain_text = f"Rules of the form A\u2192B where A,B\u2208\u03A0"
        rules = []
        for nonterminal in set_temp:
            for rule in config['rules'][nonterminal].split(','):
                if rule in list(config['rules']):
                    set_nt.add(rule)
                    if rule not in rules and rule not in set_temp:
                        rules.append(rule)
                        explain_text += f"\n{nonterminal} = {rule}"

        if set_temp != set_nt:
            grammar_text = self.generate_grammar_text(file, rules)
            self.set_to_list(set_nt, set_list)
            transformation_text = f"{set_list[0]}{i} = {set_list}"
            stack_transformation.push({"grammar_text": grammar_text, "transform_text": transformation_text,
                                       "explain_text": explain_text})
            i_int = ord(i) + 1
            i = chr(i_int)
            self.remove_unit_rules(file, config, stack_transformation, set_nt, set_list, i)
        else:
            transformation_text = stack_transformation.data[-1]['transform_text']
            transformation_text += '\n'
            stack_transformation.data[-1]['transform_text'] = transformation_text

    def decompose_rules(self, config, grammar):
        new_rules = {}
        new_nt_count = 1
        for nonterminal, rules in grammar.rules.items():
            for rule in rules:
                if len(rule) > 2:
                    first = 0
                    for i, item in enumerate(rule):
                        if i < len(rule) - 2:
                            new_nt = f'nt{new_nt_count}'
                            sub_rule = [item, new_nt]
                            if nonterminal not in new_rules:
                                new_rules[nonterminal] = []
                                new_rules[nonterminal].append(sub_rule)
                            elif first == 0:
                                new_rules[nonterminal].append(sub_rule)
                                first = 1
                            else:
                                new_nt = f'nt{new_nt_count - 1}'
                                if new_nt not in new_rules:
                                    new_rules[new_nt] = []
                                new_rules[new_nt].append(sub_rule)
                        elif i == len(rule) - 2:
                            new_nt_count -= 1
                            new_nt = f'nt{new_nt_count}'
                            sub_rule = [item, rule[i + 1]]
                            if new_nt not in new_rules:
                                new_rules[new_nt] = []
                            new_rules[new_nt].append(sub_rule)
                        else:
                            new_nt_count -= 1
                        new_nt_count += 1
                else:
                    if nonterminal not in new_rules:
                        new_rules[nonterminal] = []
                    new_rules[nonterminal].append(rule)

        self.rule_dict_to_config(config, new_rules)

    def rule_dict_to_config(self, config, new_rules):
        for nonterminal, rules in new_rules.items():
            nonterminals = config['input']['nonterminals'].split(',')
            if nonterminal not in nonterminals:
                nonterminals.append(nonterminal)
                config.set('input', 'nonterminals', ','.join(nonterminals))

            rule_list = []
            for rule in rules:
                if rule == ['']:
                    rule_list.append('epsilon')
                else:
                    rule_list.append(''.join(rule))

            config.set('rules', nonterminal, ','.join(rule_list))

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
        sentence = new_st.printst()
        return sentence

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
        return root

    def read_config(self, file):
        config = CaseSensitiveConfigParser(interpolation=configparser.ExtendedInterpolation())
        config.read(file)
        return config

    def write_to_config(self, config, file):
        with open(file, 'w', encoding="utf-8") as cf:
            config.write(cf)

    def write_to_config_copy(self, config, file):
        directory, filename = os.path.split(file)
        new_filename = f"{os.path.splitext(filename)[0]}_copy.txt"
        new_file = os.path.join(directory, new_filename)

        with open(new_file, 'w', encoding="utf-8") as cf:
            config.write(cf)

        return new_file

    def check_rule(self, rule, substrings):
        for substring in substrings:
            if substring in rule:
                rule = rule.replace(substring, '')
        return not rule

    def add_value(self, config, val_type, val, file, overwrite=True):
        data = config['input'][val_type].split(',')
        inputs = config['input']['nonterminals'].split(',') + config['input']['terminals'].split(',')
        if val not in inputs and val != '':
            data.append(val)
            new_val = ','.join(data)
            config.set('input', val_type, new_val)
            if overwrite:
                self.write_to_config(config, file)
            else:
                self.write_to_config_copy(config, file)
            return None
        elif val == '':
            return None
        else:
            return f'{val} already exists'

    def get_dependent_rules(self, config, val):
        dlist = []
        for nt in config['rules']:
            for rlist in config['rules'][nt].split(','):
                if val in rlist:
                    print(f'Rule {nt} has dependency on {val}: {"".join(rlist)}')
                    dlist.append("".join(rlist))
        return dlist

    def remove_rule(self, config, val, file, overwrite=True):
        if val in config['rules']:
            config.remove_option('rules', val)
            if overwrite:
                self.write_to_config(config, file)
            else:
                self.write_to_config_copy(config, file)
        for nt in config['rules']:
            if val in config['rules'][nt].split(','):
                data = config['rules'][nt].split(',')
                data.remove(val)
                new_val = ','.join(data)
                config.set('rules', nt, new_val)
                if overwrite:
                    self.write_to_config(config, file)
                else:
                    self.write_to_config_copy(config, file)

    def remove_value(self, config, val_type, val, file, overwrite=True):
        data = config['input'][val_type].split(',')
        if val in data:
            dlist = self.get_dependent_rules(config, val)
            if overwrite:
                for rule in dlist:
                    self.remove_rule(config, rule, file)
                self.remove_rule(config, val, file)
            else:
                for rule in dlist:
                    self.remove_rule(config, rule, file, overwrite)
                self.remove_rule(config, val, file, overwrite)
            data.remove(val)
            new_val = ','.join(data)
            config.set('input', val_type, new_val)
            if overwrite:
                self.write_to_config(config, file)
            else:
                self.write_to_config_copy(config, file)
            return None
        elif val == '':
            return None
        else:
            return f'{val_type} {val} does not exist'

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
                    position = int(input(
                        f"Enter the occurrence of '{initial_nonterminal}' to expand in '{stack.current()}' : \n "))
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


def main(file_variable):
    config = CaseSensitiveConfigParser(interpolation=configparser.ExtendedInterpolation())
    config.read(file_variable)
    grammar = CFG()
    grammar.nonterminals = (config['input']['nonterminals']).split(',')
    grammar.terminals = (config['input']['terminals']).split(',')
    grammar.initial_nonterminal = config['input']['initial_nonterminal']
    grammar.create_class(grammar.nonterminals)
    grammar.create_class(grammar.terminals)
    for nt in grammar.nonterminals:
        nlist = []
        if nt in config['rules']:
            for rule in (config['rules'][nt]).split(','):
                rlist = []
                temp = ''
                if rule == 'epsilon':
                    rlist = ['']
                else:
                    substrings = grammar.nonterminals + grammar.terminals
                    for char in rule:
                        temp += char
                        for substring in substrings:
                            if temp == substring:
                                rlist.append(substring)
                                temp = ''
                                break

                nlist.append(rlist)
            grammar.add_rule(globals()[nt]().attribute, nlist)

    grammar.stack.push(grammar.initial_nonterminal)
    return grammar


if __name__ == "__main__":
    main()
