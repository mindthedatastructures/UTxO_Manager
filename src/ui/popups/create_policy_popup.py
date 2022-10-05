
from tkinter import *
import tkinter.ttk as ttk

class CreatePolicyPopup(Toplevel):
    def __init__(self,root, app):
        super(CreatePolicyPopup,self).__init__(root)
        self.app = app
        self.root = root

        self.beforeValue = -1
        width = 250
        self.protocol("WM_DELETE_WINDOW", self.close_popup)
        self.geometry(f"1000x300")
        self.title("Transaction")
        self.grab_set()
        self.bind('<Escape>', lambda e: self.close_popup)

        formFrame = Frame(self)
        formFrame.grid(row=0,column=0)

        ttk.Label(formFrame, text=f"Name").grid(row = 0,column = 0)
        ttk.Label(formFrame, text=f"Used Address\n(if None, it will be generated)").grid(row = 1,column = 0)

        self.before_var = StringVar()
        self.before_var.trace('w', self.before_changed)

        ttk.Label(formFrame, text="Before (current slot + x) (1 slot = 10s)").grid(row=2, column=0)
        ttk.Entry(formFrame, textvariable=self.before_var).grid(row=2, column=1)


        self.createButton = ttk.Button(formFrame, text=f"Create", command=self.createPolicy)
        self.createButton.grid(row = 3,column = 0)
        self.createButton.configure(state='disabled')

        self.cancelButton = ttk.Button(formFrame, text=f"Cancel", command=self.close_popup)
        self.cancelButton.grid(row = 3,column = 1)

        self.name_var = StringVar()
        ttk.Entry(formFrame, textvariable=self.name_var, width=35).grid(row = 0,column = 1)
        self.name_var.trace('w', self.onNameChanged)

        self.addr_var = StringVar()
        asd = ttk.Entry(formFrame, textvariable=self.addr_var, width=45)
        asd.grid(row = 1,column = 1)
        asd.configure(state='disabled')
        self.addr_var.set('Disabled Because we cannot generate key-hash just with address, we need vkey file')

        self.error_var = StringVar()
        ttk.Label(formFrame, textvariable=self.error_var, width=100).grid(row = 4,column = 0, columnspan=2)

        # self.name_var.trace('w', self.onNameChanged)

    def before_changed(self, *args):
        try:
            self.beforeValue = self.app.getTipSlot() + int(self.before_var.get())
        except:
            self.beforeValue = -1

        

    def onNameChanged(self,*args):
        policies = self.app.getPolicies()
        empty = self.name_var.get() == ''
        if not empty and not self.name_var.get() in [p.name for p in policies]:
            self.createButton.configure(state='active')
        else:
            self.createButton.configure(state='disabled')

    def createPolicy(self,*args):
        try:
            if self.addr_var.get()[:5] == 'addr_':
                self.app.createPolicy(self.name_var.get(), self.addr_var.get(), self.beforeValue)
            else:
                self.app.createPolicy(self.name_var.get(), '', self.beforeValue)
            self.root.updatePolicyView()
            self.close_popup()
        except Exception as e:
            print("ERROR")
            print(e)
            self.error_var.set(str(e))
            return

    def close_popup(self):
        self.grab_release()
        self.destroy()
