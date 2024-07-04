import copy
from tkinter import filedialog, ttk
from cfg import CFG, main, Stack, Transform, LLParser, LRParser
import tkinter as tk
from itertools import combinations
import os
from tooltips import CreateToolTip
import tempfile
from recognizer import Recognizer


def update_scrollregion(canvas):
    canvas.configure(scrollregion=canvas.bbox("all"))


def create_text_scrollbar(text_widget):
    v_scrollbar = ttk.Scrollbar(text_widget, orient=tk.VERTICAL, command=text_widget.yview)
    v_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    h_scrollbar = ttk.Scrollbar(text_widget, orient=tk.HORIZONTAL, command=text_widget.xview)
    h_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)

    text_widget.config(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)


def create_scrollbars(frame):
    vertical_scrollbar = ttk.Scrollbar(master=frame, orient="vertical")
    horizontal_scrollbar = ttk.Scrollbar(master=frame, orient="horizontal")
    canvas = tk.Canvas(master=frame, yscrollcommand=vertical_scrollbar.set, xscrollcommand=horizontal_scrollbar.set)
    vertical_scrollbar.config(command=canvas.yview)
    horizontal_scrollbar.config(command=canvas.xview)
    vertical_scrollbar.pack(side="right", fill="y")
    horizontal_scrollbar.pack(side="bottom", fill="x")
    canvas.pack(fill="both", expand=1)
    canvas.bind("<MouseWheel>", lambda event: canvas.yview_scroll(int(-1 * (event.delta / 120)), "units"))
    canvas.bind("<Control MouseWheel>", lambda event: canvas.xview_scroll(int(-1 * (event.delta / 120)), "units"))

    return canvas


def update_label(label, text):
    label.set(text)


def update_options(combobox, options):
    combobox['values'] = options
    combobox.current(0)


def open_files(listbox, listbox_items, file_error, listbox_dict):
    file_error.config(text='')

    # Get the current working directory
    initial_dir = os.getcwd()

    filenames = filedialog.askopenfilenames(
        initialdir=initial_dir,
        title="Select A File",
        filetypes=(("Text files", "*.txt"), ("All files", "*.*"))
    )

    for filename in filenames:
        directory, keytype = os.path.split(filename)
        key = os.path.splitext(keytype)[0]
        listbox_dict[key] = filename

        if key not in listbox.get(0, tk.END):
            listbox.insert(tk.END, key)
            listbox_items.append(filename)


def remove_file(listbox, listbox_items, file_error, listbox_dict):
    file_error.config(text='')
    selected_indices = listbox.curselection()
    if selected_indices:
        for index in reversed(selected_indices):
            listbox.delete(index)
            key = [k for k, v in listbox_dict.items() if v == listbox_items[index]]
            key = ''.join(key)
            del listbox_dict[key]
            del listbox_items[index]
    else:
        file_error.config(text='Please select one or more files to remove')


def read_file(file):
    with open(file, 'r') as f:
        text = f.read()
        return text


def on_pressing_right(grammar_text_widget, transform_str, explain_str, stack_transformation, index, back_btn,
                      forward_btn, transform_canvas):
    if index.get() < len(stack_transformation.data) - 1:
        index.set(index.get() + 1)
        back_btn.config(state=tk.NORMAL)

        grammar_text, transform_text, explain_text = get_stack_transformation_data(index, stack_transformation)

        display_popup_grammar(grammar_text_widget, grammar_text)

        new_transform_text = transform_str.get()
        new_transform_text += f"\n{transform_text}"
        update_label(transform_str, new_transform_text)
        update_vertical_scrollregion(transform_canvas, transform_str)

        update_label(explain_str, explain_text)

        if index.get() == len(stack_transformation.data) - 1:
            forward_btn.config(state=tk.DISABLED)


def on_pressing_left(grammar_text_widget, transform_str, explain_str, stack_transformation, index, back_btn,
                     forward_btn, transform_canvas):
    if index.get() > 0:
        index.set(index.get() - 1)
        forward_btn.config(state=tk.NORMAL)

        grammar_text, transform_text, explain_text = get_stack_transformation_data(index, stack_transformation)

        display_popup_grammar(grammar_text_widget, grammar_text)

        if index.get() == 0:
            back_btn.config(state=tk.DISABLED)
            transform_text = stack_transformation.data[0]["transform_text"]
        else:
            transform_text = stack_transformation.data[0]["transform_text"]
            for i in range(1, index.get() + 1):
                transform_text += f'\n{stack_transformation.data[i]["transform_text"]}'

        update_label(transform_str, transform_text)
        update_vertical_scrollregion(transform_canvas, transform_str)

        update_label(explain_str, explain_text)


def display_popup_grammar(grammar_text_widget, grammar_text):
    grammar_text_widget.config(state=tk.NORMAL)
    grammar_text_widget.delete("1.0", tk.END)
    grammar_text_widget.insert("1.0", grammar_text)
    highlight_text(grammar_text_widget)
    grammar_text_widget.config(state=tk.DISABLED)


def get_stack_transformation_data(index, stack_transformation):
    grammar_text = stack_transformation.data[index.get()]["grammar_text"]
    transform_text = stack_transformation.data[index.get()]["transform_text"]
    explain_text = stack_transformation.data[index.get()]["explain_text"]

    return grammar_text, transform_text, explain_text


def highlight_text(text_widget):
    start_index = "1.0"
    start_occurrence = 0
    end_occurrence = 1
    line_set = set()
    indices = []
    while True:
        start_index = text_widget.search("ஆ", start_index, stopindex="end", count="1")
        if not start_index:
            break
        line, column = map(int, start_index.split('.'))

        if line in line_set:
            start_occurrence += 1
            end_occurrence += 1
        else:
            line_set.add(line)
            start_occurrence = 0
            end_occurrence = 1

        new_column = column - 2 * start_occurrence
        new_start_index = f"{line}.{new_column}"

        end_index = text_widget.search("ஆ", f"{start_index}+1c", stopindex="end", count="1")
        if not end_index:
            break
        line, column = map(int, end_index.split('.'))

        new_column = column - 2 * end_occurrence
        new_end_index = f"{line}.{new_column}"

        start_index = f"{end_index}+1c"
        indices.append((new_start_index, new_end_index))

    text_content = text_widget.get("1.0", "end")
    modified_text = text_content.replace("ஆ", "")
    text_widget.delete("1.0", "end")
    text_widget.insert("1.0", modified_text)

    for index in indices:
        text_widget.tag_add("highlight", index[0], f"{index[1]}+1c")


def save_as_transformed_grammar(config, popup_window, listbox_items, filename):
    # Get the current working directory
    initial_dir = os.getcwd()

    file = filedialog.asksaveasfilename(parent=popup_window,
                                        defaultextension=".*",
                                        initialdir=initial_dir,
                                        initialfile=filename,
                                        title="Save File",
                                        filetypes=(("Text files", "*.txt"), ("All files", "*.*"))
                                        )

    if file:
        CFG().write_to_config(config, file)
        listbox_items.append(file)


def on_popup_window_close(window, config, file):
    temp_file = CFG().write_to_config_copy(config, file)
    os.remove(temp_file)
    window.destroy()


