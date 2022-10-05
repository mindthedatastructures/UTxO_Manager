
from tkinter import *
import tkinter.ttk as ttk

from src.ui.tables.abstract_table import AbstractTable

class SignedTransactionsTable(AbstractTable):
    def getColumnNames(self):
        return ('Transaction','a')

    def getColumnWidths(self):
        return [150,500]

    def doubleClickFn(self, uimanager, tx):
        None

    def getItemView(self, tx):
        return ('ABC', 'DEF')

    def getItemDefaultView(self):
        return ('No TX','')
