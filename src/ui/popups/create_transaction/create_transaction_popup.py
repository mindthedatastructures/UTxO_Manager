
from tkinter import *
import tkinter.ttk as ttk

from src.app.app import CliException

from src.ui.tabs.scrollable_tab import ScrollableTab

from src.ui.popups.create_transaction.sub_popups.add_input_utxo_popup import AddInputUtxoPopup
from src.ui.popups.create_transaction.sub_popups.add_output_utxo_popup import AddOutputUtxoPopup
# from src.ui.popups.create_transaction.sub_popups.remove_input_utxo_popup import RemoveInputUtxoPopup
# from src.ui.popups.create_transaction.sub_popups.remove_output_utxo_popup import RemoveOutputUtxoPopup
from tkinter.filedialog import askopenfilename

from src.model.tx.transaction_model import TransactionModel
from src.model.tx.utxo_model import UtxoModel
from src.model.tx.token_model import TokenModel
from src.model.tx.mint_model import MintModel

from src.ui.widget.item_selector import ItemSelector


font1 = "Helvetica 16 bold"
font2 = "Helvetica 12 bold"


class CreateTransactionPopup(Toplevel):
    def __init__(self,root, app):
        super(CreateTransactionPopup,self).__init__(root)
        self.app = app

        self.width = 250

        self.beneficiary_options = []
        self.token_options = []
        self.output_to_remove_options = []
        self.input_to_remove_options = []

        self.protocol("WM_DELETE_WINDOW", self.close_popup)
        self.geometry(f"1500x800")
        self.title("Transaction")
        self.grab_set()
        self.bind('<Escape>', lambda e: self.close_popup)

        scrollable_frame = ScrollableTab(self)
        scrollable_frame.pack(fill='both', expand=True)
        mainFrame = ttk.Frame(scrollable_frame.viewPort)
        # mainFrame = ttk.Frame(self)
        ttk.Button(scrollable_frame.buttonsFrame, text="Close", command=self.close_popup).grid(row = 0,column = 0)
        self.initUI(mainFrame)

        mainFrame.pack(fill='both')

    def initUI(self,mainFrame):
        createFrame = Frame(mainFrame,highlightbackground="grey", highlightthickness=3)
        createFrame.pack(fill='both')
        signFrame = Frame(mainFrame,highlightbackground="grey", highlightthickness=3)
        signFrame.pack(fill='both')
        sendFrame = Frame(mainFrame,highlightbackground="grey", highlightthickness=3)
        sendFrame.pack(fill='both')

        self.transaction = TransactionModel()
        self.mint_model = MintModel()
        self.change_beneficiary_utxo = None

        #####################
        ## CREATE FRAME

        # Title
        titleFrame = Frame(createFrame)
        ttk.Label(titleFrame, text=f"Create",font=font1).pack(fill='both')

        # inputUtxos
        inUtxoFrame = Frame(createFrame)
        ttk.Label(inUtxoFrame, text=f"Input Utxos:",font=font2).grid(row = 0,column = 0)
        self.input_utxos_var = StringVar()
        ttk.Label(inUtxoFrame, textvariable=self.input_utxos_var).grid(row = 1,column = 0)
        self.input_utxos_var.set("")
        buttonsFrame = Frame(inUtxoFrame)
        buttonsFrame.grid(row = 2,column = 0, columnspan=2)

        ttk.Button(buttonsFrame, text='Add Input', command=self.openAddInputUtxoPopup).grid(row = 0,column = 0)
        ttk.Button(buttonsFrame, text='Add DummyInput', command=self.addDummyInput).grid(row = 0,column = 1, columnspan=2)
        
        self.input_to_remove_var = StringVar()
        self.input_to_remove_var.trace('w', self.removeInputUtxoVar)

        ItemSelector.addButton(
            title='Remove Input', row=1, column=0, 
            parent1=buttonsFrame, parent2=self, 
            var=self.input_to_remove_var, 
            options=self.input_to_remove_options,
            label='Remove'
            )

        # Mint tokens
        mintFrame = Frame(createFrame)
        self.mint_checkbox_bool_var = IntVar()
        self.mint_checkbox_bool_var.trace('w', self.mintcheckboxChanged)

        Checkbutton(mintFrame, text="Mint Tokens (use only 1 policy)", font=font2, variable=self.mint_checkbox_bool_var).grid(row=0, column = 0)

        self.mintTokensSubFrame = Frame(mintFrame)
        self.mintTokensSubFrame.grid(row=1, column = 0)
        self.initMintTokenSubFrame()
        self.mintTokensSubFrame.grid_remove()

        # metadata

        self.metadataFrame = Frame(createFrame)
        ttk.Label(self.metadataFrame, text='Metadata.json (optional)',font=font2).grid(row = 0,column = 0)
        self.metadata_var = StringVar()
        ttk.Label(self.metadataFrame, textvariable=self.metadata_var).grid(row = 1,column = 0)

        buttonsFrame = Frame(self.metadataFrame,highlightbackground="grey", highlightthickness=1)
        buttonsFrame.grid(row = 2,column = 0)

        ttk.Button(buttonsFrame, text='Add Metadata', command=self.openAddMetadataPopup).grid(row = 0,column = 0)
        self.removeMetadataButton = ttk.Button(buttonsFrame, text='Remove Metadata', command=self.removeMetadata)
        self.removeMetadataButton.grid(row = 0,column = 1)
        self.removeMetadataButton.configure(state='disabled')

        # Output Utxos
        outputUtxosFrame = Frame(createFrame)
        ttk.Label(outputUtxosFrame, text=f"Ouput Utxos:").grid(row = 0,column = 0)
        self.output_utxos_var = StringVar()

        ttk.Label(outputUtxosFrame, textvariable=self.output_utxos_var).grid(row = 0,column = 1)
        self.output_utxos_var.set("")
        buttonsFrame = Frame(outputUtxosFrame,highlightbackground="grey", highlightthickness=1)
        buttonsFrame.grid(row = 1,column = 0)
        ttk.Button(buttonsFrame, text='Add Output', command=self.openAddOuputUtxoPopup).grid(row = 0,column = 0, columnspan=3)

        self.output_to_remove_var = StringVar()
        self.output_to_remove_var.trace('w', self.removeOutputUtxoVar)

        ItemSelector.addButton(
            title='Remove Output', row=1, column=0, 
            parent1=buttonsFrame, parent2=self, 
            var=self.output_to_remove_var, 
            options=self.output_to_remove_options,
            label='Remove'
            )

        # Fee

        feeFrame = Frame(createFrame)
        ttk.Label(feeFrame, text=f"Fee:").grid(row = 0,column = 0)

        feeSubFrame = Frame(feeFrame)
        feeSubFrame.grid(row = 0,column = 1)

        self.calculated_fee_var = StringVar()
        ttk.Label(feeSubFrame, textvariable=self.calculated_fee_var).grid(row = 0,column = 0)
        self.output_utxos_var.set("-")
        self.forced_fee_var = StringVar()
        ttk.Label(feeSubFrame, text='Force fee').grid(row = 0,column = 1)
        ttk.Entry(feeSubFrame, textvariable=self.forced_fee_var, width=10).grid(row = 0,column = 2)
        ttk.Button(feeSubFrame, text="Force", command=self.forceFee).grid(row = 0,column = 3)

        self.fees_buttonsFrame = Frame(feeFrame)
        self.fees_buttonsFrame.grid(row = 1,column = 0, columnspan=2)
        self.calculateFeeButton = ttk.Button(self.fees_buttonsFrame, text='Calculate Fee', command=self.calculateFee)
        self.calculateFeeButton.grid(row = 0,column = 0)
        self.calculateFeeButton.configure(state='disabled')
        self.updateChangeBeneficiaryOutputUtxoButton = ttk.Button(self.fees_buttonsFrame, text='Update Change Beneficiary Output Utxo', command=self.updateChangeBeneficiaryOutputUtxo)
        self.updateChangeBeneficiaryOutputUtxoButton.grid(row = 0,column = 1)

        ttk.Label(self.fees_buttonsFrame, text='select change beneficiary utxo:').grid(row = 0,column = 2)
        self.change_beneficiary_utxo_var = StringVar()
        self.change_beneficiary_utxo_var.trace('w', self.changeBeneficiaryUtxoDropdownChanged)

        ItemSelector.addButton(title='Mode', row=0, column=3, parent1=self.fees_buttonsFrame, parent2=self.fees_buttonsFrame, var=self.change_beneficiary_utxo_var, options=self.beneficiary_options)


        # Build
        buildButtonFrame = Frame(createFrame)
        ttk.Button(buildButtonFrame, text='Validate IO', command=self.validateIO).grid(row = 0,column = 0)

        self.io_validation_var = StringVar()
        ttk.Label(buildButtonFrame, textvariable=self.io_validation_var).grid(row = 1,column = 0)

        self.build_output_var = StringVar()
        self.estimated_size_var = StringVar()
        ttk.Label(buildButtonFrame, textvariable=self.build_output_var).grid(row = 2,column = 0)
        self.buildButton = ttk.Button(buildButtonFrame, text='Build', command=self.build)
        self.buildButton.grid(row = 3,column = 0)
        ttk.Button(buildButtonFrame, text='Print Command', command=self.printCommand).grid(row = 3,column = 2)
        ttk.Button(buildButtonFrame, text='Build And Send To Ready To Sign', command=self.buildAndSendToReadyToSign).grid(row = 3,column = 1)
        ttk.Label(buildButtonFrame, text='Estimated Size: ').grid(row = 4,column = 0)
        ttk.Label(buildButtonFrame, textvariable=self.estimated_size_var).grid(row = 4,column = 5)


        titleFrame                    .pack(fill='both')
        ttk.Separator(createFrame)    .pack(fill='both')
        inUtxoFrame                   .pack(fill='both')
        ttk.Separator(createFrame)    .pack(fill='both')
        mintFrame                     .pack(fill='both')
        ttk.Separator(createFrame)    .pack(fill='both')
        self.metadataFrame            .pack(fill='both')
        ttk.Separator(createFrame)    .pack(fill='both')
        outputUtxosFrame              .pack(fill='both')
        ttk.Separator(createFrame)    .pack(fill='both')
        feeFrame                      .pack(fill='both')
        ttk.Separator(createFrame)    .pack(fill='both')
        buildButtonFrame              .pack(fill='both')

        #####################
        ## CREATE FRAME

        ttk.Label(signFrame, text=f"Sign").grid(row = 0,column = 0)
        self.signButton = ttk.Button(signFrame, text='Sign', command=self.signTransaction).grid(row = 0,column = 0)
        self.sign_output_var = StringVar()
        ttk.Label(signFrame, textvariable=self.sign_output_var).grid(row = 1,column = 0)


        #####################
        ## SEND FRAME

        ttk.Label(sendFrame, text=f"Send").grid(row = 0,column = 0)
        self.sendButton = ttk.Button(sendFrame, text='Send', command=self.sendTransaction).grid(row = 1,column = 0)
        self.send_output_var = StringVar()
        ttk.Label(sendFrame, textvariable=self.send_output_var).grid(row = 2,column = 0)

        col_count, row_count = self.grid_size()

        for col in range(col_count):
            mainFrame.grid_columnconfigure(col, minsize=self.width)

    def close_popup(self):
        self.grab_release()
        self.destroy()


