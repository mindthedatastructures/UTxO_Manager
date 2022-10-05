
from tkinter import *
import tkinter.ttk as ttk

from src.ui.toggled_frame import ToggledFrame
from src.ui.tabs.scrollable_tab import ScrollableTab

from src.ui.widget.item_selector import ItemSelector

from src.ui.tables.nft_to_mint_table import NftToMintTable

from src.model.tx.token_model import TokenModel
from src.model.tx.output_utxo_model import OutputUtxoModel


class MintNftTab(ScrollableTab):
    global_variable_label_error = 0
    global_variable_label_error2 = 0
    def __init__(self,tabControl,app, uimanager):
        super(MintNftTab,self).__init__(tabControl)
        self.app = app
        self.uimanager = uimanager

        self.loadEverything()


    def loadEverything(self):
        frame = Frame(self.viewPort)
        frame.pack(fill='both')

        self.buttonsFrame = Frame(frame)
        self.buttonsFrame.pack(fill='x')

        self.count_nft_var= StringVar()
        self.beneficiary_var= StringVar()
        self.error_var= StringVar()
        self.error2_var= StringVar()

        self.selected_policy_var= StringVar()
        Label(self.buttonsFrame, text="Count Nfts To Generate").grid(row=0, column=0)
        Entry(self.buttonsFrame, textvariable=self.count_nft_var, width = 3).grid(row=0, column=1)
        Label(self.buttonsFrame, text="Beneficiary").grid(row=0, column=2)
        Entry(self.buttonsFrame, textvariable=self.beneficiary_var).grid(row=0, column=3)
        Button(self.buttonsFrame, text="Load Treasury", command=self.loadTreasuryBeneficiary).grid(row=1, column=3)

        Label(self.buttonsFrame, text="Policy").grid(row=0, column=4)
        self.updatePolicies()

        ItemSelector.addButton(title='Policies', row=0, column=5, parent1=self.buttonsFrame, parent2=self.buttonsFrame, var=self.selected_policy_var, options=[f'{i}:{p.name}' for i, p in enumerate(self.policies)] if len(self.policies)>0 else [''])
        Button(self.buttonsFrame, text="Update", command=self.updatePolicies).grid(row=1, column=5)


        Button(self.buttonsFrame, text = 'Generate', command=self.generateKNfts).grid(row=0, column=7)
        Label(self.buttonsFrame, textvariable=self.error_var).grid(row=0, column=8)

        self.nftToMintTable = NftToMintTable(frame, self.uimanager)
        self.nftToMintTable.pack(fill='x')

        otherbuttonsFrame = Frame(frame)
        otherbuttonsFrame.pack(fill='x')
        Button(otherbuttonsFrame, text = 'Create Mint Transaction', command=self.createMintTransaction).grid(row=0, column=0)
        Label(otherbuttonsFrame, textvariable=self.error2_var).grid(row=0, column=1)

    def updatePolicies(self):
        self.policies = self.app.getPolicies()

    def generateKNfts(self):
        error=0
        try:
            int(self.count_nft_var.get())
        except:
            error=1
        try:
            self.app.getUtxos(self.beneficiary_var.get())
        except:
            error=2
        try:
            policy = self.policies[int(self.selected_policy_var.get().split(':')[0])]
        except:
            error=3

        if error != 0:
            error_msg = 'Not valid Number, ' if error == 1 else 'Invalid beneficiary' if error == 2 else 'Invalid Policy'
            self.error_var.set(error_msg)
            def resetErrorLabel(self):
                MintNftTab.global_variable += 1
                a = MintNftTab.global_variable_label_error
                time.sleep(2)
                if a == RequestInboxTab.global_variable_label_error:
                    self.error_var.set('')
            threading.Thread(target=resetErrorLabel, args=(self,)).start()
            return

        k = int(self.count_nft_var.get())
        beneficiary = self.beneficiary_var.get()
        nftsToMint = self.app.service_counter_manager.generateKNftsToMint(policy, beneficiary, k)
        [self.nftToMintTable.addItem(nft) for nft in nftsToMint]


    def createMintTransaction(self):
        error=0
        try:
            self.app.getUtxos(self.beneficiary_var.get())
        except:
            error=1
        if error != 0:
            error_msg = 'Invalid beneficiary'
            self.error2_var.set(error_msg)
            def resetErrorLabel(self):
                MintNftTab.global_variable += 1
                a = MintNftTab.global_variable_label_error2
                time.sleep(2)
                if a == RequestInboxTab.global_variable_label_error2:
                    self.error2_var.set('')
            threading.Thread(target=resetErrorLabel, args=(self,)).start()
            return

        popup = self.uimanager.createTransactionPopup(self)
        popup.mint_checkbox_bool_var.set(1)

        for nft in self.nftToMintTable.models:
            output_utxo = OutputUtxoModel(self.beneficiary_var.get(), 'Treasury', int(self.app.config['minimumAda']))
            popup.selectedPolicy = nft.policy
            output_utxo.addToken(TokenModel(nft.name, nft.policy.id),1)
            popup.addOutputUtxo(output_utxo)
            popup.addToken(nft.name, nft.policy.id, 1)
        popup.generate_metadata_bool_var.set(1)
        # setMetadata(self.app.service_counter_manager.generateMetadata([nft.name for nft in nftToMintTable.models]))


    def loadTreasuryBeneficiary(self):
        self.beneficiary_var.set(list(filter(lambda u:u.name == 'Treasury', self.app.getUsers()))[0].addr)
