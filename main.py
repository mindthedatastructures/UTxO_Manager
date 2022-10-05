#!/usr/bin/env python3

from tkinter import *
import tkinter.ttk as ttk
from src.app.app import Application
from src.ui.ui_manager import UIManager
 
class Root(Tk):
    def __init__(self):
        super(Root,self).__init__()
        self.app = Application()
        self.uimanager = UIManager(self.app,self)
        self.uimanager.startUI()
        self.title("UTxO Manager")
        self.minsize(800,600)
    



if __name__ == "__main__":    
    root = Root()
    root.mainloop()
