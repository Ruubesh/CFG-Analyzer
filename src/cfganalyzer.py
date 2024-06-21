import tempfile
import tkinter as tk
from tkinter import ttk
import functions
import cfg
from functions import clear_widgets
from tooltips import CreateToolTip
import os


def execute_submit(grammar_str, init_combo, rule_combo, rules, file_error, rule_entry):
    try:
        file_error.pack_forget()
        functions.submit(file_variable, grammar_str, init_combo, rule_combo, rules, rule_entry)
    except Exception as e:
        load_initial_page(f"Invalid grammar file format.\nerror: {e}")


def execute_run(listbox, file_error):
    try:
        selected = listbox.curselection()
        if not selected:
            file_error.config(text="No file selected. Please select a file")
        elif len(selected) > 1:
            file_error.config(text="Multiple files selected. Please select only one file")
        else:
            load_page2()
    except Exception as e:
        load_initial_page(f"Invalid grammar file format.\nerror: {e}")


def create_edit_frame(master_frame, frame_name, grammar_str, error_label):
    edit_frame = tk.LabelFrame(master=master_frame, text=frame_name, height=165)
    edit_frame.pack(fill="x")
    edit_frame.pack_propagate(0)

    nt_frame = tk.Frame(master=edit_frame, height=155, width=edit_frame.winfo_width() / 2)
    nt_frame.pack(side='left', fill='x', expand=1, padx=100)

    back_btn = tk.Button(master=nt_frame, text='Back', width=7, command=lambda: load_initial_page())
    back_btn.pack(side=tk.LEFT)

    entry_str = tk.StringVar()
    entry = tk.Entry(master=nt_frame, textvariable=entry_str)
    entry.pack(pady=5)

    edit_f1 = tk.Frame(master=nt_frame)
    edit_f1.pack(pady=10)

    choice = tk.StringVar()
    choice.set("nonterminals")
    nt_radio = tk.Radiobutton(edit_f1, text="Non-Terminal", variable=choice, value="nonterminals")
    nt_radio.pack(side='left', padx=10)
    t_radio = tk.Radiobutton(edit_f1, text="Terminal", variable=choice, value="terminals")
    t_radio.pack(side='left', padx=10)

    edit_f2 = tk.Frame(master=nt_frame)
    edit_f2.pack(pady=10)

    temp_variable = tk.StringVar()
    temp_variable.set(temp_file)

    add_btn = tk.Button(master=edit_f2, text="Add", width=7,
                        command=lambda: functions.add(temp_variable, choice.get(), entry_str.get(), grammar_str,
                                                      init_combo, rule_combo, rules, error_label, rule_entry))
    add_btn.pack(side="left", padx=10)

    remove_btn = tk.Button(master=edit_f2, text="Remove", width=7,
                           command=lambda: functions.remove(temp_variable, choice.get(), entry_str.get(),
                                                            grammar_str, init_combo, rule_combo, rules,
                                                            error_label, rule_entry))
    remove_btn.pack(side="left", padx=10)

    rule_frame = tk.Frame(master=edit_frame, height=155, width=edit_frame.winfo_width() / 2)
    rule_frame.pack(side="left", fill='both', expand=1)

    rule_l1 = tk.Label(master=rule_frame, text="Initial Nonterminal:")
    rule_l1.grid(row=0, column=0, pady=10)

    init_val = tk.StringVar()
    nt_options = []
    init_combo = ttk.Combobox(master=rule_frame, textvariable=init_val, state="readonly", values=nt_options)
    init_combo.grid(row=0, column=1)

    init_combo.bind("<<ComboboxSelected>>",
                    lambda event: functions.save_to_tempfile(temp_file, rule_val, rules, init_val,
                                                             grammar_str, error_label))

    rule_l2 = tk.Label(master=rule_frame, text="Rules:")
    rule_l2.grid(row=1, column=0, sticky='e', pady=12)

    rule_val = tk.StringVar()
    rule_options = []
    rule_combo = ttk.Combobox(master=rule_frame, textvariable=rule_val, state="readonly", values=rule_options)
    rule_combo.grid(row=1, column=1)
    rule_combo.bind("<<ComboboxSelected>>",
                    lambda event: functions.on_select_rule(temp_file, rule_val, rules))

    rules = tk.StringVar()
    rule_entry = tk.Entry(master=rule_frame, width=30, textvariable=rules)
    rule_entry.grid(row=1, column=2, padx=10)

    # bind rules entry box
    rule_entry.bind("<KeyRelease>",
                    lambda event: functions.save_to_tempfile(temp_file, rule_val, rules, init_val,
                                                             grammar_str, error_label))

    save_btn = tk.Button(master=rule_frame, text="Save", width=7,
                         command=lambda: functions.saveas_newfile(temp_file, window, listbox_items))
    save_btn.grid(row=2, columnspan=3, pady=10)

    # Tooltips for edit frame
    CreateToolTip(back_btn, "Go to previous page")
    CreateToolTip(add_btn, "Add the specified input symbol to the grammar")
    CreateToolTip(remove_btn, "Remove the specified input symbol from the grammar")
    CreateToolTip(entry, "Enter an input symbol")
    CreateToolTip(init_combo, "Choose the initial nonterminal")
    CreateToolTip(rule_combo, "Choose a nonterminal to modify its production rules")
    CreateToolTip(rule_entry, "Modify the production rules of the chosen nonterminal")
    CreateToolTip(save_btn, "Save the modified grammar")

    return init_combo, rule_combo, rules, rule_entry


