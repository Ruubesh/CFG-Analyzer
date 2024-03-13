from tkinter import filedialog, ttk
from cfg import CFG, main, Stack
import tkinter as tk
from itertools import combinations
import os


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


def open_files(listbox, listbox_items):
    filenames = filedialog.askopenfilenames(
        initialdir="/Users/ruube/PycharmProjects/Thesis",
        title="Select A File",
        filetypes=(("Text files", "*.txt"), ("All files", "*.*"))
    )

    for filename in filenames:
        if filename not in listbox.get(0, tk.END):
            listbox.insert(tk.END, filename)
            listbox_items.append(filename)


def remove_file(listbox, listbox_items):
    selected_index = listbox.curselection()
    if selected_index:
        listbox.delete(selected_index)
        for index in selected_index:
            del listbox_items[index]


def read_file(file):
    with open(file, 'r') as f:
        text = f.read()
        return text


def display_grammar(file, grammar_str, file_variable):
    file_variable.set(file)
    text = CFG().generate_grammar_text(file, {}, label=True)
    grammar_str.set(text)


def submit(file_variable, grammar_str, init_combo, rule_combo, rules):
    file = file_variable.get()
    display_grammar(file, grammar_str, file_variable)

    grammar = CFG().read_config(file)
    init_combo['values'] = grammar['input']['nonterminals'].split(',')
    init_combo.current(0)

    rule_combo['values'] = grammar['input']['nonterminals'].split(',')
    rule_combo.current(0)
    rules.set(grammar['rules'][rule_combo['values'][0]])


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


def save_as_transformed_grammar(config, popup_window):
    file = filedialog.asksaveasfilename(parent=popup_window,
                                        defaultextension=".*",
                                        initialdir="/Users/ruube/PycharmProjects/Thesis",
                                        title="Save File",
                                        filetypes=(("Text files", "*.txt"), ("All files", "*.*"))
                                        )

    if file:
        CFG().write_to_config(config, file)


def on_popup_window_close(window, config, file):
    temp_file = CFG().write_to_config_copy(config, file)
    os.remove(temp_file)
    window.destroy()


def create_popup_window(window, stack_transformation, config, file):
    popup_window = tk.Toplevel(window)
    popup_window.title("View Transformation")
    popup_window.protocol("WM_DELETE_WINDOW", lambda: on_popup_window_close(popup_window, config, file))
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
                         command=lambda: save_as_transformed_grammar(config, popup_window))
    save_btn.pack(side=tk.LEFT, padx=20, pady=15)
    forward_btn = tk.Button(master=center_button_frame, text="-->",
                            command=lambda: on_pressing_right(grammar_text_widget, transform_str, explain_str,
                                                              stack_transformation, index, back_btn, forward_btn,
                                                              transform_canvas))
    forward_btn.pack(side=tk.LEFT, padx=20)

    grammar_frame = tk.LabelFrame(master=popup_window, text="Grammar", width=popup_window.winfo_width() / 3)
    grammar_frame.pack(side="left", fill="both", expand=1)
    grammar_frame.pack_propagate(0)
    grammar_text_widget = tk.Text(master=grammar_frame, width=15, bg="#d3d3d3")
    grammar_text_widget.pack(fill="both", expand=1)

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


def reduce(window, file_variable):
    stack_transformation = Stack()
    grammar = main(file_variable)
    config = CFG().read_config(file_variable)

    set_t = set()
    set_list = []
    grammar.reduce_phase1(file_variable, config, grammar, stack_transformation, set_t, set_list, '\u2080')

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
    grammar.reduce_phase2(file_variable, config, grammar, stack_transformation, set_t, set_d, set_list, '\u2081')

    transform_text = f"\nD = {set_list}"
    stack_transformation.push({"grammar_text": grammar_text, "transform_text": transform_text, "explain_text": ''})

    update_reduction_rules(config, grammar, file_variable, set_d, stack_transformation)

    create_popup_window(window, stack_transformation, config, file_variable)