def create_popup_window(window, stack_transformation, config, file, win_title, listbox_items):
    popup_window = tk.Toplevel(window)
    popup_window.protocol("WM_DELETE_WINDOW", lambda: on_popup_window_close(popup_window, config, file))
    popup_window.title(win_title)
    popup_window.geometry(f'{window.winfo_screenwidth() - 16}x{window.winfo_screenheight() - 80}+0+0')
    popup_window.focus()

    button_frame = tk.Frame(master=popup_window)
    button_frame.pack(fill=tk.X)
    left_button_frame = tk.Frame(master=button_frame)
    left_button_frame.place(x=40, y=15)
    close_btn = tk.Button(master=left_button_frame, text="Close",
                          command=lambda: on_popup_window_close(popup_window, config, file))
    close_btn.pack()
    center_button_frame = tk.Frame(master=button_frame)
    center_button_frame.pack()
    back_btn = tk.Button(master=center_button_frame, text="<--",
                         command=lambda: on_pressing_left(grammar_text_widget, transform_str, explain_str,
                                                          stack_transformation, index, back_btn, forward_btn,
                                                          transform_canvas),
                         state=tk.DISABLED)
    back_btn.pack(side=tk.LEFT, padx=20)
    save_btn = tk.Button(master=center_button_frame, text="Save",
                         command=lambda: save_as_transformed_grammar(config, popup_window, listbox_items, ''))
    save_btn.pack(side=tk.LEFT, padx=20, pady=15)
    forward_btn = tk.Button(master=center_button_frame, text="-->",
                            command=lambda: on_pressing_right(grammar_text_widget, transform_str, explain_str,
                                                              stack_transformation, index, back_btn, forward_btn,
                                                              transform_canvas))
    forward_btn.pack(side=tk.LEFT, padx=20)

    grammar_frame = tk.LabelFrame(master=popup_window, text="Grammar", width=popup_window.winfo_width() / 3)
    grammar_frame.pack(side="left", fill="both", expand=1)
    grammar_frame.pack_propagate(0)
    grammar_text_widget = tk.Text(master=grammar_frame, wrap=tk.NONE, width=15, bg="#d3d3d3")
    grammar_text_widget.pack(fill="both", expand=1)

    create_text_scrollbar(grammar_text_widget)

    transform_frame = tk.LabelFrame(master=popup_window, text="Transformation Steps",
                                    width=popup_window.winfo_width() / 3)
    transform_frame.pack(side="left", fill="both", expand=1)
    transform_frame.pack_propagate(0)
    transform_str = tk.StringVar()

    transform_canvas = create_scrollbars(transform_frame)

    explain_frame = tk.LabelFrame(master=popup_window, text="Explanation", width=popup_window.winfo_width() / 3)
    explain_frame.pack(side="left", fill="both", expand=1)
    explain_frame.pack_propagate(0)
    explain_str = tk.StringVar()
    explain_label = tk.Label(master=explain_frame, textvariable=explain_str, justify="left")
    explain_label.pack()

    index = tk.IntVar()
    index.set(0)

    grammar_text, transform_text, explain_text = get_stack_transformation_data(index, stack_transformation)

    grammar_text_widget.insert("1.0", grammar_text)
    grammar_text_widget.tag_configure("highlight", foreground="red")
    highlight_text(grammar_text_widget)
    grammar_text_widget.config(state=tk.DISABLED)
    update_label(transform_str, transform_text)
    update_vertical_scrollregion(transform_canvas, transform_str)
    update_label(explain_str, explain_text)

    popup_window.bind("<Right>", lambda event: on_pressing_right(grammar_text_widget, transform_str, explain_str,
                                                                 stack_transformation, index, back_btn, forward_btn,
                                                                 transform_canvas))
    popup_window.bind("<Left>", lambda event: on_pressing_left(grammar_text_widget, transform_str, explain_str,
                                                               stack_transformation, index, back_btn, forward_btn,
                                                               transform_canvas))

    # Tooltips
    CreateToolTip(close_btn, "Close this window")
    CreateToolTip(back_btn, "Previous step")
    CreateToolTip(forward_btn, "Next step")
    CreateToolTip(save_btn, "Save the transformed grammar")


def generate_rules_text(config):
    text = '\n'
    for nt in config['rules']:
        rules = config['rules'][nt].split(',')
        formatted_rules = ' | '.join(rules)
        text += f"{nt} → {formatted_rules}\n"

    return text


def update_reduction_rules(config, grammar, file_variable, set_transformation, stack_transformation):
    not_set_t = set(grammar.nonterminals) - set_transformation
    for not_t in not_set_t:
        CFG().remove_value(config, 'nonterminals', not_t, file_variable, overwrite=False)

    text = generate_rules_text(config)

    grammar_text = CFG().generate_grammar_text(file_variable, {})
    explain_text = f"Remove all nonterminals that are not in\n" \
                   f"{set_transformation}\n" \
                   f"together with all rules where they occur\n" \
                   f"Removed Nonterminals: {not_set_t}"
    stack_transformation.push({"grammar_text": grammar_text, "transform_text": text, "explain_text": explain_text})


def reduce(window, file_variable, listbox_items):
    stack_transformation = Stack()
    grammar = main(file_variable)
    config = CFG().read_config(file_variable)

    set_t = set()
    set_list = []
    Transform().reduce_phase1(file_variable, config, grammar, stack_transformation, set_t, set_list, '\u2080')

    grammar_text = CFG().generate_grammar_text(file_variable, {})
    transform_text = f"\nT = {set_list}"
    stack_transformation.push({"grammar_text": grammar_text, "transform_text": transform_text, "explain_text": ''})

    update_reduction_rules(config, grammar, file_variable, set_t, stack_transformation)

    set_list.clear()
    set_list.append(grammar.initial_nonterminal)
    set_d = set()
    set_d.add(grammar.initial_nonterminal)
    grammar_text = CFG().generate_grammar_text(file_variable, {})
    reduction_text = f"D\u2080 = {set_list}"
    explain_text = f"{grammar.initial_nonterminal} is the initial nonterminal"
    stack_transformation.push({"grammar_text": grammar_text, "transform_text": reduction_text,
                               "explain_text": explain_text})
    Transform().reduce_phase2(file_variable, config, grammar, stack_transformation, set_t, set_d, set_list, '\u2081')

    transform_text = f"\nD = {set_list}"
    stack_transformation.push({"grammar_text": grammar_text, "transform_text": transform_text, "explain_text": ''})

    update_reduction_rules(config, grammar, file_variable, set_d, stack_transformation)

    create_popup_window(window, stack_transformation, config, file_variable, 'Reduction', listbox_items)


def remove_epsilon_rules(listbox_items, window, file_variable, other_stack=None, other_transform=False):
    grammar_text = CFG().generate_grammar_text(file_variable, {})
    if other_transform:
        stack_transformation = other_stack
        transform_text = 'Step 2:\n'
        explain_text = "Remove epsilon rules"
        stack_transformation.push({"grammar_text": grammar_text, "transform_text": transform_text,
                                   "explain_text": explain_text})
    else:
        stack_transformation = Stack()

    config = CFG().read_config(file_variable)
    grammar = main(file_variable)

    set_e = set()
    set_list = []
    Transform().remove_epsilon_rules(file_variable, config, stack_transformation, set_e, set_list, '\u2080')

    transform_text = f"\n\u2107 = {set_list}"
    explain_text = f"Nonterminals {set_list} can generate epsilon"
    stack_transformation.push(
        {"grammar_text": grammar_text, "transform_text": transform_text, "explain_text": explain_text})

    new_rules = {}
    for nonterminal, production_rules in grammar.rules.items():
        for rule in production_rules:
            indices = []
            for index, nt in enumerate(rule):
                if nt in set_e:
                    indices.append(index)
            if nonterminal not in new_rules:
                new_rules[nonterminal] = []
            if tuple(rule) not in new_rules[nonterminal]:
                new_rules[nonterminal].append(tuple(rule))
            for r in range(1, len(indices) + 1):
                combos = combinations(indices, r)
                for combo in combos:
                    temp_rule = rule.copy()
                    for ind in sorted(combo, reverse=True):
                        temp_rule.pop(ind)
                    if tuple(temp_rule) not in new_rules[nonterminal]:
                        new_rules[nonterminal].append(tuple(temp_rule))
        new_production_rule = []
        for new_rule in new_rules[nonterminal]:
            new_production_rule.append(''.join(new_rule))
        new_production_rules = [item for item in new_production_rule if item != '']
        config.set('rules', nonterminal, ','.join(new_production_rules))

    if grammar.initial_nonterminal in set_e:
        new_init_nt = 'Φ'
        CFG().add_value(config, 'nonterminals', new_init_nt, file_variable, overwrite=False)
        new_init_rule = [grammar.initial_nonterminal, 'epsilon']
        config.set('input', 'initial_nonterminal', new_init_nt)
        config.set('rules', new_init_nt, ','.join(new_init_rule))
    elif other_transform:
        for nonterminal, production_rules in grammar.rules.items():
            for rule in production_rules:
                if grammar.initial_nonterminal in rule:
                    new_init_nt = 'Φ'
                    CFG().add_value(config, 'nonterminals', new_init_nt, file_variable)
                    new_init_rule = [grammar.initial_nonterminal]
                    config.set('input', 'initial_nonterminal', new_init_nt)
                    config.set('rules', new_init_nt, ','.join(new_init_rule))
                    break

    transformation_text = generate_rules_text(config)
    explain_text = f"Remove all epsilon rules and replace every other A --> \u03B1 \nwith a set of rules obtained by " \
                   f"all possible rules of the form A --> \u03B1\u2032 \nwhere \u03B1\u2032 is obtained from \u03B1 by " \
                   f"possible ommitting of \n(some) occurrences of nonterminals from set\n" \
                   f"{set_e}"
    stack_transformation.push({"grammar_text": grammar_text, "transform_text": transformation_text,
                               "explain_text": explain_text})

    if other_transform:
        CFG().write_to_config(config, file_variable)
    else:
        CFG().write_to_config_copy(config, file_variable)

        create_popup_window(window, stack_transformation, config, file_variable, 'Remove Epsilon Rules', listbox_items)