########################
# Minting Panel

    def mintcheckboxChanged(self, *args):
        if self.mint_checkbox_bool_var.get() == 1:
            self.mintTokensSubFrame.grid()
            self.transaction.mint = self.mint_model
            self.metadataFrame.grid_remove()
        else:
            self.mintTokensSubFrame.grid_remove()
            self.metadataFrame.grid()
            self.transaction.mint = None

    def initMintTokenSubFrame(self):

        self.selected_policy_var = StringVar()
        self.token_name_var = StringVar()
        self.policy_options = self.app.getPolicies()
        self.tokens_label_var = StringVar()
        self.token_amount_var = StringVar()
        self.token_to_remove_var = StringVar()


        ttk.Label(self.mintTokensSubFrame, text="Policy").grid(row = 0,column = 0)
        ttk.Label(self.mintTokensSubFrame, text="Tokens").grid(row = 1,column = 0)

        self.selected_policy_var.trace('w', self.onSelectedPolicyChanged)

        ItemSelector.addButton(
            title='Policy', 
            row=0, column=1, 
            parent1=self.mintTokensSubFrame, parent2=self.mintTokensSubFrame, 
            var=self.selected_policy_var, 
            options=[f'{i}:{p.toString()}' for i, p in enumerate(self.policy_options)])
    
        tokensFrame =Frame(self.mintTokensSubFrame, width=200, height=300)
        tokensFrame.grid(row=1,column=1)

        ttk.Label(tokensFrame, textvariable=self.tokens_label_var).grid(row = 0,column = 0)
        self.tokenOptionsFrame = Frame(tokensFrame)
        self.tokenOptionsFrame.grid(row=0,column=1)
        self.addTokenButton = ttk.Button(self.tokenOptionsFrame, text="Add Token", command=lambda:self.addToken(self.token_name_var.get(), self.selectedPolicy.id,int(self.token_amount_var.get())))
        self.addTokenButton.grid(row = 0,column = 0)
        self.removeTokenButton = ttk.Button(self.tokenOptionsFrame, text="Remove Token", command=self.removeToken)
        self.removeTokenButton.grid(row = 1,column = 0)
        self.removeTokenButton.configure(state='disabled')


        addingframe = Frame(self.tokenOptionsFrame)
        addingframe.grid(row=0,column=1)
        ttk.Label(addingframe, text='Name').grid(row = 0,column = 0)
        ttk.Entry(addingframe, textvariable=self.token_name_var).grid(row = 0,column = 1)
        ttk.Label(addingframe, text='Amount').grid(row = 1,column = 0)
        ttk.Entry(addingframe, textvariable=self.token_amount_var).grid(row = 1,column = 1)

        self.token_name_var.trace('w', lambda *args:self.updateTokenButtonsState())
        self.token_amount_var.trace('w', lambda *args:self.updateTokenButtonsState())
        self.token_to_remove_var.trace('w', lambda *args:self.updateTokenButtonsState())

        self.tokens_to_remove_dropdown = None

        metadataGeneratedFrame = Frame(self.mintTokensSubFrame)
        metadataGeneratedFrame.grid(row=2,column=0, columnspan = 2)

        self.generate_metadata_bool_var = IntVar()
        self.generate_metadata_bool_var.trace('w', self.updateGeneratedMetadata)

        self.generated_metadata_name_var = StringVar()

        Checkbutton(metadataGeneratedFrame, text="Generate Metadata", font=font2, variable=self.generate_metadata_bool_var).grid(row=0, column = 0)
        Label(metadataGeneratedFrame, textvariable=self.generated_metadata_name_var).grid(row=0, column = 1)

        ItemSelector.addButton(title='Mode', row=1, column=1, parent1=self.tokenOptionsFrame, parent2=self.tokenOptionsFrame, var=self.token_to_remove_var, options=self.token_options)

        self.updateTokenButtonsState()

    def addToken(self, name, policy_id, amount):
        token = TokenModel(name, policy_id)
        self.mint_model.addToken(token, amount)
        self.mint_model.policy = self.selectedPolicy
        self.token_name_var.set('')
        self.token_amount_var.set('')
        self.updateTokenView()
        self.token_to_remove_var.set('')
        self.updateRemoveTokenDropdown()
        self.updateTokenButtonsState()
        self.updateGeneratedMetadata()

    def removeToken(self):
        token = self.mint_model.tokens[int(self.token_to_remove_var.get().split(':')[0])]
        self.mint_model.tokens.remove(token)
        self.updateRemoveTokenDropdown()
        self.updateTokenView()
        self.updateTokenButtonsState()
        self.updateGeneratedMetadata()

    def onSelectedPolicyChanged(self, *args):
        if self.selected_policy_var.get() != '':
            self.selectedPolicy = self.policy_options[int(self.selected_policy_var.get().split(':')[0])]
        else:
            self.selectedPolicy = None

    def updateRemoveTokenDropdown(self):
        self.token_to_remove_var.set('')
        [self.token_options.pop() for i in range(len(self.token_options))]
        [self.token_options.append(f'{i}:{t["token"].toDisplayableString()}') for i,t in enumerate(self.mint_model.tokens)]

    def updateTokenButtonsState(self):
        if(self.token_name_var.get() != '' and self.selected_policy_var.get() != '' and self.token_amount_var.get() != ''):
            try:
                int(self.token_amount_var.get())
                self.addTokenButton.configure(state='active')
            except:
                self.addTokenButton.configure(state='disabled')
        else:
            self.addTokenButton.configure(state='disabled')

        if self.token_to_remove_var.get() == '':
            self.removeTokenButton.configure(state='disabled')
        else:
            self.removeTokenButton.configure(state='active')

    def updateTokenView(self):
        self.tokens_label_var.set('\n'.join([f'{i}:{t["token"].toDisplayableString()}:{t["value"]}' for i,t in enumerate(self.mint_model.tokens)]))

    def updateGeneratedMetadata(self, *args):
        if self.generate_metadata_bool_var.get() == 1:
            filename = self.app.service_counter_manager.generateMetadata([t['token'].name for t in self.mint_model.tokens], self.mint_model.policy.id)
            self.transaction.generated_metadata = filename
            self.generated_metadata_name_var.set(filename)
            self.transaction.generate_metadata = True
        else:
            self.transaction.generate_metadata = False



