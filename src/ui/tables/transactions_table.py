
from tkinter import *
import tkinter.ttk as ttk

from src.ui.tables.abstract_table import AbstractTable

class TransactionsTable(AbstractTable):
    def getColumnNames(self):
        return ('Transaction','a')

    def getColumnWidths(self):
        return [150,500]

    def doubleClickFn(self, uimanager, tx):
        uimanager.seeTransactionPopup(tx)

    def getItemView(self, tx):
        return ('ABC', 'DEF')

    def getItemDefaultView(self):
        return ('No TX','')