def remove_unit_rules(listbox_items, window, file, other_stack=None, other_transform=False):
    grammar_text = CFG().generate_grammar_text(file, {})
    config = CFG().read_config(file)
    epsilon = False
    if other_transform:
        stack_transformation = other_stack
        transform_text = 'Step 3:\n'
        explain_text = "Remove unit rules"
        stack_transformation.push({"grammar_text": grammar_text, "transform_text": transform_text,
                                   "explain_text": explain_text})
    else:
        stack_transformation = Stack()
        for nonterminal in config['rules']:
            for rule in config['rules'][nonterminal].split(','):
                if rule == 'epsilon':
                    file = CFG().write_to_config_copy(config, file)
                    remove_epsilon_rules(listbox_items, window, file, Stack(), other_transform=True)
                    epsilon = True

        config = CFG().read_config(file)
        transform_text = generate_rules_text(config)
        explain_text = "Grammar after removing epsilon rules"
        stack_transformation.push({"grammar_text": grammar_text, "transform_text": transform_text,
                                   "explain_text": explain_text})

    grammar_text = CFG().generate_grammar_text(file, {})
    transform_sets = {}
    for nonterminal in config['rules']:
        set_nt = set()
        set_list = []

        set_nt.add(nonterminal)
        set_list.append(nonterminal)
        transformation_text = f"N({nonterminal})\u2080 = {set_list}"
        stack_transformation.push({"grammar_text": grammar_text, "transform_text": transformation_text,
                                   "explain_text": ''})
        Transform().remove_unit_rules(file, config, stack_transformation, set_nt, set_list, '\u2081')

        transform_sets[nonterminal] = set_list

    transformation_text = ''
    for key, value in transform_sets.items():
        transformation_text += f"N({key}) = {value}\n"

        new_rules = []
        for val in value:
            for rule in config['rules'][val].split(','):
                if rule not in list(config['rules']) and rule not in new_rules:
                    new_rules.append(rule)
        config.set('rules', key, ','.join(new_rules))

    explain_text = "For each A\u2208\u03A0 compute the set of all nonterminals\n" \
                   "that can be obtained from A by using only unit rules, i.e.,\nA = {B\u2208\u03A0 | A =>\u002A B}"
    stack_transformation.push({"grammar_text": grammar_text, "transform_text": transformation_text,
                               "explain_text": explain_text})

    transformation_text = generate_rules_text(config)
    explain_text = "Construct CFG G\u2032 = (Π, Σ, S, P′) where P′ consist of rules of the form\n" \
                   "A → β where A ∈ Π, β is not a single nonterminal,\n" \
                   "and (B → β) ∈ P for some B ∈ set A"
    stack_transformation.push({"grammar_text": grammar_text, "transform_text": transformation_text,
                               "explain_text": explain_text})

    if other_transform:
        CFG().write_to_config(config, file)
    elif epsilon:
        os.remove(file)
        create_popup_window(window, stack_transformation, config, file, 'Remove Unit Rules', listbox_items)
    else:
        CFG().write_to_config_copy(config, file)

        create_popup_window(window, stack_transformation, config, file, 'Remove Unit Rules', listbox_items)


def chomsky_normal_form(window, file, listbox_items):
    stack_transformation = Stack()
    config = CFG().read_config(file)
    grammar = main(file)

    # Step 1
    Transform().decompose_rules(config, grammar)

    grammar_text = CFG().generate_grammar_text(file, {})
    transformation_text = 'Step 1:'
    stack_transformation.push({"grammar_text": grammar_text, "transform_text": transformation_text,
                               "explain_text": 'Decompose rules'})

    transformation_text = generate_rules_text(config)
    explain_text = "Decompose each rule A → α where |α| ≥ 3 into a sequence of rules\n" \
                   "where each right-hand size has length 2"
    stack_transformation.push({"grammar_text": grammar_text, "transform_text": transformation_text,
                               "explain_text": explain_text})

    copy_file = CFG().write_to_config_copy(config, file)

    # Step 2
    remove_epsilon_rules(listbox_items, window, copy_file, stack_transformation, other_transform=True)

    # Step 3
    remove_unit_rules(listbox_items, window, copy_file, stack_transformation, other_transform=True)

    # Step 4
    config = CFG().read_config(copy_file)
    grammar = main(copy_file)

    new_rules = {}
    new_nt_count = 1
    replaced = set()
    for nonterminal, rules in grammar.rules.items():
        for rule in rules:
            if len(rule) == 2:
                terminals = config['input']['terminals'].split(',')
                for terminal in terminals:
                    for index in range(len(rule)):
                        if rule[index] == terminal:
                            new_nt = f'<et{new_nt_count}>'
                            while new_nt in grammar.nonterminals:
                                new_nt_count += 1
                                new_nt = f'<et{new_nt_count}>'
                            for key, value in new_rules.items():
                                if terminal in value:
                                    rule[index] = key
                            if terminal not in replaced:
                                rule[index] = new_nt
                                new_rules[new_nt] = [terminal]
                                replaced.add(terminal)
                                new_nt_count += 1

    for nonterminal, rule in new_rules.items():
        grammar.add_rule(nonterminal, [rule])

    CFG().rule_dict_to_config(config, grammar.rules)

    grammar_text = CFG().generate_grammar_text(copy_file, {})
    transformation_text = 'Step 4:'
    stack_transformation.push({"grammar_text": grammar_text, "transform_text": transformation_text,
                               "explain_text": ''})

    transformation_text = generate_rules_text(config)
    explain_text = "For each terminal 'a' occurring on the right-hand size\n" \
                   "of some rule A → α where |α| = 2 introduce a new nonterminal N\u2090,\n" \
                   "replace occurrences of 'a' on such right-hand sides\n" \
                   "with N\u2090, and add N\u2090 → a as a new rule"
    stack_transformation.push({"grammar_text": grammar_text, "transform_text": transformation_text,
                               "explain_text": explain_text})

    CFG().write_to_config(config, copy_file)

    create_popup_window(window, stack_transformation, config, file, 'Chomsky Normal Form', listbox_items)


