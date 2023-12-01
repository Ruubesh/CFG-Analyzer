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
    combobox.current(0)


def undo(output_str, input_str, sentential_str, tree_str, execute_e1, grammar, execute_btn, undo_btn, redo_btn):
    redo_btn.config(state="normal")
    sentence, ldata = grammar.stack.undo('S', grammar.nonterminals)
    tree = grammar.stack_tree.undo('T', grammar.nonterminals)
    if ldata == grammar.stack.data[0]:
        undo_btn.config(state="disabled")
        update_label(sentential_str, grammar.stack.data[0])
        update_label(tree_str, grammar.stack.data[0])
        execute(output_str, input_str, sentential_str, tree_str, execute_e1, grammar, ldata, execute_btn, undo_btn, redo_btn)
    else:
        update_label(sentential_str, sentence)
        update_label(tree_str, tree)
        get_nonterminal(output_str, input_str, sentential_str, tree_str, execute_e1, grammar, execute_btn, ldata, undo_btn, redo_btn)


def redo(output_str, input_str, sentential_str, tree_str, execute_e1, grammar, execute_btn, undo_btn, redo_btn):
    undo_btn.config(state="normal")
    sentence, ldata = grammar.stack.redo('S', grammar.nonterminals)
    if ldata == grammar.stack.data[-1]:
        redo_btn.config(state="disabled")
    update_label(sentential_str, sentence)
    update_label(tree_str, grammar.stack_tree.redo('T', grammar.nonterminals))
    get_nonterminal(output_str, input_str, sentential_str, tree_str, execute_e1, grammar, execute_btn, ldata, undo_btn, redo_btn)


def choose_nonterminal(output_str, input_str, sentential_str, tree_str, execute_e1, grammar, execute_btn, undo_btn, redo_btn):
    non_terminal = input_str.get()
    execute(output_str, input_str, sentential_str, tree_str, execute_e1, grammar, non_terminal, execute_btn, undo_btn, redo_btn)


def get_nonterminal(output_str, input_str, sentential_str, tree_str, execute_e1, grammar, execute_btn, ldata, undo_btn, redo_btn):
    val = [elem for elem in grammar.nonterminals if elem in ldata.split(" ")]
    if val:
        if len(val) == 1:
            non_terminal = val[0]
            execute(output_str, input_str, sentential_str, tree_str, execute_e1, grammar, non_terminal, execute_btn, undo_btn, redo_btn)
        else:
            update_label(output_str,
                         f"\nLast expansion : {ldata} \nChoose the next non terminal for expansion: \n ")
            update_options(execute_e1, val)
            execute_btn.config(
                command=lambda: choose_nonterminal(output_str, input_str, sentential_str, tree_str, execute_e1, grammar,
                                                   execute_btn, undo_btn, redo_btn))


def process_data(output_str, input_str, sentential_str, tree_str, execute_e1, grammar, initial_nonterminal, execute_btn, selected_expansion, undo_btn, redo_btn):
    undo_btn.config(state="normal")
    redo_btn.config(state="disabled")
    if grammar.stack.current().count(initial_nonterminal) > 1:
        position = int(input_str.get())
    else:
        position = 1

    if "\u03B5" in selected_expansion:
        selected_expansion[0] = ''

    ldata = grammar.replacer(grammar.stack.current(), initial_nonterminal, " ".join(selected_expansion), position)
    ldata = " ".join(ldata.split())
    grammar.stack.push(ldata)
    sentence = grammar.create_sentential_form(grammar.stack.data, initial_nonterminal, "".join(selected_expansion),
                                              position)
    update_label(sentential_str, sentence)
    grammar.stack_tree.push({initial_nonterminal: selected_expansion, "position": position})
    tree = grammar.build_tree(grammar.stack_tree, grammar.nonterminals)
    update_label(tree_str, tree)

    get_nonterminal(output_str, input_str, sentential_str, tree_str, execute_e1, grammar, execute_btn, ldata, undo_btn, redo_btn)


def get_occurrence(output_str, input_str, sentential_str, tree_str, execute_e1, grammar, initial_nonterminal, execute_btn, undo_btn, redo_btn):
    selected_expansion = input_str.get().split()
    if grammar.stack.current().count(initial_nonterminal) > 1:
        update_label(output_str, f"Enter the occurrence of '{initial_nonterminal}' to expand in '{grammar.stack.current()}' : \n ")
        occurrences = []
        for i in range(1, grammar.stack.current().count(initial_nonterminal) + 1):
            occurrences.append(i)
        update_options(execute_e1, occurrences)
        execute_btn.config(command=lambda: process_data(output_str, input_str, sentential_str, tree_str, execute_e1, grammar, initial_nonterminal, execute_btn, selected_expansion, undo_btn, redo_btn))
    else:
        process_data(output_str, input_str, sentential_str, tree_str, execute_e1, grammar, initial_nonterminal, execute_btn, selected_expansion, undo_btn, redo_btn)


def execute(output_str, input_str, sentential_str, tree_str, execute_e1, grammar, initial_nonterminal, execute_btn, undo_btn, redo_btn):
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

    execute_btn.config(command=lambda: get_occurrence(output_str, input_str, sentential_str, tree_str, execute_e1, grammar, initial_nonterminal, execute_btn, undo_btn, redo_btn))
