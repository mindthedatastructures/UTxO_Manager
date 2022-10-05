
from tkinter import *
import tkinter.ttk as ttk

from src.ui.tables.abstract_table import AbstractTable

class ErrorRequestTable(AbstractTable):
    def getColumnNames(self):
        return ('Utxo','Comments')

    def getColumnWidths(self):
        return [120,250]

    def doubleClickFn(self, uimanager, model):
        uimanager.seeRequestPopup(model)

    def getItemView(self, errorRequest):
        return (f'{errorRequest.utxo.hash[:50]}..', ', '.join(errorRequest.comments))

    def getItemDefaultView(self):
        return ('No Request','')