def greibach_normal_form(window, file, listbox_items):
    config = CFG().read_config(file)
    copy_file = CFG().write_to_config_copy(config, file)
    stack_transformation = Stack()

    # Remove Epsilon Rules
    remove_epsilon_rules(listbox_items, window, copy_file, Stack(), other_transform=True)

    # Remove Unit Rules
    remove_unit_rules(listbox_items, window, copy_file, Stack(), other_transform=True)

    # Step 1
    config = CFG().read_config(copy_file)

    grammar_text = CFG().generate_grammar_text(file, {})
    transformation_text = 'Step 1:'
    explain_text = "Remove unit rules and epsilon rules"
    stack_transformation.push({"grammar_text": grammar_text, "transform_text": transformation_text,
                               "explain_text": explain_text})

    transformation_text = generate_rules_text(config)
    explain_text = "Grammar after removing unit rules and epsilon rules"
    stack_transformation.push({"grammar_text": grammar_text, "transform_text": transformation_text,
                               "explain_text": explain_text})

    # Step 2
    grammar = main(copy_file)

    grammar_text = CFG().generate_grammar_text(copy_file, {})
    transformation_text = 'Step 2:'
    explain_text = "Assign integer values to nonterminal symbols from 1...N in same sequence\n" \
                   "and reorder the rules in ascending order"
    stack_transformation.push({"grammar_text": grammar_text, "transform_text": transformation_text,
                               "explain_text": explain_text})

    new_config = CFG().read_config(copy_file)
    nt_dict = {}
    i = 1
    for nonterminal, production_rules in grammar.rules.items():
        if nonterminal not in nt_dict:
            if nonterminal in new_config['rules']:
                new_config.remove_option('rules', nonterminal)

            new_config.set('rules', nonterminal, config['rules'][nonterminal])
            nt_dict[nonterminal] = i
            explain_text += f"\n{nonterminal} = {i}"
            i += 1
        for production_rule in production_rules:
            for item in production_rule:
                if item in grammar.nonterminals and item not in nt_dict:
                    if item in new_config['rules']:
                        new_config.remove_option('rules', item)

                    new_config.set('rules', item, config['rules'][item])
                    nt_dict[item] = i
                    explain_text += f"\n{item} = {i}"
                    i += 1

    config = new_config
    transformation_text = generate_rules_text(config)
    stack_transformation.push({"grammar_text": grammar_text, "transform_text": transformation_text,
                               "explain_text": explain_text})

    # Step 3
    CFG().write_to_config(config, copy_file)
    grammar_text = CFG().generate_grammar_text(copy_file, {})
    transformation_text = 'Step 3:'
    explain_text = "Check for every production rule if RHS has first symbol\n" \
                   "as non terminal say Aj for the production of Ai,\n" \
                   "it is mandatory that i should be less than j.\n" \
                   "Not great and not even equal.\n\n" \
                   "If i>j then replace the production rule of Aj at its place in Ai.\n\n" \
                   "If i=j, it is the left recursion. Create a new state Z\n" \
                   "which has the symbols of the left recursive production,\n" \
                   "once followed by Z and once without Z,\n" \
                   "and change that production rule by removing that particular production\n" \
                   "and adding all other production once followed by Z."
    stack_transformation.push({"grammar_text": grammar_text, "transform_text": transformation_text,
                               "explain_text": explain_text})

    for nonterminal in nt_dict.keys():
        Transform().gnf_phase1(grammar, nonterminal, nt_dict, config, stack_transformation, copy_file)

    # Step 4
    grammar_text = CFG().generate_grammar_text(copy_file, {})
    transformation_text = 'Step 4:'
    explain_text = "Replace the production to the form of either\n" \
                   "Ai → x (any single terminal symbol)\n" \
                   "OR\n" \
                   "Ai → xX (any single terminal followed by any number of non terminals)"
    stack_transformation.push({"grammar_text": grammar_text, "transform_text": transformation_text,
                               "explain_text": explain_text})

    for nonterminal in grammar.rules.keys():
        Transform().gnf_phase2(grammar, nonterminal, config, stack_transformation, copy_file)

    explain_text = stack_transformation.data[-1]["explain_text"]
    explain_text += "\n\nThe grammar is now in Greibach Normal Form"
    stack_transformation.data[-1]["explain_text"] = explain_text

    CFG().write_to_config_copy(config, file)

    create_popup_window(window, stack_transformation, config, file, 'Greibach Normal Form', listbox_items)


def compute_first_and_follow(window, file):
    stack_transformation = Stack()
    config = CFG().read_config(file)
    grammar = main(file)

    # compute_first
    first_dict, node_dict = LLParser().compute_first(grammar)

    # nodes and edges
    transformation_text = ''
    for node, edges in node_dict.items():
        transformation_text += f"Node({node}):\n"
        for edge in edges:
            transformation_text += f"\t→{edge}\n"

    grammar_text = CFG().generate_grammar_text(file, {})
    explain_text = "Nodes and their respective edges to other nodes"
    stack_transformation.push({"grammar_text": grammar_text, "transform_text": transformation_text,
                               "explain_text": explain_text})

    # FIRST
    transformation_text = '\n'
    for nonterminal, first_set in first_dict.items():
        f_set = first_set.copy()
        if 'epsilon' in f_set:
            f_set.remove('epsilon')
            f_set.add('ε')
        transformation_text += f"FIRST({nonterminal}) = {f_set}\n"

    explain_text = 'FIRSTs of the nonterminals in the grammar'
    stack_transformation.push({"grammar_text": grammar_text, "transform_text": transformation_text,
                               "explain_text": explain_text})

    # compute_follow
    follow_dict = LLParser().compute_follow(grammar, first_dict)

    # FOLLOW
    transformation_text = '\n'
    for nonterminal, follow_set in follow_dict.items():
        transformation_text += f"FOLLOW({nonterminal}) = {follow_set}\n"

    explain_text = 'FOLLOWs of the nonterminals in the grammar'
    stack_transformation.push({"grammar_text": grammar_text, "transform_text": transformation_text,
                               "explain_text": explain_text})

    create_popup_window(window, stack_transformation, config, file, 'First and Follow', None)


def is_ll1(window, file):
    grammar = main(file)
    stack_transformation = Stack()
    config = CFG().read_config(file)

    first_dict, _ = LLParser().compute_first(grammar)
    follow_dict = LLParser().compute_follow(grammar, first_dict)

    grammar_text = CFG().generate_grammar_text(file, {})

    # display first and follow
    transformation_text = '\n'
    for nonterminal, first_set in first_dict.items():
        f_set = first_set.copy()
        if 'epsilon' in f_set:
            f_set.remove('epsilon')
            f_set.add('ε')
        transformation_text += f"FIRST({nonterminal}) = {f_set}\n"

    explain_text = 'FIRSTs of the nonterminals in the grammar'
    stack_transformation.push({"grammar_text": grammar_text, "transform_text": transformation_text,
                               "explain_text": explain_text})

    transformation_text = '\n'
    for nonterminal, follow_set in follow_dict.items():
        transformation_text += f"FOLLOW({nonterminal}) = {follow_set}\n"

    explain_text = 'FOLLOWs of the nonterminals in the grammar'
    stack_transformation.push({"grammar_text": grammar_text, "transform_text": transformation_text,
                               "explain_text": explain_text})

    instance_dict = {}
    for name, cls in grammar.classes.items():
        if name in grammar.nonterminals:
            instance = cls()
            instance.first_rules = {}
            instance_dict[name] = instance

            LLParser().compute_first_rules(grammar, instance, first_dict, follow_dict)

            conflict = LLParser().is_mutually_disjoint(instance, stack_transformation, grammar_text)

            if conflict:
                break

            conflict = LLParser().ll1_c3(instance, stack_transformation, grammar_text, first_dict, follow_dict)

            if conflict:
                break

    if not conflict:
        explain_text = "This is a LL(1) grammar"
        stack_transformation.push({"grammar_text": grammar_text, "transform_text": '',
                                   "explain_text": explain_text})

    create_popup_window(window, stack_transformation, config, file, 'LL(1)', None)


def create_augmented_grammar(file):
    config = CFG().read_config(file)

    # augmented grammar
    init_nt = config['input']['initial_nonterminal']
    new_nt = 'Φ'
    config.set('rules', new_nt, init_nt)
    temp_file = CFG().write_to_config_copy(config, file)
    config['input']['initial_nonterminal'] = new_nt
    CFG().write_to_config(config, temp_file)
    CFG().add_value(config, 'nonterminals', new_nt, temp_file)

    grammar = main(temp_file)
    os.remove(temp_file)

    return grammar


def rules_numbering(grammar):
    rules_num_dict = {}
    count = 0
    for nonterminal, rules in grammar.rules.items():
        for rule in rules:
            if nonterminal != grammar.initial_nonterminal:
                rules_num_dict[count] = (nonterminal, rule)
                count += 1

    return rules_num_dict


