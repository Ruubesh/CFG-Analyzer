from tkinter import filedialog
from cfg import CFG


def open_file(file_variable):
    filename = filedialog.askopenfilename(
        initialdir="/Users/ruube/PycharmProjects/Thesis",
        title="Select A File",
        filetypes=(("Text files", "*.txt"), ("All files", "*.*"))
    )

    file_variable.set(filename)


def submit(file, grammar_str):
    with open(file, 'r') as f:
        grammar = f.read()
        grammar_str.set(grammar)


def add(file, val_type, val, grammar_str):
    config = CFG().read_config(file)
    if val_type == 'rules':
        CFG().add_rule_to_config(config, val)
    else:
        CFG().add_value(config, val_type, val)

    submit(file, grammar_str)


def remove(file, val_type, val, grammar_str):
    config = CFG().read_config(file)
    if val_type == 'rules':
        CFG().remove_rule(config, val)
    else:
        CFG().remove_value(config, val_type, val)

    submit(file, grammar_str)


def update_label(label, text):
    label.set(text)


def update_options(combobox, options):
    combobox['values'] = options


def execute(output_str, input_str, sentential_str, tree_str, execute_e1, grammar, initial_nonterminal):
    if initial_nonterminal not in grammar.rules:
        return initial_nonterminal

    update_label(output_str, f"Choose the next expansion for '{initial_nonterminal}':")
    options = []
    for i, option in enumerate(grammar.rules[initial_nonterminal], 1):
        if option[0] == '':
            options.append("\u03B5")
        else:
            options.append(' '.join(option))

    update_options(execute_e1, options)

    selected_expansion = input_str.get().split()

    if grammar.stack.current().count(initial_nonterminal) > 1:
        update_label(output_str, f"Enter the occurrence of '{initial_nonterminal}' to expand in '{grammar.stack.current()}' : \n ")
        occurrences = []
        for i in range(1, grammar.stack.current().count(initial_nonterminal) + 1):
            occurrences.append(i)
        update_options(execute_e1, occurrences)
        position = int(input_str.get())
    else:
        position = 1

    ldata = grammar.replacer(grammar.stack.current(), initial_nonterminal, " ".join(selected_expansion), position)
    ldata = " ".join(ldata.split())
    grammar.stack.push(ldata)
    sentence = grammar.create_sentential_form(grammar.stack.data, initial_nonterminal, "".join(selected_expansion), position)
    update_label(sentential_str, sentence)
    grammar.stack_tree.push({initial_nonterminal: selected_expansion, "position": position})
    tree = grammar.build_tree(grammar.stack_tree, grammar.nonterminals)
    update_label(tree_str, tree)
    non_terminal = ''
    val = [elem for elem in grammar.nonterminals if elem in ldata.split(" ")]
    if val:
        if len(val) == 1:
            non_terminal = val[0]
        else:
            update_label(output_str, f"\nLast expansion : {ldata} \nChoose the next non terminal for expansion or 'u' to undo or 'r' to redo : \n ")
            update_options(execute_e1, val)
            non_terminal = input_str.get()

    execute(output_str, input_str, sentential_str, tree_str, execute_e1, grammar, non_terminal)

    # return stack.data[-1]