def load_create_page():
    clear_widgets(initial_page_frame)
    initial_page_frame.pack_forget()
    create_page_frame.pack(fill=tk.BOTH, expand=1)

    # grammar_frame
    grammar_frame = tk.LabelFrame(master=create_page_frame, text="Grammar", height=400)
    # grammar_frame.pack_propagate(0)

    grammar_str = tk.StringVar()
    grammar_l1 = tk.Label(master=grammar_frame, textvariable=grammar_str, justify='left')
    grammar_l1.pack()

    error_label = tk.Label(master=create_page_frame, fg="red")

    # Create frame
    frame_name = 'Create'
    init_combo, rule_combo, rules, rule_entry = create_edit_frame(create_page_frame, frame_name, grammar_str,
                                                                  error_label)

    # disable widgets
    init_combo.config(state=tk.DISABLED)
    rule_combo.config(state=tk.DISABLED)
    rule_entry.config(state=tk.DISABLED)

    # pack widgets
    error_label.pack(pady=10)
    grammar_frame.pack(fill=tk.BOTH, expand=1)

    # create new temp file
    config = cfg.CFG().new_config()
    cfg.CFG().write_to_config(config, temp_file)


def load_initial_page(error_text=''):
    clear_widgets(create_page_frame)
    clear_widgets(page1_frame)
    clear_widgets(page2_frame)
    page1_frame.pack_forget()
    page2_frame.pack_forget()
    create_page_frame.pack_forget()
    initial_page_frame.pack(fill=tk.BOTH, expand=1)

    # top_frame
    top_frame = tk.Frame(master=initial_page_frame, height=initial_page_frame.winfo_height() / 2)
    top_frame.pack(fill='x', expand=1)

    # list_frame
    list_frame = tk.Frame(master=top_frame)
    list_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=1)

    listbox = tk.Listbox(master=list_frame, selectmode=tk.EXTENDED, height=25, width=80)
    listbox.pack(padx=80, pady=10, anchor=tk.E)
    listbox.bind("<<ListboxSelect>>",
                 lambda event: functions.display_grammar(listbox.get(tk.ANCHOR), grammar_str, file_variable,
                                                         file_error))

    for item in listbox_items:
        listbox.insert(tk.END, item)

    # btn_frame
    btn_frame = tk.Frame(master=top_frame)
    btn_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=1, pady=60)

    new_btn = tk.Button(master=btn_frame, text="New", width=10,
                        command=lambda: load_create_page())
    new_btn.pack(anchor=tk.W)

    add_btn = tk.Button(master=btn_frame, text="Add", width=10,
                        command=lambda: functions.open_files(listbox, listbox_items, file_error))
    add_btn.pack(pady=40, anchor=tk.W)

    remove_btn = tk.Button(master=btn_frame, text="Remove", width=10,
                           command=lambda: functions.remove_file(listbox, listbox_items, file_error))
    remove_btn.pack(anchor=tk.W)

    edit_btn = tk.Button(master=btn_frame, text="Edit", width=10,
                         command=lambda: load_page1(file_error, listbox))
    edit_btn.pack(pady=40, anchor=tk.W)

    run_btn = tk.Button(master=btn_frame, text="Run", width=10,
                        command=lambda: execute_run(listbox, file_error))
    run_btn.pack(anchor=tk.W)

    file_error = tk.Label(master=initial_page_frame, text=error_text, fg='red')
    file_error.pack()

    # grammar_frame
    grammar_frame = tk.LabelFrame(master=initial_page_frame, text="Grammar", height=400)
    grammar_frame.pack(fill=tk.X, side=tk.BOTTOM)
    grammar_frame.pack_propagate(0)

    grammar_str = tk.StringVar()
    grammar_l1 = tk.Label(master=grammar_frame, textvariable=grammar_str, justify='left')
    grammar_l1.pack()

    # Tooltips
    CreateToolTip(add_btn, "Add one or more grammars from your computer to the list box")
    CreateToolTip(remove_btn, "Remove one or more grammars from the list box")
    CreateToolTip(edit_btn, "Edit the selected grammar or perform operations on it")
    CreateToolTip(run_btn, "Construct derivations on the selected grammar")
    CreateToolTip(new_btn, "Create a new grammar file")


