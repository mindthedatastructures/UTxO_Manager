from tkinter import *
import tkinter.ttk as ttk

from src.ui.tabs.scrollable_tab import ScrollableTab

class SeeUtxoPopup(Toplevel):
    def __init__(self,root, app, utxo):
        super(SeeUtxoPopup,self).__init__(root)
        self.app = app
        self.root = root
        self.utxo = utxo
        self.protocol("WM_DELETE_WINDOW", self.close_popup)
        self.geometry(f"1000x600")
        self.title("Utxo Review")
        self.bind('<Escape>', lambda e: self.close_popup)

        scroll = ScrollableTab(self)
        scroll.pack(fill='both', expand=1)

        self.frame = Frame(scroll.viewPort)
        self.frame.pack(fill='both', expand=1)

        Label(self.frame, text='hash').grid(row=0, column=0)
        Label(self.frame, text='address').grid(row=1, column=0)
        Label(self.frame, text='datum').grid(row=2, column=0)
        Label(self.frame, text='datumHash').grid(row=3, column=0)
        Label(self.frame, text='value').grid(row=4, column=0)


        self.hash_var = StringVar()
        self.address_var = StringVar()


        Entry(self.frame, width=100, textvariable=self.hash_var).grid(row=0, column=1)
        Entry(self.frame, width=100, textvariable=self.address_var).grid(row=1, column=1)
        self.hash_var.set(f'{utxo.hash}')
        self.address_var.set(f'{utxo.address}')


        Label(self.frame, text=f'{utxo.datum}').grid(row=2, column=1)
        Label(self.frame, text=f'{utxo.datumHash}').grid(row=3, column=1)
        Label(self.frame, text=f'{utxo.value}').grid(row=4, column=1)

        Button(self.frame, text='loadExtraData',command=self.loadExtraData).grid(row=5, column=0)

    def loadExtraData(self):
        self.app.decorateUtxoWithBornTransaction(self.utxo)
        Label(self.frame, text=f'Born Transaction Values').grid(row=3, column=0)
        Label(self.frame, text=f'Inputs').grid(row=7, column=0)
        i=8
        bornTx = self.utxo.decorators['bornTx']
        for u in bornTx.input_utxos:
            Label(self.frame, text=f'{u.address}').grid(row=i, column=1)
            Label(self.frame, text=f'{u.value}').grid(row=i, column=2)
            i+=1
        Label(self.frame, text=f'Outputs').grid(row=i, column=0)
        i+=1
        for u in bornTx.output_utxos:
            Label(self.frame, text=f'{u.address}').grid(row=i, column=1)
            Label(self.frame, text=f'{u.value}').grid(row=i, column=2)
            i+=1

    def close_popup(self):
        self.grab_release()
        self.destroy()