########################


########################
# INPUT

    def openAddInputUtxoPopup(self, *args):
        AddInputUtxoPopup(self, self.app)

    def addDummyInput(self):
        utxo = UtxoModel()
        utxo.hash = 'e9b94f025d1a25f71fe1093d03ed1068ac5adaba82738b4ddd8d3250ea354f35#0'
        utxo.address = 'addr1vy9fzngkynrgpczx9g4wnsmzjk7xut5ztkplmzudlys74ts67z3yy'
        utxo.value = {'lovelace': 21693360}
        self.addInputUtxo(utxo)

    def addInputUtxo(self, utxo):
        self.transaction.input_utxos.append(utxo)
        self.updateLabelUtxoInputData()
        self.updateCalculateFeeButton()
        self.updateAllUtxoOptions()

    def removeInputUtxoVar(self, *args):
        if self.input_to_remove_var.get() == '':
            return
        utxo = self.transaction.input_utxos[int(self.input_to_remove_var.get().split(':')[0])]
        self.input_to_remove_var.set('')
        self.transaction.input_utxos.remove(utxo)
        self.updateLabelUtxoInputData()
        self.updateCalculateFeeButton()
        self.updateAllUtxoOptions()

    def updateLabelUtxoInputData(self):
        toPrint = ''
        for i,u in enumerate(self.transaction.input_utxos):
            if i != 0:
                toPrint += '\n'
            toPrint += f'{i}:'+u.uiString()

        self.input_utxos_var.set(toPrint)