def get_lr0_items(file):
    grammar = create_augmented_grammar(file)
    grammar.rules[grammar.initial_nonterminal][0].append('⊣')

    # instances
    states_dict = {}
    state = 0
    class_name = f'I{state}'
    cls = type(class_name, (), {'name': class_name, 'items': {}, 'transitions': {}})
    instance = cls()
    states_dict[state] = instance

    # create starting item
    init_rule = grammar.rules[grammar.initial_nonterminal][0].copy()
    init_rule.insert(0, '.')
    starting_item = [init_rule]
    instance.items[grammar.initial_nonterminal] = starting_item

    # compute initial state
    LRParser().compute_lr0_closure(grammar, instance.items)

    # compute LR(0) items
    LRParser().compute_lr0_items(grammar, states_dict)

    # assign number for each production rule
    rules_num_dict = rules_numbering(grammar)

    return states_dict, rules_num_dict, grammar


def is_slr(window, file):
    grammar = main(file)

    first_dict, _ = LLParser().compute_first(grammar)
    follow_dict = LLParser().compute_follow(grammar, first_dict)

    states_dict, rules_num_dict, grammar = get_lr0_items(file)

    # compute parsing tables
    action_dict = LRParser().compute_slr_action_table(states_dict, rules_num_dict, follow_dict, grammar)
    goto_dict = LRParser().compute_lr0_goto_table(states_dict)

    # display FOLLOW sets below grammar
    config = CFG().read_config(file)
    config.add_section('FOLLOW Sets')
    for nonterminal, follow in follow_dict.items():
        config.set('FOLLOW Sets', f'FOLLOW({nonterminal})', f"{{{','.join(follow)}}}")

    with tempfile.NamedTemporaryFile(delete=False, suffix='.txt') as temp:
        temp_file = temp.name
        CFG().write_to_config(config, temp_file)

        create_table_window(window, temp_file, rules_num_dict, action_dict, goto_dict, states_dict, 'SLR(1)')
        temp.close()
        os.remove(temp_file)


def is_lr0(window, file):
    states_dict, rules_num_dict, _ = get_lr0_items(file)

    # compute action and goto table
    action_dict = LRParser().compute_lr0_action_table(states_dict, rules_num_dict)
    goto_dict = LRParser().compute_lr0_goto_table(states_dict)

    create_table_window(window, file, rules_num_dict, action_dict, goto_dict, states_dict, 'LR(0)')


def is_lr1(window, file):
    grammar = create_augmented_grammar(file)
    # grammar.rules[grammar.initial_nonterminal][0].append('⊣')

    # instances
    states_dict = {}
    state = 0
    class_name = f'I{state}'
    cls = type(class_name, (), {'name': class_name, 'items': {}, 'transitions': {}})
    instance = cls()
    states_dict[state] = instance

    # create starting item
    init_rule = grammar.rules[grammar.initial_nonterminal][0].copy()
    init_rule.insert(0, '.')
    instance.items[grammar.initial_nonterminal] = [(init_rule, '⊣')]

    # compute FIRST
    first_dict, _ = LLParser().compute_first(grammar)

    # compute initial state
    LRParser().compute_lr1_closure(grammar, instance.items, first_dict)

    # compute LR(1) items
    LRParser().compute_lr1_items(grammar, states_dict, first_dict)

    rules_num_dict = rules_numbering(grammar)

    # compute action and goto table
    action_dict = LRParser().compute_lr1_action_table(grammar, states_dict, rules_num_dict)
    goto_dict = LRParser().compute_lr0_goto_table(states_dict)

    create_table_window(window, file, rules_num_dict, action_dict, goto_dict, states_dict, 'LR(1)')


def is_lalr(window, file):
    # get lr0 items
    states_dict, rules_num_dict, grammar = get_lr0_items(file)
    grammar.terminals.append('⊣')

    # find nullable nonterminals
    config = CFG().read_config(file)
    null_nt = set()
    Transform().remove_epsilon_rules(file, config, Stack(), null_nt, [], '\u2080')

    # create lalr state set
    lalr_states = {}
    read_graph = {}
    includes_graph = {}
    for start_state, instance in states_dict.items():
        for symbol, end_state in instance.transitions.items():
            if symbol in grammar.nonterminals:
                key = (start_state, symbol)

                # compute direct reads
                lalr_states[key] = set()
                LRParser().compute_direct_reads(grammar, end_state, states_dict, lalr_states[key])

                direct_reads = copy.deepcopy(lalr_states)

                # compute read graph
                read_graph[key] = set()
                LRParser().compute_read_graph(grammar, end_state, states_dict, read_graph[key], null_nt)

                # compute includes (Follow graph)
                LRParser().compute_includes(grammar, includes_graph, key, null_nt, states_dict)

    # compute reads
    LRParser().digraph(read_graph, lalr_states)

    reads = copy.deepcopy(lalr_states)

    # compute follow
    LRParser().digraph(includes_graph, lalr_states)

    follow = copy.deepcopy(lalr_states)

    # compute look-ahead sets
    la_sets = LRParser().compute_la_sets(lalr_states, states_dict)

    # compute action and goto table
    action_dict = LRParser().compute_lalr_action_table(states_dict, la_sets, grammar)
    goto_dict = LRParser().compute_lr0_goto_table(states_dict)

    # display sets below grammar
    config = CFG().read_config(file)
    config.add_section('Direct Reads')
    for node, terminals in direct_reads.items():
        config.set('Direct Reads', f"({node[0]}, {node[1]})", f"{{{','.join(terminals)}}}")

    config.add_section('Reads')
    for node, terminals in reads.items():
        config.set('Reads', f"({node[0]}, {node[1]})", f"{{{','.join(terminals)}}}")

    config.add_section('Follow')
    for node, terminals in follow.items():
        config.set('Follow', f"({node[0]}, {node[1]})", f"{{{','.join(terminals)}}}")

    config.add_section('Look-ahead')
    for node, terminals in la_sets.items():
        state, lhs, rhs = node
        if rhs == ():
            rhs = ['ε']
        config.set('Look-ahead', f"LA({state}, {lhs} → {''.join(rhs)})", f"{{{','.join(terminals)}}}")

    with tempfile.NamedTemporaryFile(delete=False, suffix='.txt') as temp:
        temp_file = temp.name
        CFG().write_to_config(config, temp_file)

        create_table_window(window, temp_file, rules_num_dict, action_dict, goto_dict, states_dict, 'LALR(1)')
        temp.close()
        os.remove(temp_file)


def map_table_rows(table):
    row_map = {}
    for row_id in table.get_children():
        values = table.item(row_id, 'values')
        identifier = values[0]
        row_map[identifier] = row_id
    return row_map


def clear_table(table):
    table.delete(*table.get_children())


def highlight_matching_row(event, source_table, target_table, source_to_target_map, states_dict, item_table):
    clear_table(item_table)
    item = source_table.selection()[0]
    values = source_table.item(item, 'values')
    identifier = values[0]

    if identifier in source_to_target_map:
        target_row_id = source_to_target_map[identifier]
        target_table.selection_set(target_row_id)
        target_table.focus(target_row_id)

        selected_row = target_table.item(target_row_id, 'values')[0]
        for state, instance in states_dict.items():
            if int(state) == int(selected_row):
                item_table['columns'] = ()
                item_table['columns'] = ('state',)
                item_table.column("#0", width=0, stretch=tk.NO)
                item_table.column("state", anchor=tk.W)
                item_table.heading("state", text=state)
                for lhs, rhs in instance.items.items():
                    for element in rhs:
                        if isinstance(element, tuple):
                            item_text = f"{lhs} → {''.join(element[0])}     {','.join(element[1])}"
                        else:
                            item_text = f"{lhs} → {''.join(element)}"
                        item_table.insert(parent='', index='end', values=(item_text,))
                item_table.pack(pady=20)


