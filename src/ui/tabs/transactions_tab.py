
from tkinter import *
import tkinter.ttk as ttk

from src.ui.toggled_frame import ToggledFrame
from src.ui.tabs.scrollable_tab import ScrollableTab

from src.ui.tables.transactions_table import TransactionsTable

class TransactionsTab(ScrollableTab):
    def __init__(self,tabControl,app, uimanager):
        super(TransactionsTab,self).__init__(tabControl)
        self.app = app
        self.uimanager = uimanager

        self.loadEverything()

    def loadEverything(self):
        self.txTable = TransactionsTable(self.viewPort, self.uimanager)
        self.txTable.pack(fill='both', expand = 1)
        self.updatePolicyView()

    def createPolicy(self, *args):
        self.uimanager.createPolicyPopup(self)

    def updatePolicyView(self, *args):
        self.txTable.clear()


