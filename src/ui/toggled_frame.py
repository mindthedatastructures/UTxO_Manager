
import tkinter as tk
import tkinter.ttk as ttk


class ToggledFrame(tk.Frame):
    def __init__(self, parent, text="", *args, **options):
        tk.Frame.__init__(self, parent, *args, **options)

        self.parent = parent

        self.isExpanded = False
        

        self.title_frame = tk.Frame(self)
        self.title_frame.pack(fill="x", expand=1)

        self.toggle_button = ttk.Button(self.title_frame, width=2, text='+', command=lambda:self.toggle(0), style='Toolbutton')
        self.toggle_button.pack(side="left")

        ttk.Label(self.title_frame, text=text).pack(side="left", fill="x", expand=1)

        self.sub_frame = tk.Frame(self, relief="sunken", borderwidth=1)

        self.pack(fill="x", expand=1, pady=2, padx=2, anchor="n")
        self.toggle(1)


    def toggle(self, value):
        expand = True if value==2 else False if value==1 else not self.isExpanded
        if expand:
            self.sub_frame.forget()
            self.toggle_button.configure(text='+')
        else:
            self.sub_frame.pack(fill="x", expand=1)
            self.toggle_button.configure(text='-')
        self.isExpanded = expand
