
from tkinter import *
import tkinter.ttk as ttk

from src.ui.tables.abstract_table import AbstractTable

class ValidRequestTable(AbstractTable):

    def getColumnNames(self):
        return ('Nft Requested','Value Paid', 'Contains Tokens', 'Beneficiary', 'Comments')

    def getColumnWidths(self):
        return [120, 120, 20, 150, 500]

    def doubleClickFn(self, uimanager, model):
        uimanager.seeRequestPopup(model)

    def getItemView(self, utxo_model):
        return (validRequest.nft_requested, validRequest.value_sent/10.0**6, str(validRequest.contains_other_tokens),validRequest.beneficiary, validRequest.comments)

    def getItemDefaultView(self):
        return ('No Request','','','','')

