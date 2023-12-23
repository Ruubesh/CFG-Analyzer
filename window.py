import tkinter as tk
from tkinter import ttk
import functions
import cfg


def clear_widgets(frame):
    for widget in frame.winfo_children():
        widget.destroy()


def execute_submit(grammar_str, init_combo, rule_combo, rules, file_error):
    try:
        file_error.pack_forget()
        functions.submit(file_variable.get(), grammar_str, init_combo, rule_combo, rules)
    except Exception as e:
        file_error.config(text=e)
        file_error.pack(pady=5)
        return e


def execute_run():
    try:
        load_page2()
    except KeyError as k:
        load_page1(f"Invalid file {k}")
    except Exception as e:
        load_page1(e)


def load_page1(error_text=''):
    clear_widgets(page2_frame)
    page2_frame.pack_forget()
    page1_frame.pack(fill="both")

    # select_frame
    select_frame = tk.LabelFrame(master=page1_frame, text="Select A File", height=110, width=500)
    select_frame.pack(fill="x")
    select_frame.pack_propagate(0)

    select_f1 = tk.Frame(master=select_frame)
    select_f1.pack(pady=5)

    select_l1 = tk.Label(master=select_f1, text="File:")
    select_l1.pack(side="left")

    file_textbox = tk.Entry(master=select_f1, textvariable=file_variable, width=100)
    file_textbox.pack(side="left")

    browse_btn = tk.Button(master=select_f1, text="Browse", command=lambda: functions.open_file(file_variable))
    browse_btn.pack(side="left", padx=5)

    select_f2 = tk.Frame(master=select_frame)
    select_f2.pack()

    submit_btn = tk.Button(master=select_f2, text="Submit",
                           command=lambda: execute_submit(grammar_str, init_combo, rule_combo, rules, file_error))
    submit_btn.pack(side="left", padx=5)

    run_btn = tk.Button(master=select_f2, text="Run", width=5,
                        command=lambda: execute_run())
    run_btn.pack(side="left", padx=10)

    file_error = tk.Label(master=select_frame, text=error_text, fg="red")
    file_error.pack(pady=5)

    # edit_frame
    edit_frame = tk.LabelFrame(master=page1_frame, text="Edit", height=155)
    edit_frame.pack(fill="x")
    edit_frame.pack_propagate(0)

    nt_frame = tk.Frame(master=edit_frame, height=155, width=edit_frame.winfo_width()/2)
    nt_frame.pack(side='left', fill='x', expand=1, padx=100)

    entry_str = tk.StringVar()
    entry = tk.Entry(master=nt_frame, textvariable=entry_str)
    entry.pack(pady=10)

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

    add_btn = tk.Button(master=edit_f2, text="Add", width=7,
                        command=lambda: functions.add(file_variable.get(), choice.get(), entry_str.get(), grammar_str, init_combo, rule_combo, rules, error_label))
    add_btn.pack(side="left", padx=10)

    remove_btn = tk.Button(master=edit_f2, text="Remove",
                           command=lambda: functions.remove(file_variable.get(), choice.get(), entry_str.get(),
                                                            grammar_str, init_combo, rule_combo, rules, error_label))
    remove_btn.pack(side="left", padx=10)

    rule_frame = tk.Frame(master=edit_frame, height=155, width=edit_frame.winfo_width()/2)
    rule_frame.pack(side="right", fill='both', expand=1)

    rule_l1 = tk.Label(master=rule_frame, text="Initial Nonterminal:")
    rule_l1.grid(row=0, column=0, pady=10)

    init_val = tk.StringVar()
    nt_options = []
    init_combo = ttk.Combobox(master=rule_frame, textvariable=init_val, state="readonly", values=nt_options)
    init_combo.grid(row=0, column=1)

    rule_l2 = tk.Label(master=rule_frame, text="Rules:")
    rule_l2.grid(row=1, column=0, sticky='e', pady=12)

    rule_val = tk.StringVar()
    rule_options = []
    rule_combo = ttk.Combobox(master=rule_frame, textvariable=rule_val, state="readonly", values=rule_options)
    rule_combo.grid(row=1, column=1)
    rule_combo.bind("<<ComboboxSelected>>", lambda event: functions.on_select_rule(file_variable.get(), rule_val, rules))

    rules = tk.StringVar()
    rule_entry = tk.Entry(master=rule_frame, width=30, textvariable=rules)
    rule_entry.grid(row=1, column=2, padx=10)

    save_btn = tk.Button(master=rule_frame, text="Save", command=lambda: functions.save_to_config(file_variable.get(), rule_val, rules, init_val, grammar_str, error_label))
    save_btn.grid(row=2, columnspan=3, pady=10)

    error_label = tk.Label(master=page1_frame, fg="red")
    error_label.pack()

    # grammar_frame
    grammar_frame = tk.LabelFrame(master=page1_frame, text="Grammar", height=400)
    grammar_frame.pack(fill="x")
    # grammar_frame.pack_propagate(0)

    grammar_str = tk.StringVar()
    grammar_l1 = tk.Label(master=grammar_frame, textvariable=grammar_str, justify='left')
    grammar_l1.pack()


