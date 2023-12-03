import tkinter as tk
from tkinter import ttk
import functions
import cfg


def clear_widgets(frame):
    # select all frame widgets and delete them
    for widget in frame.winfo_children():
        widget.destroy()


def load_page1():
    clear_widgets(page2_frame)
    page2_frame.pack_forget()
    page1_frame.pack(fill="both")

    # select_frame
    select_frame = tk.LabelFrame(master=page1_frame, text="Select A File", height=100, width=500)
    select_frame.pack(fill="x")
    select_frame.pack_propagate(0)

    select_f1 = tk.Frame(master=select_frame)
    select_f1.pack(pady=5)

    select_l1 = tk.Label(master=select_f1, text="File:")
    select_l1.pack(side="left")

    file_variable = tk.StringVar()
    file_textbox = tk.Entry(master=select_f1, textvariable=file_variable, width=100)
    file_textbox.pack(side="left")

    browse_btn = tk.Button(master=select_f1, text="Browse", command=lambda: functions.open_file(file_variable))
    browse_btn.pack(side="left", padx=5)

    select_f2 = tk.Frame(master=select_frame)
    select_f2.pack()

    submit_btn = tk.Button(master=select_f2, text="Submit",
                           command=lambda: functions.submit(file_variable.get(), grammar_str))
    submit_btn.pack(side="left", padx=5)
    # submit_btn.config(state="disabled")

    run_btn = tk.Button(master=select_f2, text="Run", width=5,
                        command=lambda: load_page2(file_variable))
    run_btn.pack(side="left", padx=10)
    # run_btn.config(state="disabled")

    # edit_frame
    edit_frame = tk.LabelFrame(master=page1_frame, text="Edit", height=155, width=500)
    edit_frame.pack(fill="x")
    edit_frame.pack_propagate(0)

    entry_str = tk.StringVar()
    entry = tk.Entry(master=edit_frame, textvariable=entry_str)
    entry.pack(pady=10)

    edit_f1 = tk.Frame(master=edit_frame)
    edit_f1.pack(pady=10)

    choice = tk.StringVar()
    choice.set("nonterminals")
    nt_radio = tk.Radiobutton(edit_f1, text="Non-Terminal", variable=choice, value="nonterminals")
    nt_radio.pack(side='left', padx=10)
    t_radio = tk.Radiobutton(edit_f1, text="Terminal", variable=choice, value="terminals")
    t_radio.pack(side='left', padx=10)
    rule_radio = tk.Radiobutton(edit_f1, text="Rule", variable=choice, value="rules")
    rule_radio.pack(side='left', padx=10)

    edit_f2 = tk.Frame(master=edit_frame)
    edit_f2.pack(pady=10)

    add_btn = tk.Button(master=edit_f2, text="Add", width=7,
                        command=lambda: functions.add(file_variable.get(), choice.get(), entry_str.get(), grammar_str))
    add_btn.pack(side="left", padx=10)

    remove_btn = tk.Button(master=edit_f2, text="Remove",
                           command=lambda: functions.remove(file_variable.get(), choice.get(), entry_str.get(),
                                                            grammar_str))
    remove_btn.pack(side="left", padx=10)

    # grammar_frame
    grammar_frame = tk.LabelFrame(master=page1_frame, text="Grammar", height=400)
    grammar_frame.pack(fill="x")
    # grammar_frame.pack_propagate(0)

    grammar_str = tk.StringVar()
    grammar_l1 = tk.Label(master=grammar_frame, textvariable=grammar_str, justify='left')
    grammar_l1.pack()


def load_page2(file_variable):
    clear_widgets(page1_frame)
    page1_frame.pack_forget()
    page2_frame.pack(fill="both", expand=1)

    grammar = cfg.main(file_variable.get())

    # top_frame
    top_frame = tk.Frame(master=page2_frame, height=window.winfo_screenheight(), width=window.winfo_screenwidth())
    top_frame.pack(fill='both', expand=1)

    # execute_frame
    execute_frame = tk.LabelFrame(master=top_frame, text="Execute", width=window.winfo_screenwidth()/2)
    execute_frame.pack(side="left", fill='y')
    execute_frame.pack_propagate(0)

    # button_frame
    button_frame = tk.Frame(master=execute_frame)
    button_frame.pack(fill='x')

    back_btn = tk.Button(master=button_frame, text="Back", command=lambda: load_page1())
    back_btn.pack(side='left', padx=10)

    redo_btn = tk.Button(master=button_frame, text="-->",
                         command=lambda: functions.redo(output_str, input_str, sentential_str, canvas, execute_e1,
                                                        grammar, execute_btn, undo_btn, redo_btn), state="disabled")
    redo_btn.pack(side='right', padx=10)

    undo_btn = tk.Button(master=button_frame, text="<--",
                         command=lambda: functions.undo(output_str, input_str, sentential_str, canvas, execute_e1, grammar, execute_btn, undo_btn, redo_btn), state="disabled")
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
                                                              execute_e1, grammar, grammar.initial_nonterminal, execute_btn, undo_btn, redo_btn))
    execute_btn.pack(pady=10)

    # tree_frame
    tree_frame = tk.LabelFrame(master=top_frame, text="Derivation Tree", width=window.winfo_screenwidth()/2)
    tree_frame.pack(side="left", fill='y')
    tree_frame.pack_propagate(0)

    tree_sb_vertical = ttk.Scrollbar(master=tree_frame, orient="vertical")
    tree_sb_horizontal = ttk.Scrollbar(master=tree_frame, orient="horizontal")
    canvas = tk.Canvas(master=tree_frame, yscrollcommand=tree_sb_vertical.set, xscrollcommand=tree_sb_horizontal.set)
    tree_sb_vertical.config(command=canvas.yview)
    tree_sb_horizontal.config(command=canvas.xview)
    tree_sb_vertical.pack(side="right", fill="y")
    tree_sb_horizontal.pack(side="bottom", fill="x")
    canvas.pack(fill="both", expand=1)
    canvas.bind_all("<MouseWheel>", functions.on_canvas_scroll)

    # sentential_frame
    sentential_frame = tk.LabelFrame(master=page2_frame, text="Sentential Form", height=50, width=900)
    sentential_frame.pack(fill="x")
    sentential_frame.pack_propagate(0)

    sentential_str = tk.StringVar()
    sentential_l1 = tk.Label(master=sentential_frame, textvariable=sentential_str)
    sentential_l1.pack()


# window
window = tk.Tk()
window.title("CFG")
# window.eval("tk::PlaceWindow . center")
window.geometry(f'{window.winfo_screenwidth() - 16}x{window.winfo_screenheight() - 80}+0+0')

# page1
page1_frame = tk.Frame(master=window)
page1_frame.pack(fill="both")

# page2
page2_frame = tk.Frame(master=window)

# load page1
load_page1()

# run
window.mainloop()
