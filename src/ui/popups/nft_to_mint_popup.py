from tkinter import *
import tkinter.ttk as ttk

import json

class SeeNftToMintPopup(Toplevel):
    def __init__(self,root, app, nftToMint):
        super(SeeNftToMintPopup,self).__init__(root)
        self.app = app
        self.root = root
        self.nftToMint = nftToMint
        self.protocol("WM_DELETE_WINDOW", self.close_popup)
        self.geometry(f"1000x600")
        self.title("Utxo Review")
        self.bind('<Escape>', lambda e: self.close_popup)

        Label(self, text='name').grid(row=0, column=0)
        Label(self, text='policyID').grid(row=1, column=0)
        Label(self, text='beneficiary').grid(row=2, column=0)
        Label(self, text='has been minted').grid(row=3, column=0)
        Label(self, text='metadata content').grid(row=3, column=0)

        Label(self, text=f'{nftToMint.name}').grid(row=0, column=1)
        Label(self, text=f'{nftToMint.policy.id}').grid(row=1, column=1)
        Label(self, text=f'{nftToMint.beneficiary}').grid(row=2, column=1)
        Label(self, text=f'NO').grid(row=3, column=1)
        Label(self, text=f'{json.dumps(self.app.service_counter_manager.getMetadataContent(nftToMint.name), indent=2)}').grid(row=3, column=1)

        Button(self, text='loadExtraData',command=self.loadExtraData).grid(row=5, column=0)

    def loadExtraData(self):
        raise NotImplementedError()
        # self.app.decorateUtxoWithBornTransaction(self.utxo)
        # Label(self, text=f'Born Transaction Values').grid(row=5, column=0)
        # Label(self, text=f'Inputs').grid(row=6, column=0)
        # i=7
        # bornTx = self.utxo.decorators['bornTx']
        # for u in bornTx.input_utxos:
        #     Label(self, text=f'{u.address}').grid(row=i, column=1)
        #     Label(self, text=f'{u.value}').grid(row=i, column=2)
        #     i+=1
        # Label(self, text=f'Outputs').grid(row=i, column=0)
        # i+=1
        # for u in bornTx.output_utxos:
        #     Label(self, text=f'{u.address}').grid(row=i, column=1)
        #     Label(self, text=f'{u.value}').grid(row=i, column=2)
        #     i+=1

    def close_popup(self):
        self.grab_release()
        self.destroy()
