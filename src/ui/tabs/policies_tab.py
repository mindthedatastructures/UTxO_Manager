
from tkinter import *
import tkinter.ttk as ttk

from src.ui.toggled_frame import ToggledFrame
from src.ui.tabs.scrollable_tab import ScrollableTab

from src.ui.tables.policies_table import PoliciesTable

class PoliciesTab(ScrollableTab):
    def __init__(self,tabControl,app, uimanager):
        super(PoliciesTab,self).__init__(tabControl)
        self.app = app
        self.uimanager = uimanager

        self.loadEverything()

    def loadEverything(self):
        self.policiesFrame = Frame(self.viewPort)
        self.policiesFrame.pack(fill='both')

        buttonsFrame = Frame(self.policiesFrame)
        buttonsFrame.pack(fill='x')
        Button(buttonsFrame, text='Create New Policy', command=self.createPolicy).grid(row = 1,column = 0)
        Button(buttonsFrame, text='Update Policy View', command=self.updatePolicyView).grid(row = 1,column = 1)
        
        self.policyTable = PoliciesTable(self.policiesFrame, self.uimanager)
        self.policyTable.pack(fill='both')
        self.updatePolicyView()

    def createPolicy(self, *args):
        self.uimanager.createPolicyPopup(self)

    def updatePolicyView(self, *args):
        self.policyTable.clear()
        [self.policyTable.addItem(p) for p in self.app.getPolicies()]