def load_page1(file_error, listbox):
    selected = listbox.curselection()
    if not selected:
        file_error.config(text="No file selected. Please select a file")
    elif len(selected) > 1:
        file_error.config(text="Multiple files selected. Please select only one file")
    else:
        clear_widgets(initial_page_frame)
        clear_widgets(page2_frame)
        initial_page_frame.pack_forget()
        page2_frame.pack_forget()
        page1_frame.pack(fill="both")

        # grammar_frame
        grammar_frame = tk.LabelFrame(master=page1_frame, text="Grammar", height=400)
        # grammar_frame.pack_propagate(0)

        grammar_str = tk.StringVar()
        grammar_l1 = tk.Label(master=grammar_frame, textvariable=grammar_str, justify='left')
        grammar_l1.pack()

        error_label = tk.Label(master=page1_frame, fg="red")

        # edit_frame
        frame_name = 'Edit'
        init_combo, rule_combo, rules, rule_entry = create_edit_frame(page1_frame, frame_name, grammar_str, error_label)

        # write selected grammar to temp file
        config = cfg.CFG().read_config(file_variable.get())
        cfg.CFG().write_to_config(config, temp_file)

        # transform frame
        transform_frame = tk.LabelFrame(master=page1_frame, text='Transform', height=155)
        transform_frame.pack(fill='x', expand=1)

        reduce_btn = tk.Button(master=transform_frame, text="Reduce", width=20,
                               command=lambda: functions.reduce(window, file_variable.get(), listbox_items))
        reduce_btn.grid(row=0, column=0, padx=10)

        epsilon_btn = tk.Button(master=transform_frame, text="Remove Epsilon Rules", width=20,
                                command=lambda: functions.remove_epsilon_rules(listbox_items, window, file_variable.get()))
        epsilon_btn.grid(row=1, column=0, pady=10)

        unit_btn = tk.Button(master=transform_frame, text="Remove Unit Rules", width=20,
                             command=lambda: functions.remove_unit_rules(listbox_items, window, file_variable.get()))
        unit_btn.grid(row=0, column=1)

        chomsky_btn = tk.Button(master=transform_frame, text="Chomsky Normal Form", width=20,
                                command=lambda: functions.chomsky_normal_form(window, file_variable.get(), listbox_items))
        chomsky_btn.grid(row=0, column=2, padx=20)

        greibach_btn = tk.Button(master=transform_frame, text="Greibach Normal Form", width=20,
                                 command=lambda: functions.greibach_normal_form(window, file_variable.get(), listbox_items))
        greibach_btn.grid(row=1, column=2)

        first_btn = tk.Button(master=transform_frame, text="FIRST and FOLLOW", width=20,
                              command=lambda: functions.compute_first_and_follow(window, file_variable.get()))
        first_btn.grid(row=0, column=3, padx=10)

        ll1_btn = tk.Button(master=transform_frame, text="LL(1)", width=20,
                            command=lambda: functions.is_ll1(window, file_variable.get()))
        ll1_btn.grid(row=1, column=3, padx=10)

        lr0_btn = tk.Button(master=transform_frame, text="LR(0)", width=20,
                            command=lambda: functions.is_lr0(window, file_variable.get()))
        lr0_btn.grid(row=0, column=4, padx=10)

        lr1_btn = tk.Button(master=transform_frame, text="LR(1)", width=20,
                            command=lambda: functions.is_lr1(window, file_variable.get()))
        lr1_btn.grid(row=1, column=4, padx=10)

        slr_btn = tk.Button(master=transform_frame, text="SLR(1)", width=20,
                            command=lambda: functions.is_slr(window, file_variable.get()))
        slr_btn.grid(row=0, column=5, padx=10)

        # pack widgets
        error_label.pack(pady=10)
        grammar_frame.pack(fill="x")

        # load rule specifications to combo boxes
        execute_submit(grammar_str, init_combo, rule_combo, rules, file_error, rule_entry)

        # Tooltips for transform frame
        CreateToolTip(reduce_btn, "Perform reduction")
        CreateToolTip(epsilon_btn, "Remove epsilon rules")
        CreateToolTip(unit_btn, "Eliminate unit rules")
        CreateToolTip(chomsky_btn, "Convert to Chomsky Normal Form")
        CreateToolTip(greibach_btn, "Convert to Greibach Normal Form")
        CreateToolTip(first_btn, "Compute FIRST and FOLLOW sets")
        CreateToolTip(ll1_btn, "Check if the grammar is LL(1)")
        CreateToolTip(lr0_btn, "Check if the grammar is LR(0)")
        CreateToolTip(lr1_btn, "Check if the grammar is LR(1)")