def remove_epsilon_rules(window, file_variable, other_stack=None, other_transform=False):
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
    CFG().remove_epsilon_rules(file_variable, config, stack_transformation, set_e, set_list, '\u2080')

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
        new_init_nt = f"{grammar.initial_nonterminal}_prime"
        CFG().add_value(config, 'nonterminals', new_init_nt, file_variable, overwrite=False)
        new_init_rule = [grammar.initial_nonterminal, 'epsilon']
        config.set('input', 'initial_nonterminal', new_init_nt)
        config.set('rules', new_init_nt, ','.join(new_init_rule))
    elif other_transform:
        for nonterminal, production_rules in grammar.rules.items():
            for rule in production_rules:
                if grammar.initial_nonterminal in rule:
                    new_init_nt = f"{grammar.initial_nonterminal}_prime"
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

        create_popup_window(window, stack_transformation, config, file_variable)


def remove_unit_rules(window, file, other_stack=None, other_transform=False):
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
                    remove_epsilon_rules(window, file, Stack(), other_transform=True)
                    epsilon = True

        config = CFG().read_config(file)
        transform_text = generate_rules_text(config)
        explain_text = "Grammar after removing epsilon rules"
        stack_transformation.push({"grammar_text": grammar_text, "transform_text": transform_text,
                                   "explain_text": explain_text})

    transform_sets = {}
    for nonterminal in config['rules']:
        set_nt = set()
        set_list = []

        set_nt.add(nonterminal)
        set_list.append(nonterminal)
        transformation_text = f"N({nonterminal})\u2080 = {set_list}"
        stack_transformation.push({"grammar_text": grammar_text, "transform_text": transformation_text,
                                   "explain_text": ''})
        CFG().remove_unit_rules(file, config, stack_transformation, set_nt, set_list, '\u2081')

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
        create_popup_window(window, stack_transformation, config, file)
    else:
        CFG().write_to_config_copy(config, file)

        create_popup_window(window, stack_transformation, config, file)


def chomsky_normal_form(window, file):
    stack_transformation = Stack()
    config = CFG().read_config(file)
    grammar = main(file)

    # Step 1
    CFG().decompose_rules(config, grammar)

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
    remove_epsilon_rules(window, copy_file, stack_transformation, other_transform=True)

    # Step 3
    remove_unit_rules(window, copy_file, stack_transformation, other_transform=True)

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

    create_popup_window(window, stack_transformation, config, file)


def greibach_normal_form(window, file):
    config = CFG().read_config(file)
    copy_file = CFG().write_to_config_copy(config, file)
    stack_transformation = Stack()

    # Remove Epsilon Rules
    remove_epsilon_rules(window, copy_file, Stack(), other_transform=True)

    # Remove Unit Rules
    remove_unit_rules(window, copy_file, Stack(), other_transform=True)

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
        CFG().gnf_phase1(grammar, nonterminal, nt_dict, config, stack_transformation, copy_file)

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
        CFG().gnf_phase2(grammar, nonterminal, config, stack_transformation, copy_file)

    CFG().write_to_config_copy(config, file)

    create_popup_window(window, stack_transformation, config, file)


def save_to_config(file, rule_val, rules, init_val, grammar_str, error_label):
    grammar = CFG().read_config(file)
    grammar.set('input', 'initial_nonterminal', init_val.get())

    substrings = grammar['input']['nonterminals'].split(',') + grammar['input']['terminals'].split(',') + ['epsilon']
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
    grammar.set('rules', rule_val.get(), ','.join(new_rules))
    CFG().write_to_config(grammar, file)
    text = CFG().generate_grammar_text(file, {}, label=True)
    grammar_str.set(text)


def on_select_rule(file, rule_val, rules):
    grammar = CFG().read_config(file)
    for i in grammar['rules']:
        if i == rule_val.get():
            rules.set(grammar['rules'][i])