def create_table_with_scrollbar(master_frame, frame_height, text, row):
    table_frame = tk.LabelFrame(master=master_frame, text=text, height=frame_height)
    table_frame.pack(fill=tk.BOTH, expand=1, side=tk.TOP)
    table_frame.pack_propagate(0)

    # Vertical scrollbar
    table_scroll_y = ttk.Scrollbar(table_frame, orient=tk.VERTICAL)
    table_scroll_y.pack(side=tk.RIGHT, fill=tk.Y)

    # Horizontal scrollbar
    table_scroll_x = ttk.Scrollbar(table_frame, orient=tk.HORIZONTAL)
    table_scroll_x.pack(side=tk.BOTTOM, fill=tk.X)

    # Treeview widget
    table = ttk.Treeview(table_frame, yscrollcommand=table_scroll_y.set, xscrollcommand=table_scroll_x.set)
    table_scroll_y.config(command=table.yview)
    table_scroll_x.config(command=table.xview)

    return table


def create_table_window(window, file, rules_num_dict, action_dict, goto_dict, states_dict, win_title):
    popup_window = tk.Toplevel(window)
    popup_window.title(win_title)
    popup_window.geometry(f'{window.winfo_screenwidth() - 16}x{window.winfo_screenheight() - 80}+0+0')
    popup_window.focus()

    # create grammar frame
    grammar_frame = tk.LabelFrame(master=popup_window, text="Grammar", width=400)
    grammar_frame.pack(side="left", fill=tk.Y)
    grammar_frame.pack_propagate(0)
    grammar_text_widget = tk.Text(master=grammar_frame, width=15, bg="#d3d3d3")
    grammar_text_widget.pack(fill="both", expand=1)

    create_text_scrollbar(grammar_text_widget)

    result = f"This grammar is {win_title}"
    num_states = len(states_dict)
    for state, actions in action_dict.items():
        if len(actions) > 1:
            result = f"This grammar is not {win_title}"
    result_label = tk.Label(master=grammar_frame, text=result)
    result_label.pack(pady=50)

    close_btn = tk.Button(master=grammar_frame, text="Close",
                          command=lambda: popup_window.destroy())
    close_btn.pack(pady=(0, 50))

    # insert text into grammar widget
    grammar_text = CFG().generate_grammar_text(file, {})
    grammar_text_widget.insert("1.0", grammar_text)
    grammar_text_widget.config(state=tk.DISABLED)

    # create analysis frame
    analysis_frame = tk.LabelFrame(master=popup_window, text="Analysis")
    analysis_frame.pack(side="left", fill="both", expand=1)
    analysis_frame.pack_propagate(0)

    canvas = create_scrollbars(analysis_frame)
    frame_hieght = analysis_frame.winfo_height() // 3

    # create action table
    action_table = create_table_with_scrollbar(canvas, frame_hieght, "Action table", 0)
    if win_title == 'LR(0)':
        action_table['columns'] = ("states", "action")
        action_table.column("#0", width=0, stretch=tk.NO)
        action_table.column("states", width=80, anchor=tk.CENTER)
        action_table.column("action", anchor=tk.CENTER)
        action_table.heading("action", text="Action")
        action_table.heading("states", text="States")

        # insert data into action table
        for state, actions in action_dict.items():
            action_text = ''
            count = 0
            tag = ""
            for action in actions:
                if action != 'Shift' and action != 'Accept':
                    rule_number = int(action[1])
                    rule = rules_num_dict[rule_number]
                    nonterminal, production = rule[0], rule[1]
                    if production == ['']:
                        production = ['ε']
                    action = f"{nonterminal} → {''.join(production)}"
                if count == 0:
                    action_text += action
                    count += 1
                else:
                    action_text += f' | {action}'
                    tag = "conflict"
            action_table.insert(parent='', index='end', values=(state, action_text), tags=(tag,))
            action_table.tag_configure("conflict", foreground="red")
        action_table.pack()
    else:
        create_table(action_dict, num_states, action_table, True)

    # create goto table
    goto_table = create_table_with_scrollbar(canvas, frame_hieght, "Goto table", 1)
    create_table(goto_dict, num_states, goto_table)

    # create item table
    item_table = create_table_with_scrollbar(canvas, frame_hieght, "Items", 2)

    # map rows from action_table to goto_table
    action_to_goto_map = map_table_rows(action_table)

    # map rows from goto_table to action_table
    goto_to_action_map = map_table_rows(goto_table)

    # Bind click event to action_table
    action_table.bind('<ButtonRelease-1>', lambda event: highlight_matching_row(event, action_table, goto_table,
                                                                                action_to_goto_map, states_dict,
                                                                                item_table))

    # Bind click event to table2
    goto_table.bind('<ButtonRelease-1>', lambda event: highlight_matching_row(event, goto_table, action_table,
                                                                              goto_to_action_map, states_dict,
                                                                              item_table))


def create_table(goto_dict, state, goto_table, action=False):
    # sort columns
    column_names = []
    for state_symbol, next_state in goto_dict.items():
        symbol = state_symbol[1]
        if symbol not in column_names:
            column_names.append(symbol)
    column_names.sort()

    # sort data
    rows = []
    for stat in range(state):
        temp_dict = {}
        for state_symbol, next_state in goto_dict.items():
            st, sym = state_symbol[0], state_symbol[1]
            if stat == st:
                temp_dict[sym] = next_state
        row = []
        for column_name in column_names:
            if column_name not in temp_dict:
                row.append('')
            else:
                row.append(temp_dict[column_name])
        row.insert(0, stat)
        rows.append(row)

    # format headings
    column_names.insert(0, 'States')
    goto_table['columns'] = column_names
    goto_table.column("#0", width=0, stretch=tk.NO)
    for col_name in column_names:
        if action:
            goto_table.column(col_name, anchor=tk.CENTER)
        else:
            goto_table.column(col_name, anchor=tk.CENTER, width=70)
        goto_table.heading(col_name, text=col_name)

    # insert data
    for row in rows:
        tag = ""
        for column in row:
            if isinstance(column, set):
                if len(column) > 1:
                    tag = "conflict"
        goto_table.insert(parent='', index='end', values=row, tags=(tag,))
    goto_table.tag_configure("conflict", foreground="red")
    goto_table.pack(pady=20)


def save_to_tempfile(file, rule_val, rules, init_val, grammar_str, error_label):
    config = CFG().read_config(file)
    config.set('input', 'initial_nonterminal', init_val.get())

    substrings = config['input']['nonterminals'].split(',') + config['input']['terminals'].split(',') + ['epsilon']
    substrings = sorted(substrings, key=lambda x: not x.startswith('<'))
    new_rule = []
    for rule in rules.get().split(','):
        if CFG().check_rule(rule.strip(), substrings):
            new_rule.append(rule.strip())
            error_label.config(text="")
        else:
            error_label.config(text=f"{rule} is not a valid rule")
            return

    new_rules = [item for item in new_rule if item != '']
    config.set('rules', rule_val.get(), ','.join(new_rules))
    CFG().write_to_config(config, file)
    text = CFG().generate_grammar_text(file, {}, label=True)
    grammar_str.set(text)


def saveas_newfile(temp_file, window, listbox_items, filename):
    config = CFG().read_config(temp_file)
    save_as_transformed_grammar(config, window, listbox_items, filename)


def on_select_rule(file, rule_val, rules):
    config = CFG().read_config(file)
    val = rule_val.get()
    if val in config['rules']:
        rules.set(config['rules'][val])
    else:
        rules.set('')


def display_grammar(file, grammar_str, file_variable, file_error, listbox_dict, filepath):
    file_error.config(text='')
    if file not in listbox_dict:
        file = filepath
    else:
        file = listbox_dict[file]
    if file != '':
        file_variable.set(file)
        text = CFG().generate_grammar_text(file, {}, label=True)
        grammar_str.set(text)


