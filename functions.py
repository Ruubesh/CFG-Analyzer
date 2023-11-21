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

