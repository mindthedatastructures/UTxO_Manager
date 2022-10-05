
from tkinter import *
import tkinter.ttk as ttk


from src.ui.widget.item_selector import ItemSelector

class AddInputUtxoPopup(Toplevel):
    def __init__(self,root, app):
        super(AddInputUtxoPopup,self).__init__(root)
        self.app = app
        self.root = root
        self.bind('<Escape>', lambda e: self.close_popup)

        self.protocol("WM_DELETE_WINDOW", self.close_popup)
        self.geometry(f"800x250")
        self.title("Add Input Utxo to Transaction")
        self.grab_set()

        self.utxos_options = []
        self.utxos_options_string = []

        ttk.Label(self, text=f"Address:").grid(row = 0,column = 0)
        self.users_var = StringVar()

        ItemSelector.addButton(
            title='User', 
            row=0, column=1, 
            parent1=self, parent2=self, 
            var=self.users_var,
            options=[user.uiString() for user in self.app.getUsers()]
        )

        self.users_var.trace('w', self.onAddressChanged)

        self.selected_utxo_var = StringVar()
        self.selected_utxo_var.trace('w', self.onUtxoChanged)

        ItemSelector.addButton(
            title='Utxos', 
            row=1, column=1, 
            parent1=self, parent2=self, 
            var=self.selected_utxo_var,
            options=self.utxos_options_string
        )

        ttk.Label(self, text=f"Utxo").grid(row = 1,column = 0)

        buttonsFrame = Frame(self)
        buttonsFrame.grid(row = 4,column = 0, columnspan=2)

        self.okButton = Button(buttonsFrame, text='Add Utxo', command=self.submitAddInputUtxo)
        self.okButton.grid(row = 0,column = 1)
        self.okButton.configure(state='disabled')
        cancelButton = Button(buttonsFrame, text='Cancel', command=self.close_popup)
        cancelButton.grid(row = 0,column = 2)

    def close_popup(self):
        self.grab_release()
        self.destroy()

    def onUtxoChanged(self, *args):
        if self.selected_utxo_var.get() != '':
            self.okButton.configure(state='active')

    def onAddressChanged(self, *args):
        while len(self.utxos_options_string) > 0:
            self.utxos_options_string.pop(0)

        self.utxos_options = self.app.getUtxos(self.users_var.get().split(':')[1])
        self.filteredAlreadyIncludedUtxos()
        [self.utxos_options_string.append(f'{i}:{u.uiString()}') for i,u in enumerate(self.utxos_options)]
        self.selected_utxo_var.set('')
        self.okButton.configure(state='disabled')

    def submitAddInputUtxo(self, *args):
        input_utxo = self.utxos_options[int(self.selected_utxo_var.get().split(':')[0])]
        user = list(filter(lambda u: u.addr == input_utxo.address, self.app.getUsers()))[0]
        input_utxo.decorators['user'] = user
        self.root.addInputUtxo(input_utxo)
        self.grab_release()
        self.destroy()

    def filteredAlreadyIncludedUtxos(self):
        hashes = [u.hash for u in self.root.transaction.input_utxos]
        toRemove = list(filter(lambda x: x.hash in hashes, self.utxos_options))
        [self.utxos_options.remove(u) for u in toRemove]