def submit(file_variable, grammar_str, init_combo, rule_combo, rules, rule_entry, listbox_dict):
    file = file_variable.get()

    # dummy label
    file_error = tk.Label()

    directory, filetype = os.path.split(file)
    filename = os.path.splitext(filetype)[0]
    display_grammar(filename, grammar_str, file_variable, file_error, listbox_dict, file)

    config = CFG().read_config(file)

    nonterminals = config['input']['nonterminals'].split(',')
    initial_nonterminal = config['input']['initial_nonterminal']

    # for new config
    if initial_nonterminal not in nonterminals:
        initial_nonterminal = nonterminals[0]
        config.set('input', 'initial_nonterminal', initial_nonterminal)
        CFG().write_to_config(config, file)
        text = CFG().generate_grammar_text(file, {}, label=True)
        grammar_str.set(text)

    if nonterminals == ['']:
        init_combo.set('')
        rule_combo.set('')
        rules.set('')
        init_combo.config(state=tk.DISABLED)
        rule_combo.config(state=tk.DISABLED)
        rule_entry.config(state=tk.DISABLED)
    else:
        init_combo.config(state='readonly')
        rule_combo.config(state='readonly')
        rule_entry.config(state=tk.NORMAL)

        init_nt_index = nonterminals.index(initial_nonterminal)

        init_combo['values'] = nonterminals
        init_combo.current(init_nt_index)

        rule_combo['values'] = nonterminals
        last_val = len(nonterminals) - 1
        rule_combo.current(last_val)
        if rule_combo['values'][last_val] in config['rules']:
            rules.set(config['rules'][rule_combo['values'][last_val]])
        else:
            rules.set('')


def ignore_space(event):
    if event.char == ' ':
        return 'break'


def add(file_variable, val_type, val, grammar_str, init_combo, rule_combo, rules, error_label, rule_entry,
        listbox_dict):
    file = file_variable.get()
    config = CFG().read_config(file)
    error_text = CFG().add_value(config, val_type, val, file)

    if error_text is None:
        submit(file_variable, grammar_str, init_combo, rule_combo, rules, rule_entry, listbox_dict)
        error_label.config(text="")
    else:
        error_label.config(text=error_text)


def remove(file_variable, val_type, val, grammar_str, init_combo, rule_combo, rules, error_label, rule_entry,
           listbox_dict):
    file = file_variable.get()
    config = CFG().read_config(file)
    error_text = CFG().remove_value(config, val_type, val, file)

    if error_text is None:
        submit(file_variable, grammar_str, init_combo, rule_combo, rules, rule_entry, listbox_dict)
        error_label.config(text="")
    else:
        error_label.config(text=error_text)


def update_sentential_scrollregion(sentential_canvas, sentential_str):
    sentential_canvas.delete("all")
    width = sentential_canvas.winfo_width() / 2
    sentential_canvas.create_text(width, 30, text=sentential_str.get())
    sentential_canvas.config(scrollregion=sentential_canvas.bbox("all"))


def update_vertical_scrollregion(canvas, str_var):
    canvas.delete("all")
    width = canvas.winfo_width() / 2
    canvas.create_text(width, 10, text=str_var.get())
    canvas.config(scrollregion=canvas.bbox("all"))
    canvas.yview_moveto(1.0)


def calculate_subtree_width(tree, x_space):
    if not tree.children:
        return x_space
    return sum(calculate_subtree_width(child, x_space) for child in tree.children) + (len(tree.children) - 1) * x_space


def calculate_positions(canvas, tree, x, y, x_space, y_space, level=0, positions=None, nonterminal=None):
    if positions is None:
        positions = {}

    if tree.data == '':
        text = "\u03B5"
    else:
        text = tree.data

    width = calculate_subtree_width(tree, x_space)
    x_offset = -width / 2

    node_x = x
    node_y = y + y_space * level
    positions[id(tree)] = (node_x, node_y)

    if nonterminal == text and tree.children == []:
        canvas.create_text(node_x, node_y, text=text, tags="occ")
    else:
        canvas.create_text(node_x, node_y, text=text, tags="node")

    if tree.children:
        for child in tree.children:
            child_width = calculate_subtree_width(child, x_space)
            calculate_positions(canvas, child, x + x_offset + child_width / 2, y + y_space, x_space, y_space, level + 1,
                                positions, nonterminal)
            draw_lines_between_nodes(canvas, positions[id(tree)], positions[id(child)])
            x_offset += child_width + x_space


def draw_tree(canvas, tree, x=400, y=50, x_space=100, y_space=120, nonterminal=None, nt_pos=None):
    calculate_positions(canvas, tree, x, y, x_space, y_space, level=0, positions=None, nonterminal=nonterminal)

    occ = 0
    for widget in canvas.find_all():
        tags = canvas.gettags(widget)
        if "node" in tags:
            x, y, x1, y1 = canvas.bbox(widget)
            canvas.create_oval(x - 10, y - 8, x1 + 10, y1 + 8, fill="lightblue", tags='oval')
            canvas.tag_raise('node')
            canvas.config(scrollregion=canvas.bbox("all"))
        if "occ" in tags:
            occ += 1
            x, y, x1, y1 = canvas.bbox(widget)
            if occ == nt_pos:
                canvas.create_oval(x - 10, y - 8, x1 + 10, y1 + 8, fill="pink", tags='oval')
            else:
                canvas.create_oval(x - 10, y - 8, x1 + 10, y1 + 8, fill="lightblue", tags='oval')
            # canvas.create_text(x1 - 4, y1 + 20, text=occ, tags="occ")
            canvas.tag_raise('occ')
            canvas.config(scrollregion=canvas.bbox("all"))


def draw_lines_between_nodes(canvas, parent_pos, child_pos):
    parent_x, parent_y = parent_pos
    child_x, child_y = child_pos
    canvas.create_line(parent_x, parent_y, child_x, child_y - 15, arrow=tk.LAST)


def undo(grammar, input_frame, rule_frame, sentential_str, sentential_canvas, canvas, undo_btn, redo_btn):
    redo_btn.config(state="normal")

    sentence, ldata = grammar.stack.undo('S', grammar.nonterminals)
    tree = grammar.stack_tree.undo('T', grammar.nonterminals)
    if ldata == grammar.stack.data[0]:
        undo_btn.config(state="disabled")
        update_label(sentential_str, grammar.stack.data[0])
        update_sentential_scrollregion(sentential_canvas, sentential_str)
        x = 400
        y = 50
        canvas.delete("all")
        canvas.create_oval(x, y, x + 30, y + 30, fill="lightblue")
        canvas.create_text(x + 15, y + 15, text=grammar.stack.data[0])
        execute(grammar, ldata, input_frame, rule_frame, sentential_str, sentential_canvas, canvas, undo_btn, redo_btn,
                tree)
    else:
        update_label(sentential_str, sentence)
        update_sentential_scrollregion(sentential_canvas, sentential_str)
        canvas.delete("all")
        draw_tree(canvas, tree, 400, 50, 50, 60)
        current_sentence = ldata.split(' ')
        execute(grammar, current_sentence, input_frame, rule_frame, sentential_str, sentential_canvas, canvas, undo_btn,
                redo_btn, tree)


def redo(grammar, input_frame, rule_frame, sentential_str, sentential_canvas, canvas, undo_btn, redo_btn):
    undo_btn.config(state="normal")

    sentence, ldata = grammar.stack.redo('S', grammar.nonterminals)
    tree = grammar.stack_tree.redo('T', grammar.nonterminals)
    if ldata == grammar.stack.data[-1]:
        redo_btn.config(state="disabled")
    update_label(sentential_str, sentence)
    update_sentential_scrollregion(sentential_canvas, sentential_str)
    canvas.delete("all")
    draw_tree(canvas, tree, 400, 50, 50, 60)
    nt = [elem for elem in grammar.nonterminals if elem in ldata.split(" ")]
    if nt:
        current_sentence = ldata.split(' ')
        execute(grammar, current_sentence, input_frame, rule_frame, sentential_str, sentential_canvas, canvas, undo_btn,
                redo_btn)
    else:
        clear_widgets(input_frame)

        derived_string = ldata.split(' ')
        derived_string = [item for item in derived_string if item != '']
        derived_string = ' '.join(derived_string)

        label = tk.Label(master=input_frame, text=derived_string)
        label.pack()


def construct_derivation(grammar, nonterminal, rule, position, sentential_str, sentential_canvas, canvas):
    ldata = grammar.replacer(grammar.stack.current(), nonterminal, ' '.join(rule), position)
    current_sentence = ldata.split(' ')
    grammar.stack.push(ldata)
    sentence = grammar.create_sentential_form(grammar.stack.data, nonterminal, ''.join(rule), position)
    update_label(sentential_str, sentence)
    update_sentential_scrollregion(sentential_canvas, sentential_str)
    grammar.stack_tree.push({nonterminal: rule, "position": position})
    tree = grammar.build_tree(grammar.stack_tree, grammar.nonterminals)
    canvas.delete("all")
    draw_tree(canvas, tree, 400, 50, 50, 60)

    return current_sentence


