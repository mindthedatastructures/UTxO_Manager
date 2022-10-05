
from tkinter import *
import tkinter.ttk as ttk
from enum import Enum

from src.app.app import Application

from src.ui.widget.item_selector import ItemSelector

from src.ui.tabs.config_tab import ConfigTab
from src.ui.tabs.mainuser_tab import MainUserTab
from src.ui.tabs.policies_tab import PoliciesTab
from src.ui.tabs.transactions_tab import TransactionsTab

from src.ui.tables.utxo_table import UtxoTable
from src.ui.tables.policies_table import PoliciesTable
from src.ui.popups.create_transaction.create_transaction_popup import CreateTransactionPopup
from src.ui.popups.create_policy_popup import CreatePolicyPopup
from src.ui.popups.create_user_popup import CreateUserPopup
from src.ui.popups.see_utxos_tx import SeeUtxoPopup
from src.ui.popups.see_transaction_popup import SeeTransactionPopup


class UIManager():
    class Modes(Enum):
        Sandbox = "Sandbox"
        ServiceCounter = "ServiceCounter"

    def __init__(self, app, root):
        self.app = app
        self.root = root
        self.app.mode_changed_listeners.append(self)


    def startUI(self):
        rt = self.root
        rt.title("Cardano")
        rt.minsize(800,600)

        self.mode = UIManager.Modes.ServiceCounter

        self.initTopFrame(rt)
        
        self.initTabs(rt)


    def initTopFrame(self,rt):
        self.topFrame = ttk.Frame(rt, height = 1)
        ttk.Label(self.topFrame,
                text="UTxO Manager",
                font=('Mistral 52')
            ).pack(side="top", fill="x")
        self.topFrame.pack(side="top", fill="x")


    def initTopFrameOLD(self,rt):
        self.topFrame = ttk.Frame(rt, height = 1)
        clockFrame = ttk.Frame(self.topFrame)
        clockFrame.grid(row=0, column=0)

        ttk.Label(clockFrame, text="Next Update In : ", font=('Mistral 12')).grid(row=0, column=0)
        ttk.Label(clockFrame, text="00:00:00", font=('Mistral 16')).grid(row=0, column=1)


        modeFrame = ttk.Frame(self.topFrame)
        modeFrame.grid(row=0, column=1)

        self.mode_var = StringVar()
        ttk.Label(modeFrame, text="Mode ").grid(row=0, column=1)

        ItemSelector.addButton(title='Mode', row=0, column=2, parent1=modeFrame, parent2=rt, var=self.mode_var, options=["Sandbox","ServiceCounter"])

        self.mode_var.trace('w', self.ui_changeMode)


        self.topFrame.pack(side="top", fill="x")


    def initTabs(self,rt):
        self.tabControl = ttk.Notebook(rt)
        self.configTab = ConfigTab(None, self.app, self)
        self.tabControl.insert('end', self.configTab, text='Configs')
        self.tabControl.pack(expand=1, fill="both")

        ## Sandbox
        self.mainuserTab = MainUserTab(None, self.app, self)
        self.policiesTab = PoliciesTab(self.tabControl, self.app, self)

        self.tabControl.insert('end', self.mainuserTab, text='Users')
        self.tabControl.insert('end', self.policiesTab, text='Policies')
        
        self.sandbox_tabs = [self.mainuserTab, self.policiesTab]

        self.refreshTabs()



    def ui_changeMode(self, *args):
        self.mode = self.mode_var.get()
        mode = Application.Modes.Mainnet if self.mode_var.get() == UIManager.Modes.ServiceCounter else Application.Modes.Testnet
        self.app.setMode(mode)

    def updateMode(self):
        self.refreshTabs()

    def refreshTabs(self):
        return

        if self.mode == UIManager.Modes.Sandbox.name:
            [self.tabControl.hide(tab) for tab in self.sc_tabs]
            [self.tabControl.add(tab) for tab in self.sandbox_tabs]
        elif self.mode == UIManager.Modes.ServiceCounter.name:
            [self.tabControl.hide(tab) for tab in self.sandbox_tabs]
            [self.tabControl.add(tab) for tab in self.sc_tabs]

    def addTab(self, tab, name):
        self.tabControl.add(tab, text=name)
        return tab
        
    ## Popup Operations

    def createTransactionPopup(self, sub_root):
        return CreateTransactionPopup(sub_root, self.app)

    def createPolicyPopup(self,sub_root):
        CreatePolicyPopup(sub_root, self.app)

    def createUserPopup(self,sub_root, callback):
        CreateUserPopup(sub_root, self.app, callback)
    
    def seeUtxoTxPopup(self, utxo):
        SeeUtxoPopup(self.root, self.app, utxo)

    def seeRequestPopup(self, request):
        SeeRequestPopup(self.root, self.app, request)

    def seeNftToMintPopup(self, nftToMint):
        SeeNftToMintPopup(self.root, self.app, nftToMint)

    def seeTransactionPopup(self, tx):
        SeeTransactionPopup(self.root, self.app, tx)