########################
# METADATA

    def openAddMetadataPopup(self, *args):
        metadata = askopenfilename(
            title='Open files',
            initialdir=f'{self.app.maindir}/data/jsons',
            filetypes=[("JSON files","*.json")])
        if metadata != '':
            self.setMetadata(metadata)

    def setMetadata(self, metadata):
        self.transaction.metadata = metadata
        self.metadata_var.set(self.transaction.metadata[-50:])
        self.removeMetadataButton.configure(state='active')

    def removeMetadata(self, *args):
        self.transaction.metadata = None
        self.metadata_var.set('')
        self.removeMetadataButton.configure(state='disabled')



########################
# OUTPUT

    def openAddOuputUtxoPopup(self, *args):
        AddOutputUtxoPopup(self, self.app)

    def addOutputUtxo(self, output_utxo):
        self.transaction.output_utxos.append(output_utxo)
        self.updateLabelUtxoOutputData()
        self.updateCalculateFeeButton()
        self.updateAllUtxoOptions()

    def removeOutputUtxoVar(self, *args):
        if self.output_to_remove_var.get() == '':
            return
        utxo = self.transaction.output_utxos[int(self.output_to_remove_var.get().split(':')[0])]
        self.output_to_remove_var.set('')
        self.transaction.output_utxos.remove(utxo)
        if utxo == self.change_beneficiary_utxo:
            self.change_beneficiary_utxo_var.set('')
        self.updateLabelUtxoOutputData()
        self.updateCalculateFeeButton()
        self.updateAllUtxoOptions()

    def updateLabelUtxoOutputData(self):
        toPrint = ''
        lines = ['']*10
        for i,u in enumerate(self.transaction.output_utxos):
            lines[i%10] += f'  {i}:{u.name}:{u.address[:20]}..:{u.value}'
            for t in u.tokens:
                lines[i%10] += f"+ {t['value']} {t['token'].name}"

        self.output_utxos_var.set('\n'.join(lines))
    
    def updateChangeBeneficiaryOutputUtxo(self):
        self.transaction.updateChange(self.change_beneficiary_utxo)

        self.updateLabelUtxoOutputData()
        self.printValues()

