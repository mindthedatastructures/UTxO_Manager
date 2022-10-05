from tkinter import *
import tkinter.ttk as ttk

from src.ui.tabs.scrollable_tab import ScrollableTab

class SeeTransactionPopup(Toplevel):
    def __init__(self,root, app, tx):
        super(SeeTransactionPopup,self).__init__(root)
        self.protocol("WM_DELETE_WINDOW", self.close_popup)
        self.geometry(f"1000x600")
        self.title("Transaction Review")
        self.bind('<Escape>', lambda e: self.close_popup)


        self.app = app
        self.root = root
        self.tx = tx

        scroll = ScrollableTab(self)
        scroll.pack(fill='both', expand=1)


        self.frame = Frame(scroll.viewPort)
        self.frame.pack(fill='both', expand=1)

        Label(self.frame, text=f'Inputs').grid(row=0, column=0)
        i=1
        for u in tx.input_utxos:
            Label(self.frame, text=f'{u.address}').grid(row=i, column=1)
            Label(self.frame, text=f'{u.value}').grid(row=i, column=2)
            i+=1
        Label(self.frame, text=f'Outputs').grid(row=i, column=0)
        i+=1
        for u in tx.output_utxos:
            Label(self.frame, text=f'{u.address}').grid(row=i, column=1)
            Label(self.frame, text=f'{u.value}').grid(row=i, column=2)
            i+=1

    def close_popup(self):
        self.grab_release()
        self.destroy()
