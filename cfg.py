import re
import configparser
import os
import functions
from copy import deepcopy


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
        self.classes = {}
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

    def generate_grammar_text(self, file, rules, label=False):
        config = self.read_config(file)
        red = "ஆ"
        grammar_text = ''

        for section in config.sections():
            if section == 'rules':
                grammar_text += f"[{section}]\n"
                for nt in config[section]:
                    grammar_text += f"{nt} → "
                    rule_list = config[section][nt].split(',')
                    for index, rule in enumerate(rule_list):
                        if index == len(rule_list) - 1:
                            if nt in rules.keys() and rule in rules[nt]:
                                if rule == 'epsilon':
                                    rule = '\u03B5'
                                grammar_text += f"{red + rule + red}\n"
                            else:
                                if rule == 'epsilon':
                                    rule = '\u03B5'
                                grammar_text += f"{rule}\n"
                        elif label:
                            if nt in rules.keys() and rule in rules[nt]:
                                if rule == 'epsilon':
                                    rule = '\u03B5'
                                grammar_text += f"{red + rule + red} | "
                            else:
                                if rule == 'epsilon':
                                    rule = '\u03B5'
                                grammar_text += f"{rule} | "
                        else:
                            if nt in rules.keys() and rule in rules[nt]:
                                if rule == 'epsilon':
                                    rule = '\u03B5'
                                grammar_text += f"{red + rule + red}|"
                            else:
                                if rule == 'epsilon':
                                    rule = '\u03B5'
                                grammar_text += f"{rule}|"
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
        rules = {}
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
                        if nt not in rules:
                            rules[nt] = set()
                        rules[nt].add(rule)
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
        rules = {}
        for nt in set_temp:
            for rule in config['rules'][nt].split(','):
                for t in set_t:
                    if t in rule and t not in set_d:
                        set_d.add(t)
                        if nt not in rules:
                            rules[nt] = set()
                        rules[nt].add(rule)

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
        rules = {}
        for nt in config['rules']:
            for rule in config['rules'][nt].split(','):
                if 'epsilon' == rule:
                    set_e.add(nt)
                    if nt not in set_temp:
                        if nt not in rules:
                            rules[nt] = set()
                        rules[nt].add(rule)
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
                        if nt not in set_temp:
                            if nt not in rules:
                                rules[nt] = set()
                            rules[nt].add(rule)
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
        rules = {}
        for nonterminal in set_temp:
            for rule in config['rules'][nonterminal].split(','):
                if rule in list(config['rules']):
                    set_nt.add(rule)
                    if rule not in set_temp:
                        if nonterminal not in rules:
                            rules[nonterminal] = set()
                        rules[nonterminal].add(rule)
                        explain_text += f"\n{nonterminal} = {rule}"

        if set_temp != set_nt:
            grammar_text = self.generate_grammar_text(file, rules)
            self.set_to_list(set_nt, set_list)
            transformation_text = f"N({set_list[0]}){i} = {set_list}"
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
                            new_nt = f'<nt{new_nt_count}>'
                            while new_nt in grammar.nonterminals:
                                new_nt_count += 1
                                new_nt = f'<nt{new_nt_count}>'
                            sub_rule = [item, new_nt]
                            if nonterminal not in new_rules:
                                new_rules[nonterminal] = []
                                new_rules[nonterminal].append(sub_rule)
                                first = 1
                            elif first == 0:
                                new_rules[nonterminal].append(sub_rule)
                                first = 1
                            else:
                                if prev_nt not in new_rules:
                                    new_rules[prev_nt] = []
                                new_rules[prev_nt].append(sub_rule)
                        elif i == len(rule) - 2:
                            new_nt_count -= 1
                            sub_rule = [item, rule[i + 1]]
                            if prev_nt not in new_rules:
                                new_rules[prev_nt] = []
                            new_rules[prev_nt].append(sub_rule)
                        else:
                            new_nt_count -= 1

                        prev_nt = new_nt
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

    def gnf_phase1(self, grammar, nonterminal, nt_dict, config, stack_transformation, file):
        rules = grammar.rules[nonterminal]
        temp_rules = deepcopy(rules)
        new_nt_count = 1
        rule_highlight = {}
        explain_text = ''
        for rule_index, rule in enumerate(rules):
            first_item = rule[0]
            if first_item in grammar.nonterminals and nt_dict[first_item] < nt_dict[nonterminal]:
                if nonterminal not in rule_highlight:
                    rule_highlight[nonterminal] = set()
                rule_highlight[nonterminal].add(''.join(rule))
                explain_text = f"{first_item} < {nonterminal}\nReplace the production rule of '{first_item}' at its " \
                               f"place in '{nonterminal}'"

                if len(grammar.rules[first_item]) == 1:
                    rule[0] = grammar.rules[first_item][0][0]
                    break
                else:
                    rule_list = []
                    for item_rules in grammar.rules[first_item]:
                        temp_rule = rule.copy()
                        temp_rule[0:1] = item_rules
                        rule_list.append(temp_rule)

                    new_rule_list = rules[:rule_index] + rule_list + rules[rule_index:]
                    new_rule_list.remove(rule)
                    grammar.rules[nonterminal] = new_rule_list
                    break
            elif first_item in grammar.nonterminals and nt_dict[first_item] == nt_dict[nonterminal]:
                new_nt = f'<gt{new_nt_count}>'
                while new_nt in grammar.nonterminals:
                    new_nt_count += 1
                    new_nt = f'<gt{new_nt_count}>'

                if nonterminal not in rule_highlight:
                    rule_highlight[nonterminal] = set()
                rule_highlight[nonterminal].add(''.join(rule))
                explain_text = f"{first_item} = {nonterminal}, it is the left recursion.\n" \
                               f"Create a new state '{new_nt}' which has the symbols\n" \
                               f"of the left recursive production, once followed by {new_nt}\n" \
                               f"and once without {new_nt},and change that production rule by\n" \
                               f"removing that particular production and adding all other\n" \
                               f"production once followed by {new_nt}.\n"

                temp_rule = rule.copy()
                temp_rule.pop(0)
                temp_rule1 = temp_rule.copy()
                temp_rule1.append(new_nt)
                new_nt_rules = [temp_rule, temp_rule1]

                grammar.nonterminals.append(new_nt)
                grammar.add_rule(new_nt, new_nt_rules)

                rules.pop(rule_index)
                rule_list = []
                for rul in rules:
                    rule_list.append(rul)

                for rul in rules:
                    temp_rul = rul.copy()
                    temp_rul.append(new_nt)
                    rule_list.append(temp_rul)

                grammar.rules[nonterminal] = rule_list
                break

        if temp_rules != grammar.rules[nonterminal]:
            grammar_text = self.generate_grammar_text(file, rule_highlight)
            self.rule_dict_to_config(config, grammar.rules)
            self.write_to_config(config, file)
            transformation_text = functions.generate_rules_text(config)
            stack_transformation.push({"grammar_text": grammar_text, "transform_text": transformation_text,
                                       "explain_text": explain_text})
            self.gnf_phase1(grammar, nonterminal, nt_dict, config, stack_transformation, file)

    def gnf_phase2(self, grammar, nonterminal, config, stack_transformation, file):
        rules = grammar.rules[nonterminal]
        temp_rules = deepcopy(rules)
        rule_highlight = {}
        explain_text = ''
        for rule_index, rule in enumerate(rules):
            first_item = rule[0]
            if first_item in grammar.nonterminals:
                if nonterminal not in rule_highlight:
                    rule_highlight[nonterminal] = set()
                rule_highlight[nonterminal].add(''.join(rule))

                if len(grammar.rules[first_item]) == 1:
                    explain_text = f"{first_item} → {grammar.rules[first_item][0][0]}"
                    rule[0] = grammar.rules[first_item][0][0]
                    break
                else:
                    explain_text = f"Replace {''.join(rule)} with the following rules:"
                    rule_list = []
                    for item_rules in grammar.rules[first_item]:
                        temp_rule = rule.copy()
                        temp_rule[0:1] = item_rules
                        rule_list.append(temp_rule)
                        explain_text += f"\n{''.join(temp_rule)}"

                    new_rule_list = rules[:rule_index] + rule_list + rules[rule_index:]
                    new_rule_list.remove(rule)
                    grammar.rules[nonterminal] = new_rule_list
                    break

        if temp_rules != grammar.rules[nonterminal]:
            grammar_text = self.generate_grammar_text(file, rule_highlight)
            self.rule_dict_to_config(config, grammar.rules)
            self.write_to_config(config, file)
            transformation_text = functions.generate_rules_text(config)
            stack_transformation.push({"grammar_text": grammar_text, "transform_text": transformation_text,
                                       "explain_text": explain_text})
            self.gnf_phase2(grammar, nonterminal, config, stack_transformation, file)

    def compute_first(self, grammar):
        first_dict = {}
        node_dict = {}

        for nonterminal in grammar.nonterminals:
            first_dict[nonterminal] = set()
            node_dict[nonterminal] = set()

        while True:
            updated = False

            for nonterminal, rules in grammar.rules.items():
                for rule in rules:
                    first_item = rule[0]
                    if first_item != '':
                        node_dict[nonterminal].add(first_item)

                    if first_item in grammar.terminals:
                        if first_item not in first_dict[nonterminal]:
                            first_dict[nonterminal].add(first_item)
                            updated = True
                    elif first_item in grammar.nonterminals:
                        for item in first_dict[first_item]:
                            if item != 'epsilon' and item not in first_dict[nonterminal]:
                                first_dict[nonterminal].add(item)
                                updated = True
                        if 'epsilon' in first_dict[first_item]:
                            for ind, item in enumerate(rule[1:]):
                                if item != '':
                                    node_dict[nonterminal].add(item)

                                if item in grammar.terminals:
                                    if item not in first_dict[nonterminal]:
                                        first_dict[nonterminal].add(item)
                                        updated = True
                                    break
                                elif item in grammar.nonterminals:
                                    for i in first_dict[item]:
                                        if i != 'epsilon' and i not in first_dict[nonterminal]:
                                            first_dict[nonterminal].add(i)
                                            updated = True
                                    if 'epsilon' not in first_dict[item]:
                                        break
                                    elif ind + 1 == len(rule) - 1 and 'epsilon' not in first_dict[nonterminal]:
                                        first_dict[nonterminal].add('epsilon')
                                        updated = True
                    else:
                        if 'epsilon' not in first_dict[nonterminal]:
                            first_dict[nonterminal].add('epsilon')
                            updated = True

            if not updated:
                break

        return first_dict, node_dict

    def compute_follow(self, grammar, first_dict):
        follow_dict = {}

        for nonterminal in grammar.nonterminals:
            follow_dict[nonterminal] = set()

        follow_dict[grammar.initial_nonterminal].add('⊣')

        while True:
            updated = False

            for nt in grammar.nonterminals:
                for nonterminal, rules in grammar.rules.items():
                    for rule in rules:
                        for index, item in enumerate(rule):
                            if nt == item:
                                if index == len(rule) - 1:
                                    for item in follow_dict[nonterminal]:
                                        if item not in follow_dict[nt]:
                                            follow_dict[nt].add(item)
                                            updated = True
                                            # break
                                else:
                                    follow_item = rule[index + 1]

                                    if follow_item in grammar.terminals:
                                        if follow_item not in follow_dict[nt]:
                                            follow_dict[nt].add(follow_item)
                                            updated = True
                                    elif follow_item in grammar.nonterminals:
                                        for item in first_dict[follow_item]:
                                            if item != 'epsilon' and item not in follow_dict[nt]:
                                                follow_dict[nt].add(item)
                                                updated = True
                                        if 'epsilon' in first_dict[follow_item]:
                                            if index + 1 == len(rule) - 1:
                                                for item in follow_dict[nonterminal]:
                                                    if item not in follow_dict[nt]:
                                                        follow_dict[nt].add(item)
                                                        updated = True
                                                        # break
                                            else:
                                                for ind, item in enumerate(rule[index + 2:]):
                                                    if item in grammar.terminals:
                                                        if item not in follow_dict[nt]:
                                                            follow_dict[nt].add(item)
                                                            updated = True
                                                        break
                                                    elif item in grammar.nonterminals:
                                                        for i in first_dict[item]:
                                                            if i != 'epsilon' and i not in follow_dict[nt]:
                                                                follow_dict[nt].add(i)
                                                                updated = True
                                                        if 'epsilon' not in first_dict[item]:
                                                            break
                                                        elif index + 2 + ind == len(rule) - 1:
                                                            for i in follow_dict[nonterminal]:
                                                                if i not in follow_dict[nt]:
                                                                    follow_dict[nt].add(i)
                                                                    updated = True

            if not updated:
                break

        return follow_dict

    def compute_first_rules(self, grammar, instance, first_dict, follow_dict):
        nonterminal = instance.name
        first_rules = instance.first_rules

        for rule in grammar.rules[nonterminal]:
            if rule == ['']:
                key = 'epsilon'
            else:
                key = ''.join(rule)
            if key not in first_rules:
                first_rules[key] = set()
            for index, item in enumerate(rule):
                if item in grammar.terminals:
                    first_rules[key].add(item)
                    break
                elif item in grammar.nonterminals:
                    if index == len(rule) - 1 and 'epsilon' in first_dict[item]:
                        first_rules[key].add('epsilon')
                    if 'epsilon' in first_dict[item]:
                        for i in first_dict[item]:
                            if i != 'epsilon':
                                first_rules[key].add(i)
                    else:
                        for i in first_dict[item]:
                            first_rules[key].add(i)
                        break
                else:
                    for t in follow_dict[nonterminal]:
                        first_rules[key].add(t)

    def is_mutually_disjoint(self, instance, stack_transformation, grammar_text):
        nonterminal = instance.name
        first_rules = instance.first_rules

        transformation_text = f"Nonterminal({nonterminal}):\n"

        overlapping_pairs = []
        rules = list(first_rules.keys())
        for i in range(len(rules)):
            key = rules[i]
            keyt = key
            if keyt == 'epsilon':
                keyt = 'ε'
            first_rules_set = first_rules[key]
            if 'epsilon' in first_rules_set:
                first_rules_set.remove('epsilon')
                first_rules_set.add('ε')
            transformation_text += f"\t{first_rules_set}\t{nonterminal} → {keyt}\n"
            for j in range(i + 1, len(rules)):
                rule1, rule2 = rules[i], rules[j]
                set1, set2 = set(first_rules[rule1]), set(first_rules[rule2])
                if set1.intersection(set2):
                    overlapping_pairs.append((rule1, rule2))

        explain_text = ''
        if overlapping_pairs:
            for rule1, rule2 in overlapping_pairs:
                explain_text += f"Rules '{rule1}' and '{rule2}' in {nonterminal} contain common elements:\n" \
                                f"{first_rules[rule1].intersection(first_rules[rule2])}\n\n"

            explain_text += "This is not a LL(1) grammar"
            stack_transformation.push({"grammar_text": grammar_text, "transform_text": transformation_text,
                                       "explain_text": explain_text})
            return True
        else:
            stack_transformation.push({"grammar_text": grammar_text, "transform_text": transformation_text,
                                       "explain_text": explain_text})
            return False

    def ll1_c3(self, instance, stack_transformation, grammar_text, first_dict, follow_dict):
        nonterminal = instance.name
        first_rules = instance.first_rules

        if 'epsilon' in first_dict[nonterminal]:
            temp_dict = {}
            for rule, firsts in first_rules.items():
                if 'epsilon' in firsts:
                    continue
                else:
                    temp_dict[rule] = firsts

            set1 = set(follow_dict[nonterminal])
            for rule, firsts in temp_dict.items():
                set2 = set(firsts)
                if set1.intersection(set2):
                    explain_text = f"FIRST({rule}) has common elements with FOLLOW({nonterminal})\n" \
                                   f"{set1.intersection(set2)}\n\nThis is not a LL(1) grammar"
                    stack_transformation.push({"grammar_text": grammar_text, "transform_text": '',
                                               "explain_text": explain_text})
                    return True
                else:
                    return False

    def compute_closure(self, grammar, items):
        while True:
            updated = False
            for lhs, rhs in list(items.items()):
                for item in rhs:
                    for index, symbol in enumerate(item):
                        if symbol == '.':
                            if index == len(item) - 1:
                                continue
                            else:
                                symbol_after_dot = item[index + 1]
                                if symbol_after_dot in grammar.nonterminals:
                                    for rule in grammar.rules[symbol_after_dot]:
                                        temp_rule = rule.copy()
                                        temp_rule.insert(0, '.')
                                        if symbol_after_dot not in items:
                                            items[symbol_after_dot] = []
                                        if temp_rule not in items[symbol_after_dot]:
                                            items[symbol_after_dot].append(temp_rule)
                                            updated = True
            if not updated:
                break

        return items

    def create_lr0_state(self, states_dict, new_items, item, index, state, new_state, updated):
        present = False
        new_items = {k: sorted(v) for k, v in new_items.items()}
        for key, instance in states_dict.items():
            if new_items.items() == instance.items.items():
                symbol_after_dot = item[index + 1]

                inst = states_dict[state]
                inst.transitions[symbol_after_dot] = key

                present = True
                break

        if not present:
            symbol_after_dot = item[index + 1]

            inst = states_dict[state]
            inst.transitions[symbol_after_dot] = new_state

            class_name = f'I{new_state}'
            cls = type(class_name, (), {'name': class_name, 'items': {}, 'transitions': {}})
            instance = cls()
            states_dict[new_state] = instance
            instance.items = new_items

            new_state += 1
            updated = True

        return updated, new_state

    def compute_lr0_items(self, grammar, states_dict):
        new_state = 1
        reached_states = set()
        while True:
            updated = False
            for state, instance in list(states_dict.items()):
                if state not in reached_states:
                    reached_symbols = set()
                    for lhs, rhs in instance.items.items():
                        for item in rhs:
                            for index, symbol in enumerate(item):
                                if symbol == '.' and index != len(item) - 1:
                                    symbol_after_dot = item[index + 1]
                                    if symbol_after_dot not in reached_symbols:
                                        starting_items = {}
                                        for nonterminal, rules in instance.items.items():
                                            for rule in rules:
                                                for ind, sym in enumerate(rule):
                                                    if ind != len(rule) - 1:
                                                        if sym == '.' and symbol_after_dot == rule[ind + 1]:
                                                            if nonterminal not in starting_items:
                                                                starting_items[nonterminal] = []

                                                            temp_item = rule.copy()
                                                            dot = temp_item.pop(ind)
                                                            temp_item.insert(ind + 1, dot)

                                                            starting_items[nonterminal].append(temp_item)

                                        self.compute_closure(grammar, starting_items)
                                        updated, new_state = self.create_lr0_state(states_dict, starting_items,
                                                                                   item, index, state,
                                                                                   new_state, updated)
                                        reached_symbols.add(symbol_after_dot)

                reached_states.add(state)

            if not updated:
                break

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
            self.classes[class_name] = type(class_name, (), {'name': class_name})

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
            grammar.add_rule(nt, nlist)

    grammar.stack.push(grammar.initial_nonterminal)
    return grammar


if __name__ == "__main__":
    main()