def load_page2():
    clear_widgets(initial_page_frame)
    clear_widgets(page1_frame)
    initial_page_frame.pack_forget()
    page1_frame.pack_forget()
    page2_frame.pack(fill="both", expand=1)

    grammar = cfg.main(file_variable.get())

    # top_frame
    top_frame = tk.Frame(master=page2_frame)
    top_frame.pack(fill='both', expand=1)

    # topleft_frame
    topleft_frame = tk.Frame(master=top_frame)
    topleft_frame.pack(side="left", fill='both', expand=1)
    topleft_frame.pack_propagate(0)

    # grammar frame
    grammar_frame = tk.LabelFrame(master=topleft_frame, text="Grammar")
    grammar_frame.pack(fill="both", expand=1)
    grammar_frame.pack_propagate(0)
    grammar_text_widget = tk.Text(master=grammar_frame, wrap=tk.NONE, width=15, bg="#d3d3d3")
    grammar_text_widget.pack(fill="both", expand=1)

    functions.create_text_scrollbar(grammar_text_widget)

    grammar_text = cfg.CFG().generate_grammar_text(file_variable.get(), {})
    grammar_text_widget.insert("1.0", grammar_text)
    # grammar_text_widget.tag_configure("highlight", foreground="red")
    # functions.highlight_text(grammar_text_widget)
    grammar_text_widget.config(state=tk.DISABLED)

    # execute_frame
    execute_frame = tk.LabelFrame(master=topleft_frame, text='Execute', height=300)
    execute_frame.pack(fill=tk.X)
    execute_frame.pack_propagate(0)

    # button_frame
    button_frame = tk.Frame(master=execute_frame)
    button_frame.pack(fill='x')

    back_btn = tk.Button(master=button_frame, text="Back", command=lambda: load_initial_page())
    back_btn.pack(side='left', padx=10)

    redo_btn = tk.Button(master=button_frame, text="-->",
                         command=lambda: functions.redo(grammar, input_frame, sentential_str, sentential_canvas, canvas,
                                                        undo_btn, redo_btn),
                         state="disabled")
    redo_btn.pack(side='right', padx=10)

    undo_btn = tk.Button(master=button_frame, text="<--",
                         command=lambda: functions.undo(grammar, input_frame, sentential_str, sentential_canvas, canvas,
                                                        undo_btn, redo_btn),
                         state="disabled")
    undo_btn.pack(side='right')

    # canvas
    execute_canvas = tk.Canvas(execute_frame)
    execute_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=1)

    scrollbar = ttk.Scrollbar(execute_canvas, orient=tk.HORIZONTAL, command=execute_canvas.xview)
    scrollbar.pack(side=tk.BOTTOM, fill=tk.X)

    execute_canvas.configure(xscrollcommand=scrollbar.set)

    input_frame = tk.Frame(execute_canvas)

    # center frame
    canvas_width = execute_canvas.winfo_reqwidth()
    canvas_height = execute_canvas.winfo_reqheight()

    frame_width = input_frame.winfo_reqwidth()
    frame_height = input_frame.winfo_reqheight()

    x = (canvas_width - frame_width) / 2
    y = (canvas_height - frame_height) / 2

    execute_canvas.create_window((x, y), window=input_frame, anchor="nw")

    input_frame.bind("<Configure>", lambda event: functions.update_scrollregion(execute_canvas))

    # tree_frame
    tree_frame = tk.LabelFrame(master=top_frame, text="Derivation Tree")
    tree_frame.pack(side="left", fill='both', expand=1)
    tree_frame.pack_propagate(0)

    canvas = functions.create_scrollbars(tree_frame)

    # sentential_frame
    sentential_frame = tk.LabelFrame(master=page2_frame, text="Sentential Form", height=100)
    sentential_frame.pack(fill="x")
    sentential_frame.pack_propagate(0)

    sentential_sb = ttk.Scrollbar(master=sentential_frame, orient="horizontal")
    sentential_canvas = tk.Canvas(master=sentential_frame, xscrollcommand=sentential_sb.set)
    sentential_sb.config(command=sentential_canvas.xview)
    sentential_sb.pack(side="bottom", fill="x")
    sentential_canvas.pack(fill="both", expand=1)
    sentential_canvas.bind("<MouseWheel>",
                           lambda event: sentential_canvas.xview_scroll(int(-1 * (event.delta / 120)), "units"))

    sentential_str = tk.StringVar()

    # Tooltips
    CreateToolTip(back_btn, "Go to previous page")
    CreateToolTip(undo_btn, "Undo")
    CreateToolTip(redo_btn, "Redo")

    # run
    functions.execute(grammar, grammar.initial_nonterminal, input_frame, sentential_str, sentential_canvas, canvas,
                      undo_btn, redo_btn)


def on_close():
    os.remove(temp_file)
    window.destroy()


# window
window = tk.Tk()
window.protocol("WM_DELETE_WINDOW", on_close)
window.title("CFG")
window.geometry(f'{window.winfo_screenwidth() - 16}x{window.winfo_screenheight() - 80}+0+0')

# global variables
file_variable = tk.StringVar()
listbox_items = []
temp = tempfile.NamedTemporaryFile(delete=False, suffix='.txt')
temp_file = temp.name
temp.close()

# initial_page
initial_page_frame = tk.Frame(master=window)

# create_page
create_page_frame = tk.Frame(master=window)

# page1
page1_frame = tk.Frame(master=window)

# page2
page2_frame = tk.Frame(master=window)

# load initial_page
load_initial_page()

# run
window.mainloop()
