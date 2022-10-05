
from tkinter import *
import tkinter.ttk as ttk

from src.ui.tables.abstract_table import AbstractTable


class NftToMintTable(AbstractTable):
    def getColumnNames(self):
        return ('Name','Beneficiary', 'Policy Id')

    def getColumnWidths(self):
        return [20,150, 150]

    def doubleClickFn(self, uimanager, model):
        uimanager.seeNftToMintPopup(model)

    def getItemView(self, nft_to_mint):
        return (nft_to_mint.name, nft_to_mint.beneficiary, nft_to_mint.policy.id)

    def getItemDefaultView(self):
        return ('No Nft','')