########################
# UI OPTIONS AND LABEL  GENERALUPDATES

    def updateCalculateFeeButton(self):
        if len(self.transaction.output_utxos)>0 and len(self.transaction.input_utxos)>0:
            self.calculateFeeButton.configure(state='active')
        else:
            self.calculateFeeButton.configure(state='disabled')

    def calculateFee(self):
        self.app.calculateAndUpdateFee(self.transaction)
        self.calculated_fee_var.set(f'{self.transaction.fee} lovelace')

    def changeBeneficiaryUtxoDropdownChanged(self, *args):
        if len(self.transaction.output_utxos)>0:
            self.change_beneficiary_utxo = self.transaction.output_utxos[int(self.change_beneficiary_utxo_var.get().split(':')[0])]
        else:
            self.change_beneficiary_utxo = None


    def updateAllUtxoOptions(self):
        while len(self.beneficiary_options) > 0:
            self.beneficiary_options.pop(0)
        [self.beneficiary_options.append(o) for o in [f'{i}:{self.transaction.output_utxos[i].name}:{self.transaction.output_utxos[i].address[:20]}..:{self.transaction.output_utxos[i].value}' for i in range(len(self.transaction.output_utxos))]]
        self.change_beneficiary_utxo_var.set(self.beneficiary_options[0] if len(self.beneficiary_options)>0 else '')

        self.output_to_remove_var.set('')
        while len(self.output_to_remove_options) > 0:
            self.output_to_remove_options.pop(0)
        [self.output_to_remove_options.append(f'{i}:{u.name}:{u.address[:20]}..:{u.value}') for i, u in enumerate(self.transaction.output_utxos)]

        self.input_to_remove_var.set('')
        while len(self.input_to_remove_options) > 0:
            self.input_to_remove_options.pop(0)
        [self.input_to_remove_options.append(f'{i}:'+ u.uiString()) for i, u in enumerate(self.transaction.input_utxos)]

        if self.change_beneficiary_utxo == None:
            self.calculated_fee_var.set("Change beneficiary is null")
            return


    def printValues(self):
        out = ''
        my_sum = 0
        for i in self.transaction.input_utxos:
            if not i == self.transaction.input_utxos[0]:
                out +='+'
            out += f"{i.value['lovelace']}"
            my_sum += i.value['lovelace']
        out += f'={my_sum}\n'
        my_sum = 0
        for o in self.transaction.output_utxos:
            if not o == self.transaction.output_utxos[0]:
                out +='+'
            out += f'{o.value}'
            my_sum += o.value
        out += f'++{self.transaction.fee}'
        my_sum += self.transaction.fee
        out += f'={my_sum}\n'
        print(out)

    def printCommand(self):
        print(self.app.getBuildCommand(self.transaction, extension='raw'))

