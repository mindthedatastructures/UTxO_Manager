from tkinter import *
import tkinter.ttk as ttk
from src.model.tx.token_model import TokenModel
from src.ui.widget.item_selector import ItemSelector

from src.model.tx.output_utxo_model import OutputUtxoModel

class AddOutputUtxoPopup(Toplevel):
    def __init__(self,root, app):
        super(AddOutputUtxoPopup,self).__init__(root)
        self.app = app
        self.root = root
        self.bind('<Escape>', lambda e: self.close_popup)

        self.output_utxo_model = OutputUtxoModel()

        self.lock = False

        self.protocol("WM_DELETE_WINDOW", self.cancelAddOutputUtxo)
        self.geometry(f"1100x250")
        self.title("Add Output Utxo to Transaction")
        self.grab_set()


        ttk.Label(self, text=f"Address").grid(row = 0,column = 0)

        self.addressFrame= Frame(self)
        self.addressFrame.grid(row=0,column=1)

        self.mode_var = IntVar()
        self.mode_var.trace('w', self.ui_addressModeChanged)

        Radiobutton(self.addressFrame, text="", padx = 20, variable=self.mode_var, value=0).grid(row=0,column=0)
        Radiobutton(self.addressFrame, text="", padx = 20, variable=self.mode_var, value=1).grid(row=1,column=0)

        self.users_var = StringVar()
        self.options = self.app.getUsers()

        (self.selectUserLabel, self.selectUserButton) = ItemSelector.addButton(
            title='User', 
            row=0, column=1, 
            parent1=self.addressFrame, parent2=self.addressFrame, 
            var=self.users_var,
            options=[f'{i}:{user.name}:{user.addr}' for i, user in enumerate(self.app.getUsers())]
        )

        self.address_var = StringVar()
        self.entry_address = Entry(self.addressFrame, textvariable=self.address_var, width = 100)
        self.entry_address.grid(row=1,column=1)
        self.address_var.trace('w', self.addressChanged)
        self.qr_button = Button(self.addressFrame, text='QR', command=self.openQR, width = 1)
        self.qr_button.grid(row=1,column=2)


        self.users_var.trace('w', self.onDataChanged)

        ttk.Label(self, text=f"Amount (in lovelace)").grid(row = 1,column = 0)

        self.amount_var = StringVar()
        self.amount_var.trace('w', self.onDataChanged)
        self.amount = Entry(self, text=self.amount_var, width= 40).grid(row = 1,column = 1)

        ttk.Label(self, text=f"Amount (in ADA)").grid(row = 2,column = 0)

        self.amount_in_ada_var = StringVar()
        self.amount_in_ada_var.trace('w', self.onAdaDataChanged)
        self.amount = Entry(self, text=self.amount_in_ada_var, width= 40).grid(row = 2,column = 1)

        self.token_name_var = StringVar()
        self.tokens_label_var = StringVar()
        self.token_amount_var = StringVar()
        self.token_to_remove_var = StringVar()

        tokenOptions = self.initTokenOptions()


        ttk.Label(self, text=f"Tokens").grid(row = 3,column = 0)

        tokensFrame =Frame(self, width=200, height=300)
        tokensFrame.grid(row=3,column=1)

        ttk.Label(tokensFrame, textvariable=self.tokens_label_var).grid(row = 0,column = 0)
        self.tokenOptionsFrame = Frame(tokensFrame)
        self.tokenOptionsFrame.grid(row=0,column=1)
        self.addTokenButton = ttk.Button(self.tokenOptionsFrame, text="Add Token", command=self.addToken)
        self.addTokenButton.grid(row = 0,column = 0)
        self.removeTokenButton = ttk.Button(self.tokenOptionsFrame, text="Remove Token", command=self.removeToken)
        self.removeTokenButton.grid(row = 1,column = 0)
        self.removeTokenButton.configure(state='disabled')


        addingframe = Frame(self.tokenOptionsFrame)
        addingframe.grid(row=0,column=1)
        ttk.Label(addingframe, text='Name').grid(row = 0,column = 0)
        ttk.OptionMenu(addingframe, self.token_name_var, *[f'{i}:{t}' for i,t in enumerate(tokenOptions)]).grid(row = 0,column = 1)

        ttk.Label(addingframe, text='Amount').grid(row = 1,column = 0)
        ttk.Entry(addingframe, textvariable=self.token_amount_var).grid(row = 1,column = 1)

        self.token_name_var.trace('w', lambda *args:self.updateTokenButtonsState())
        self.token_amount_var.trace('w', lambda *args:self.updateTokenButtonsState())
        self.token_to_remove_var.trace('w', lambda *args:self.updateTokenButtonsState())

        self.tokens_to_remove_dropdown = None
        self.updateRemoveTokenDropdown()

        self.okButton = Button(self, text='Add Output Utxo', command=self.submitAddOutputUtxo)
        self.okButton.grid(row = 5,column = 0)
        self.okButton.configure(state='disabled')
        cancelButton = Button(self, text='Cancel', command=self.cancelAddOutputUtxo)
        cancelButton.grid(row = 5,column = 1)

        self.manyTimes_var = StringVar()
        Entry(self, textvariable=self.manyTimes_var, width = 3).grid(row = 5,column = 2)
        Button(self, text='AddManyTimes', command=self.addManyTimes).grid(row = 6,column = 2)


        self.mode_var.set(0)


    def addManyTimes(self, *args):
        try:
            am = int(self.manyTimes_var.get())
            [self.root.addOutputUtxo(self.output_utxo_model.copy()) for i in range(am)]
            self.grab_release()
            self.destroy()
        except:
            None

    def addressChanged(self, *args):
        print("Nononasd")

    def ui_addressModeChanged(self, *args):
        if self.mode_var.get() == 0:
            self.selectUserLabel.configure(state='active')
            self.selectUserButton.configure(state='active')
            self.entry_address.configure(state='disabled')
            self.qr_button.configure(state='disabled')
        else:
            self.selectUserLabel.configure(state='disabled')
            self.selectUserButton.configure(state='disabled')
            self.entry_address.configure(state='normal')
            self.qr_button.configure(state='active')

    def openQR(self):
        import cv2
        cap = cv2.VideoCapture(0)
        detector = cv2.QRCodeDetector()
        close_window = False
        while True:
            ret_val, img = cap.read()
            cv2.imshow('QR Reader - Press ESC to quit', img)
            data, bbox, _ = detector.detectAndDecode(img)
            if data:
                a=data
                break
            if cv2.waitKey(1) == 27: 
                close_window = True
                break
        
        if close_window:
            print("window closed")
        else:
            self.address_var.set(str(a))

    def initTokenOptions(self):
        tokens= []
        for u in self.root.transaction.input_utxos:
            print(u.value)
            for k,v in u.value.items():
                if k != 'lovelace':
                    for token, value in v.items():
                        tokens.append(f'{k}:{token}')
        if self.root.transaction.mint != None:
            for t in self.root.transaction.mint.tokens:
                tokens.append(f"{t['token'].policy_id}:{t['token'].name}")
        print(len(tokens))
        return tokens


    def addToken(self):
        parts = self.token_name_var.get().split(':')
        token = TokenModel(parts[2],parts[1])
        self.output_utxo_model.addToken(token, int(self.token_amount_var.get()))
        self.updateRemoveTokenDropdown()
        self.token_amount_var.set('')
        self.updateTokenView()
        self.updateTokenButtonsState()

    def removeToken(self):
        token = self.output_utxo_model.tokens[int(self.token_to_remove_var.get().split(':')[0])]
        self.output_utxo_model.tokens.remove(token)
        self.updateRemoveTokenDropdown()
        self.token_to_remove_var.set('')
        self.updateTokenView()
        self.updateTokenButtonsState()

    def updateRemoveTokenDropdown(self):
        if self.tokens_to_remove_dropdown != None:
            self.tokens_to_remove_dropdown.destroy()
        if len(self.output_utxo_model.tokens) == 0:
            options = ['']
        else:
            options = [f"{i}:{t['token'].name}" for i,t in enumerate(self.output_utxo_model.tokens)]
        self.tokens_to_remove_dropdown = OptionMenu(self.tokenOptionsFrame, self.token_to_remove_var, *options)
        self.tokens_to_remove_dropdown.grid(row = 1,column = 1)

    def updateTokenButtonsState(self):
        if(self.token_name_var.get() != ''):
            try:
                int(self.token_amount_var.get())
                self.addTokenButton.configure(state='active')
            except:
                self.addTokenButton.configure(state='disabled')
        else:
            self.addTokenButton.configure(state='disabled')

        if self.token_to_remove_var.get() == '':
            self.removeTokenButton.configure(state='disabled')
        else:
            self.removeTokenButton.configure(state='active')


    def updateTokenView(self):
        self.tokens_label_var.set('\n'.join([f"{i}:{t['token'].toDisplayableString()}:{t['value']}" for i,t in enumerate(self.output_utxo_model.tokens)]))

    def cancelAddOutputUtxo(self):
        self.grab_release()
        self.destroy()

    def onDataChanged(self, *args):
        if not self.lock:
            self.lock = True
            try:
                ada = str(float(int(self.amount_var.get())/(1.0*10**6)))
                self.amount_in_ada_var.set(ada)
                self.updateButtons()
            except:
                None
            self.newValuesToModel()
            self.lock=False


    def newValuesToModel(self):
        try:
            self.output_utxo_model.value = int(self.amount_var.get())
        except:
            None
        if self.mode_var.get() == 0:
            if self.users_var.get() != '':
                user = self.options[int(self.users_var.get().split(':')[0])]
                self.output_utxo_model.name = user.name
                self.output_utxo_model.address = user.addr
        else:
            self.output_utxo_model.address = self.entry_address.get()
            self.output_utxo_model.name = "NoName"


    def onAdaDataChanged(self, *args):
        if not self.lock:
            self.lock = True
            try:
                lvlc = str(int(float(self.amount_in_ada_var.get())*10**6))
                self.amount_var.set(lvlc)
                self.updateButtons()
            except:
                None
            self.newValuesToModel()
            self.lock=False

    def updateButtons(self):
        try:
            int(self.amount_var.get())
            if self.mode_var.get() == 0:
                if self.users_var.get() != '':
                    self.okButton.configure(state='active')
                else:
                    self.okButton.configure(state='disabled')
            else:
                if self.address_var.get() != '':
                    self.okButton.configure(state='active')
                else:
                    self.okButton.configure(state='disabled')

        except:
            self.okButton.configure(state='disabled')
            return

    def submitAddOutputUtxo(self, *args):
        self.root.addOutputUtxo(self.output_utxo_model)
        self.grab_release()
        self.destroy()
