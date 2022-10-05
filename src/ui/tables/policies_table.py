
from tkinter import *
import tkinter.ttk as ttk

from src.ui.tables.abstract_table import AbstractTable

class PoliciesTable(AbstractTable):
    def getColumnNames(self):
        return ('Policy Name','Policy id')

    def getColumnWidths(self):
        return [150,500]

    def doubleClickFn(self, uimanager, model):
        None

    def getItemView(self, policy_model):
        return (policy_model.name, policy_model.id)

    def getItemDefaultView(self):
        return ('No Policy','')