########################
# APP OPERATIONS

    def build(self):
        self.my_hash = self.app.build(self.transaction, extension='raw')

        estimated = self.app.estimateTxSize(self.my_hash)
        if estimated >= 16384:
            msg = f"WARNING : estimated tx size {estimated} higher than maximum 16384"
        else:
            msg = str(estimated)
        self.estimated_size_var.set(msg)

        self.build_output_var.set(f"Created File {self.my_hash}.raw with raw transaction and {self.my_hash}.command with command")

    def buildAndSendToReadyToSign(self):
        self.build()
        self.app.buildAndSendToReadyToSign(self.transaction, self.my_hash)
         

    def signTransaction(self):
        try:
            self.app.sign(self.my_hash, 'raw', self.transaction)
            self.sign_output_var.set(f"Created File {self.my_hash}.signed with signed transaction")
        except CliException as e:
            self.sign_output_var.set(str(e))

    def sendTransaction(self):
        self.app.send(self.my_hash)
        self.send_output_var.set(f"Sent Transaction {self.my_hash}!")

    def forceFee(self):
        try:
            val = int(self.forced_fee_var.get())
            self.transaction.fee = val
            self.calculated_fee_var.set(f'{self.transaction.fee} lovelace - forced {val}')
        except:
            None

    def validateIO(self):
        input__ada_sum = sum([i.value['lovelace'] for i in self.transaction.input_utxos])
        output__ada_sum = sum([o.value for o in self.transaction.output_utxos])+self.transaction.fee

        tokens_ins = {}
        tokens_out = {}

        for u in self.transaction.input_utxos:
            for policy,tokens in u.value.items():
                if policy == 'lovelace':
                    continue
                for token, value in tokens.items():
                    name = f'{policy}.{token}'
                    if name not in tokens_ins.keys():
                        tokens_ins[name] = 0
                    tokens_ins[name] += value

        if self.transaction.mint != None:
            for t in self.transaction.mint.tokens:
                name = f"{t['token'].policy_id}.{t['token'].name}"
                value = t['value']
                if name not in tokens_ins.keys():
                    tokens_ins[name] = 0
                tokens_ins[name] += value

        for u in self.transaction.output_utxos:
            for tokens_struct in u.tokens:
                name = f"{tokens_struct['token'].policy_id}.{tokens_struct['token'].name}"
                if name not in tokens_out.keys():
                    tokens_out[name] = 0
                tokens_out[name] += tokens_struct['value']

        res = ''
        if tokens_ins.keys() != tokens_out.keys():
            res += 'One error at a time\nNot the same tokens at input and output\n'
            res += f'inputs: {tokens_ins.keys()}\n'
            res += f'outputs: {tokens_out.keys()}\n'
        else:
            problem = False
            for k,v in tokens_ins.items():
                if v != tokens_out[k]:
                    problem = True
                    res += f'One error at a time\n problems with token {k}\n'
                    res += f'input sum: {v} ; output sum: {tokens_out[k]}\n'
                    break
            if not problem:
                if input__ada_sum != output__ada_sum:
                    res += f'Input lovelace different than output lovelace\n'
                    res += f'input sum: {input__ada_sum} ; output sum: {output__ada_sum}\n'
                else:
                    res += 'All Good!'
                    
        self.io_validation_var.set(res)