def load_page2():
    clear_widgets(page1_frame)
    page1_frame.pack_forget()
    page2_frame.pack(fill="both", expand=1)

    grammar = cfg.main(file_variable.get())

    # top_frame
    top_frame = tk.Frame(master=page2_frame)
    top_frame.pack(fill='both', expand=1)

    # execute_frame
    execute_frame = tk.LabelFrame(master=top_frame, text="Execute")
    execute_frame.pack(side="left", fill='both', expand=1)
    execute_frame.pack_propagate(0)

    # button_frame
    button_frame = tk.Frame(master=execute_frame)
    button_frame.pack(fill='x')

    back_btn = tk.Button(master=button_frame, text="Back", command=lambda: load_page1())
    back_btn.pack(side='left', padx=10)

    redo_btn = tk.Button(master=button_frame, text="-->",
                         command=lambda: functions.redo(output_str, input_str, sentential_str, canvas, execute_e1,
                                                        grammar, execute_btn, undo_btn, redo_btn, sentential_canvas), state="disabled")
    redo_btn.pack(side='right', padx=10)

    undo_btn = tk.Button(master=button_frame, text="<--",
                         command=lambda: functions.undo(output_str, input_str, sentential_str, canvas, execute_e1, grammar, execute_btn, undo_btn, redo_btn, sentential_canvas), state="disabled")
    undo_btn.pack(side='right')

    output_str = tk.StringVar()
    execute_l1 = tk.Label(master=execute_frame, textvariable=output_str, justify='left')
    execute_l1.pack()

    input_str = tk.StringVar()
    options = [grammar.initial_nonterminal]
    execute_e1 = ttk.Combobox(master=execute_frame, textvariable=input_str, values=options, state='readonly')
    execute_e1.current(0)
    execute_e1.pack()

    execute_btn = tk.Button(master=execute_frame, text="Execute",
                            command=lambda: functions.execute(output_str, input_str, sentential_str, canvas,
                                                              execute_e1, grammar, grammar.initial_nonterminal, execute_btn, undo_btn, redo_btn, sentential_canvas))
    execute_btn.pack(pady=10)

    # tree_frame
    tree_frame = tk.LabelFrame(master=top_frame, text="Derivation Tree")
    tree_frame.pack(side="left", fill='both', expand=1)
    tree_frame.pack_propagate(0)

    tree_sb_vertical = ttk.Scrollbar(master=tree_frame, orient="vertical")
    tree_sb_horizontal = ttk.Scrollbar(master=tree_frame, orient="horizontal")
    canvas = tk.Canvas(master=tree_frame, yscrollcommand=tree_sb_vertical.set, xscrollcommand=tree_sb_horizontal.set)
    tree_sb_vertical.config(command=canvas.yview)
    tree_sb_horizontal.config(command=canvas.xview)
    tree_sb_vertical.pack(side="right", fill="y")
    tree_sb_horizontal.pack(side="bottom", fill="x")
    canvas.pack(fill="both", expand=1)
    canvas.bind("<MouseWheel>", lambda event: canvas.yview_scroll(int(-1 * (event.delta / 120)), "units"))
    canvas.bind("<Control MouseWheel>", lambda event: canvas.xview_scroll(int(-1 * (event.delta / 120)), "units"))

    # sentential_frame
    sentential_frame = tk.LabelFrame(master=page2_frame, text="Sentential Form", height=100)
    sentential_frame.pack(fill="x")
    sentential_frame.pack_propagate(0)

    sentential_sb = ttk.Scrollbar(master=sentential_frame, orient="horizontal")
    sentential_canvas = tk.Canvas(master=sentential_frame, xscrollcommand=sentential_sb.set)
    sentential_sb.config(command=sentential_canvas.xview)
    sentential_sb.pack(side="bottom", fill="x")
    sentential_canvas.pack(fill="both", expand=1)
    sentential_canvas.bind("<MouseWheel>", lambda event: sentential_canvas.xview_scroll(int(-1 * (event.delta / 120)), "units"))

    sentential_str = tk.StringVar()


# window
window = tk.Tk()
window.title("CFG")
window.geometry(f'{window.winfo_screenwidth() - 16}x{window.winfo_screenheight() - 80}+0+0')

# global variables
file_variable = tk.StringVar()

# page1
page1_frame = tk.Frame(master=window)
page1_frame.pack(fill="both")

# page2
page2_frame = tk.Frame(master=window)

# load page1
load_page1()

# run
window.mainloop()
