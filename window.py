import tkinter as tk
import ttkbootstrap as ttk
import functions


# window
window = ttk.Window(themename="darkly")
window.title("Demo")
window.geometry("500x300")

# title
title_label = ttk.Label(master=window, text="Miles to Kilometres", font="Calibre 24 bold")
title_label.pack(pady=40)

# input field
input_frame = ttk.Frame(master=window)
entry_int = tk.IntVar()
entry = ttk.Entry(master=input_frame, textvariable=entry_int)
entry.pack(side="left", padx=10)
input_frame.pack(pady=10)

# button widget
button = ttk.Button(master=input_frame,
                    text="Convert",
                    command=lambda: functions.convert(entry_int, output_string))
button.pack()

# output
output_string = tk.StringVar()
output_label = ttk.Label(master=window,
                         text="Output",
                         font="Calibre 24",
                         textvariable=output_string)
output_label.pack(pady=5)

# run
window.mainloop()
