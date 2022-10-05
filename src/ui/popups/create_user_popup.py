
from tkinter import *
import tkinter.ttk as ttk

from src.model.tx.token_model import TokenModel


class CreateUserPopup(Toplevel):
    def __init__(self, sub_root, app, callback):
        super(CreateUserPopup,self).__init__(sub_root)
        self.app = app
        self.sub_root = sub_root
        self.callback = callback

        self.name_var = StringVar()
        self.name_var.trace("w", self.nameChanged)
        self.error_message_var = StringVar()
        Label(self,text='Name').grid(row=0,column=0)
        Entry(self,textvariable=self.name_var).grid(row=0,column=1)
        Label(self,textvariable=self.error_message_var).grid(row=1,column=0, columnspan=2)
        self.okButton = Button(self,text='Ok', command=self.ok_command)
        self.okButton.grid(row=2,column=0)
        self.okButton.configure(state='disabled')
        Button(self,text='Cancel', command=self.close_popup).grid(row=2,column=1)

    def nameChanged(self, *args):
        if self.name_var.get() != '':
            self.okButton.configure(state='active')
        else:
            self.okButton.configure(state='disabled')
    def ok_command(self):
        if self.name_var.get() in [u.name for u in self.app.getUsers()]:
            self.error_message_var.set(f"Name '{self.name_var.get()}' already exists")
            return
        self.callback(self.name_var.get())
        self.close_popup()

    def close_popup(self):
        self.grab_release()
        self.destroy()