def add(file, val_type, val, grammar_str, init_combo, rule_combo, rules, error_label):
    config = CFG().read_config(file)
    error_text = CFG().add_value(config, val_type, val, file)

    if error_text is None:
        submit(file, grammar_str, init_combo, rule_combo, rules)
        error_label.config(text="")
    else:
        error_label.config(text=error_text)


def remove(file, val_type, val, grammar_str, init_combo, rule_combo, rules, error_label):
    config = CFG().read_config(file)
    error_text = CFG().remove_value(config, val_type, val, file)

    if error_text is None:
        submit(file, grammar_str, init_combo, rule_combo, rules)
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


def draw_tree(canvas, tree, x=400, y=50, x_space=100, y_space=120, nonterminal=None):
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
            canvas.create_oval(x - 10, y - 8, x1 + 10, y1 + 8, fill="pink", tags='oval')
            canvas.create_text(x1 - 4, y1 + 20, text=occ, tags="occ")
            canvas.tag_raise('occ')
            canvas.config(scrollregion=canvas.bbox("all"))


def draw_lines_between_nodes(canvas, parent_pos, child_pos):
    parent_x, parent_y = parent_pos
    child_x, child_y = child_pos
    canvas.create_line(parent_x, parent_y, child_x, child_y - 15, arrow=tk.LAST)


def undo(output_str, input_str, sentential_str, canvas, execute_e1, grammar, execute_btn, undo_btn, redo_btn,
         sentential_canvas):
    redo_btn.config(state="normal")
    execute_btn.config(state='normal')
    execute_e1.config(state='readonly')

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
        execute(output_str, input_str, sentential_str, canvas, execute_e1, grammar, ldata, execute_btn, undo_btn,
                redo_btn, sentential_canvas, tree)
    else:
        update_label(sentential_str, sentence)
        update_sentential_scrollregion(sentential_canvas, sentential_str)
        canvas.delete("all")
        draw_tree(canvas, tree, 400, 50, 50, 60)
        get_nonterminal(output_str, input_str, sentential_str, canvas, execute_e1, grammar, execute_btn, ldata,
                        undo_btn, redo_btn, sentential_canvas, tree)


def redo(output_str, input_str, sentential_str, canvas, execute_e1, grammar, execute_btn, undo_btn, redo_btn,
         sentential_canvas):
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
        get_nonterminal(output_str, input_str, sentential_str, canvas, execute_e1, grammar, execute_btn, ldata,
                        undo_btn,
                        redo_btn, sentential_canvas)
    else:
        execute_btn.config(state='disabled')
        execute_e1.config(state='disabled')
        update_label(input_str, '')
        update_label(output_str, f'Result: {ldata}')


def choose_nonterminal(output_str, input_str, sentential_str, canvas, execute_e1, grammar, execute_btn, undo_btn,
                       redo_btn, sentential_canvas, undo_tree):
    non_terminal = input_str.get()
    execute(output_str, input_str, sentential_str, canvas, execute_e1, grammar, non_terminal, execute_btn, undo_btn,
            redo_btn, sentential_canvas, undo_tree)


def get_nonterminal(output_str, input_str, sentential_str, canvas, execute_e1, grammar, execute_btn, ldata, undo_btn,
                    redo_btn, sentential_canvas, undo_tree=None):
    val = [elem for elem in grammar.nonterminals if elem in ldata.split(" ")]
    if val:
        if len(val) == 1:
            non_terminal = val[0]
            execute(output_str, input_str, sentential_str, canvas, execute_e1, grammar, non_terminal, execute_btn,
                    undo_btn, redo_btn, sentential_canvas, undo_tree)
        else:
            update_label(output_str,
                         f"\nLast expansion : {ldata} \nChoose the next non terminal for expansion: \n ")
            update_options(execute_e1, val)
            execute_btn.config(
                command=lambda: choose_nonterminal(output_str, input_str, sentential_str, canvas, execute_e1, grammar,
                                                   execute_btn, undo_btn, redo_btn, sentential_canvas, undo_tree))


