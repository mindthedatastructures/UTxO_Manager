
from tkinter import *
import tkinter.ttk as ttk

from src.ui.tables.abstract_table import AbstractTable


class UtxoTable(AbstractTable):
    def getColumnNames(self):
        return ('Hash','Adas', 'Tokens')

    def getColumnWidths(self):
        return [550,150,500]

    def doubleClickFn(self, uimanager, model):
        uimanager.seeUtxoTxPopup(model)

    def getItemView(self, utxo_model):
        return (utxo_model.hash, utxo_model.value['lovelace']/10.0**6, UtxoTable.createTokenString(utxo_model.value))

    def getItemDefaultView(self):
        return ('No Utxos','','')

    def createTokenString(value):
        # first = True
        return ', '.join([f'{k[:15]}..:{v}' for k,v in list(filter(lambda x: x[0] != 'lovelace', value.items()))])
