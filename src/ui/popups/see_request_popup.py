from tkinter import *
import tkinter.ttk as ttk


class SeeRequestPopup(Toplevel):
    def __init__(self,root, app, utxo):
        raise Exception("NOT YET IMPLEMENTED")
        super(SeeRequestPopup,self).__init__(root)
        self.app = app
        self.root = root
        self.utxo = utxo
        self.protocol("WM_DELETE_WINDOW", self.close_popup)
        self.geometry(f"1000x600")
        self.title("Utxo Review")
        self.bind('<Escape>', lambda e: self.close_popup)

        Label(self, text='hash').grid(row=0, column=0)
        Label(self, text='address').grid(row=1, column=0)
        Label(self, text='datum').grid(row=2, column=0)
        Label(self, text='datumHash').grid(row=3, column=0)
        Label(self, text='value').grid(row=4, column=0)

        Label(self, text=f'{utxo.hash}').grid(row=0, column=1)
        Label(self, text=f'{utxo.address}').grid(row=1, column=1)
        Label(self, text=f'{utxo.datum}').grid(row=2, column=1)
        Label(self, text=f'{utxo.datumHash}').grid(row=3, column=1)
        Label(self, text=f'{utxo.value}').grid(row=4, column=1)

        Button(self, text='loadExtraData',command=self.loadExtraData).grid(row=5, column=0)

    def loadExtraData(self):
        self.app.decorateUtxoWithBornTransaction(self.utxo)
        Label(self, text=f'Born Transaction Values').grid(row=5, column=0)
        Label(self, text=f'Inputs').grid(row=6, column=0)
        i=7
        bornTx = self.utxo.decorators['bornTx']
        for u in bornTx.input_utxos:
            Label(self, text=f'{u.address}').grid(row=i, column=1)
            Label(self, text=f'{u.value}').grid(row=i, column=2)
            i+=1
        Label(self, text=f'Outputs').grid(row=i, column=0)
        i+=1
        for u in bornTx.output_utxos:
            Label(self, text=f'{u.address}').grid(row=i, column=1)
            Label(self, text=f'{u.value}').grid(row=i, column=2)
            i+=1

    def close_popup(self):
        self.grab_release()
        self.destroy()