def process_data(output_str, input_str, sentential_str, canvas, execute_e1, grammar, initial_nonterminal, execute_btn,
                 selected_expansion, undo_btn, redo_btn, sentential_canvas):
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
    update_sentential_scrollregion(sentential_canvas, sentential_str)
    grammar.stack_tree.push({initial_nonterminal: selected_expansion, "position": position})
    tree = grammar.build_tree(grammar.stack_tree, grammar.nonterminals)
    canvas.delete("all")
    draw_tree(canvas, tree, 400, 50, 50, 60)
    nt = [elem for elem in grammar.nonterminals if elem in ldata.split(" ")]
    if nt:
        get_nonterminal(output_str, input_str, sentential_str, canvas, execute_e1, grammar, execute_btn, ldata,
                        undo_btn, redo_btn, sentential_canvas)
    else:
        execute_btn.config(state='disabled')
        execute_e1.config(state='disabled')
        update_label(input_str, '')
        update_label(output_str, f'Result: {ldata}')


def get_occurrence(output_str, input_str, sentential_str, canvas, execute_e1, grammar, initial_nonterminal, execute_btn,
                   undo_btn, redo_btn, sentential_canvas, undo_tree):
    selected_expansion = input_str.get().split()
    if grammar.stack.current().count(initial_nonterminal) > 1:
        update_label(output_str,
                     f"Enter the occurrence of '{initial_nonterminal}' to expand in '{grammar.stack.current()}' : \n ")
        occurrences = []
        for i in range(1, grammar.stack.current().count(initial_nonterminal) + 1):
            occurrences.append(i)
        update_options(execute_e1, occurrences)

        if undo_tree is None:
            tree = grammar.build_tree(grammar.stack_tree, grammar.nonterminals)
            canvas.delete("all")
            draw_tree(canvas, tree, 400, 50, 50, 60, initial_nonterminal)
        else:
            canvas.delete("all")
            draw_tree(canvas, undo_tree, 400, 50, 50, 60, initial_nonterminal)

        execute_btn.config(
            command=lambda: process_data(output_str, input_str, sentential_str, canvas, execute_e1, grammar,
                                         initial_nonterminal, execute_btn, selected_expansion, undo_btn, redo_btn,
                                         sentential_canvas))
    else:
        process_data(output_str, input_str, sentential_str, canvas, execute_e1, grammar, initial_nonterminal,
                     execute_btn, selected_expansion, undo_btn, redo_btn, sentential_canvas)


def execute(output_str, input_str, sentential_str, canvas, execute_e1, grammar, initial_nonterminal, execute_btn,
            undo_btn, redo_btn, sentential_canvas, undo_tree, init_val=False):
    if initial_nonterminal not in grammar.rules:
        return initial_nonterminal

    if init_val:
        x = 400
        y = 50
        update_label(sentential_str, initial_nonterminal)
        update_sentential_scrollregion(sentential_canvas, sentential_str)
        canvas.create_oval(x, y, x + 30, y + 30, fill="lightblue")
        canvas.create_text(x + 15, y + 15, text=initial_nonterminal)

    update_label(output_str, f"Choose the next expansion for '{initial_nonterminal}':")
    options = []
    for i, option in enumerate(grammar.rules[initial_nonterminal], 1):
        if option[0] == '':
            options.append("\u03B5")
        else:
            options.append(' '.join(option))

    update_options(execute_e1, options)

    execute_btn.config(
        command=lambda: get_occurrence(output_str, input_str, sentential_str, canvas, execute_e1, grammar,
                                       initial_nonterminal, execute_btn, undo_btn, redo_btn, sentential_canvas,
                                       undo_tree))