def perform_derivation(grammar, rule, input_frame, rule_frame, sentential_str, sentential_canvas, canvas, undo_btn,
                       redo_btn, nonterminal, position):
    clear_widgets(input_frame)
    undo_btn.config(state=tk.NORMAL)
    redo_btn.config(state=tk.DISABLED)

    current_sentence = construct_derivation(grammar, nonterminal, rule, position, sentential_str, sentential_canvas,
                                            canvas)

    nt = [elem for elem in grammar.nonterminals if elem in current_sentence]
    if nt:
        execute(grammar, current_sentence, input_frame, rule_frame, sentential_str, sentential_canvas, canvas, undo_btn,
                redo_btn)
    else:
        clear_widgets(rule_frame)

        derived_string = current_sentence.copy()
        derived_string = [item for item in derived_string if item != '']
        derived_string = ' '.join(derived_string)

        label = tk.Label(master=input_frame, text=derived_string)
        label.pack(padx=90)


def choose_rule(grammar, input_frame, rule_frame, sentential_str, sentential_canvas, canvas, undo_btn, redo_btn,
                nonterminal, position, nt_btn, undo_tree):
    clear_widgets(rule_frame)

    # highlight selected button
    reset_button_colour(input_frame)
    nt_btn.config(bg='pink')

    # highlight graphical tree
    if undo_tree is None:
        tree = grammar.build_tree(grammar.stack_tree, grammar.nonterminals)
        canvas.delete("all")
        draw_tree(canvas, tree, 400, 50, 50, 60, nonterminal, position)
    else:
        canvas.delete("all")
        if isinstance(undo_tree, dict):
            x = 400
            y = 50
            canvas.create_oval(x, y, x + 30, y + 30, fill="pink")
            canvas.create_text(x + 15, y + 15, text=grammar.stack.data[0])
        else:
            draw_tree(canvas, undo_tree, 400, 50, 50, 60, nonterminal, position)

    for production in grammar.rules[nonterminal]:
        btn_txt = ''.join(production)
        if btn_txt == '':
            btn_txt = '\u03B5'
        button = tk.Button(master=rule_frame, text=btn_txt, relief='flat', bg='lightblue',
                           command=lambda rule=production: perform_derivation(grammar, rule, input_frame, rule_frame,
                                                                              sentential_str, sentential_canvas,
                                                                              canvas, undo_btn, redo_btn,
                                                                              nonterminal, position))
        button.pack(side=tk.LEFT, pady=10, padx=10)


def execute(grammar, current_sentence, input_frame, rule_frame, sentential_str, sentential_canvas, canvas, undo_btn,
            redo_btn, undo_tree=None):
    clear_widgets(input_frame)
    clear_widgets(rule_frame)

    symbol_positions = {symbol: 0 for symbol in grammar.nonterminals}

    for symbol in current_sentence:
        if symbol in grammar.nonterminals:
            symbol_positions[symbol] += 1
            position = symbol_positions[symbol]

            button = tk.Button(master=input_frame, text=symbol, relief='flat', bg='lightblue')
            button.config(command=lambda sym=symbol, pos=position, nt_btn=button: choose_rule(grammar, input_frame,
                                                                                              rule_frame,
                                                                                              sentential_str,
                                                                                              sentential_canvas,
                                                                                              canvas, undo_btn,
                                                                                              redo_btn, sym, pos,
                                                                                              nt_btn, undo_tree))
            button.pack(side=tk.LEFT, pady=10, padx=10)
        else:
            if symbol != '':
                label = tk.Label(master=input_frame, text=symbol)
                label.pack(side=tk.LEFT, pady=10, padx=10)


def get_tokens(string, grammar):
    tokens = []
    temp = ''

    for char in string:
        temp += char
        for substring in grammar.terminals:
            if temp == substring:
                tokens.append(substring)
                temp = ''
                break

    return tokens


def derive_automatically(grammar, tokens, state_sets, pointers_dict, sentential_str, sentential_canvas, canvas,
                         state_number, state_index):
    states = state_sets[(state_number, tokens[state_number])]
    state = states[state_index]
    lhs, rhs, _, _, _ = state
    if rhs == []:
        rhs = ['']

    position = 1
    construct_derivation(grammar, lhs, rhs, position, sentential_str, sentential_canvas, canvas)

    pointers = None
    if (state_number, state_index) in pointers_dict:
        pointers = pointers_dict[(state_number, state_index)]
    if pointers:
        nt_count = 0
        for symbol in rhs:
            if symbol in grammar.nonterminals:
                state_number, state_index = pointers[nt_count]
                derive_automatically(grammar, tokens, state_sets, pointers_dict, sentential_str, sentential_canvas,
                                     canvas, state_number, state_index)
                nt_count += 1


def recognize(result_str, entry_str, grammar, sentential_str, sentential_canvas, canvas):
    # reset stacks
    grammar.stack = Stack()
    grammar.stack_tree = Stack()
    grammar.stack.push(grammar.initial_nonterminal)

    tokens = get_tokens(entry_str.get(), grammar)

    # add end marker to input string
    tokens.append('⊣')
    first_dict, _ = LLParser().compute_first(grammar)

    state_sets, final_state, pointers_dict = Recognizer().parse(grammar, tokens, first_dict)

    final_state_number = len(state_sets) - 1
    if state_sets[(final_state_number, '')] == [final_state]:
        result_str.set(f"The string is in the language generated by the grammar")

        pointers = pointers_dict[(final_state_number, 0)]
        state_number, state_index = pointers[0]

        derive_automatically(grammar, tokens, state_sets, pointers_dict, sentential_str, sentential_canvas, canvas,
                             state_number, state_index)
    else:
        result_str.set(f"The string is not in the language generated by the grammar")


def change_derivation(derivation_str, input_frame, grammar, rule_frame, sentential_str, sentential_canvas, canvas,
                      undo_btn, redo_btn):
    # reset stacks
    grammar.stack = Stack()
    grammar.stack_tree = Stack()
    grammar.stack.push(grammar.initial_nonterminal)

    if derivation_str.get() == "Automatic":
        derivation_str.set("Manual")

        clear_widgets(input_frame)
        clear_widgets(rule_frame)
        undo_btn.config(state=tk.DISABLED)
        redo_btn.config(state=tk.DISABLED)

        # label
        label_str = tk.StringVar()
        label_str.set("Enter an input string")
        label = tk.Label(master=input_frame, textvariable=label_str)
        label.pack(padx=(0, 50), pady=10)

        # frame
        frame = tk.Frame(master=input_frame)
        frame.pack()

        entry_str = tk.StringVar()
        entry = tk.Entry(master=frame, textvariable=entry_str)
        entry.pack(side=tk.LEFT)

        entry.bind('<KeyPress>', ignore_space)

        # result label
        result_str = tk.StringVar()
        result_label = tk.Label(master=rule_frame, textvariable=result_str)
        result_label.pack()

        derive_btn = tk.Button(master=frame, text="Derive", command=lambda: recognize(result_str, entry_str,
                                                                                      grammar, sentential_str,
                                                                                      sentential_canvas, canvas))
        derive_btn.pack(side=tk.LEFT, padx=10)

        CreateToolTip(entry, "Enter an input")
        CreateToolTip(derive_btn, "Construct derivation for the input")
    else:
        derivation_str.set("Automatic")
        undo_tree = {'just': 'temp'}
        execute(grammar, grammar.initial_nonterminal, input_frame, rule_frame, sentential_str, sentential_canvas,
                canvas, undo_btn, redo_btn, undo_tree)


def clear_widgets(frame):
    for widget in frame.winfo_children():
        widget.destroy()


def reset_button_colour(frame):
    for widget in frame.winfo_children():
        if isinstance(widget, tk.Button):
            widget.config(bg='lightblue')
