
from tkinter import *
import tkinter.ttk as ttk

from src.ui.toggled_frame import ToggledFrame
from src.ui.tables.utxo_table import UtxoTable
from src.model.tx.utxo_model import UtxoModel

from src.ui.tabs.scrollable_tab import ScrollableTab

from src.app.app import Application


class MainUserTab(ScrollableTab):
    def __init__(self,tabControl,app, uimanager):
        super(MainUserTab,self).__init__(tabControl)
        self.app = app
        self.app.mode_changed_listeners.append(self)

        self.uimanager = uimanager

        self.initButtons()

        self.users_toggles = {}
        # self.users_toggles['faucet'] = UserToggle(self.uimanager, self.app, self.app.getFaucetUser(), self.viewPort, text='Faucet', relief="raised", borderwidth=1)
        # self.users_toggles['faucet'].init_faucet_ui()

        self.canvas.configure(scrollregion=self.canvas.bbox("all")) 
        self.updateMode()

    def updateMode(self):
        color = self.app.getColorForMode()
        self.canvas.configure(background=color)
        for name, toggle in self.users_toggles.items():
            toggle.sub_frame.configure(background=color)
        self.initButtons()

    def initButtons(self):
        for item in self.getButtonsFrame().winfo_children():
            item.destroy()
        i=0
        Button(self.buttonsFrame, text="Load Users", command=self.loadUsers).grid(row=0,column=i)
        i+=1
        Button(self.buttonsFrame, text="Expand All",
            command=lambda:[toggle.toggle(1) for i, (name, toggle) in enumerate(self.users_toggles.items())]
            ).grid(row=0,column=i)
        i+=1
        Button(self.buttonsFrame, text="Collapse All",
            command=lambda:[toggle.toggle(2) for i, (name, toggle) in enumerate(self.users_toggles.items())]
            ).grid(row=0,column=i)
        i+=1

        Button(self.buttonsFrame, text="Update All Utxos", command=lambda:[toggle.loadUtxos() for name, toggle in self.users_toggles.items()]).grid(row=0,column=i)
        i+=1
        Button(self.buttonsFrame, text="Create User", command=self.createUser).grid(row=0,column=i)
        i+=1
        Button(self.buttonsFrame, text="Create Transaction", command=self.createTransaction).grid(row=0,column=i)
        if not self.app.isMainnet():
            i+=1
            Button(self.buttonsFrame, text="Generate K users", command=self.testnet_generateKUsers).grid(row=0,column=i)
            self.users_to_generate_var = StringVar()
            i+=1
            Entry(self.buttonsFrame, textvariable=self.users_to_generate_var, width=3).grid(row=0,column=i)
            i+=1
            Button(self.buttonsFrame, text="Fund TestClients", command=self.testnet_fundTestClients).grid(row=0,column=i)

    def loadUsers(self):
        self.app.usersOutdated = True
        users = self.app.getUsers().copy()
        users.sort(key=lambda u:'aaaaa' if u.name == 'faucet' else 'z'+u.name if u.name[:10] == 'TestClient' else 'aa'+u.name)
        for u in users:
            if u.name == 'faucet':
                continue
            self.addUserUI(u)

    def addUserUI(self,u):
        self.users_toggles[u.name] = UserToggle(self.uimanager, self.app, u, self.viewPort, text=u.name, relief="raised", borderwidth=1)
        self.users_toggles[u.name].init_normal_ui()
        self.updateMode()

    def createUser(self):
        self.uimanager.createUserPopup(self, self.afterUserCreated)

    def afterUserCreated(self, username):
        self.app.createUser(username)
        u = self.app.getUserByName(username)
        self.addUserUI(u)

    def createTransaction(self):
        self.uimanager.createTransactionPopup(self)

    def testnet_generateKUsers(self):
        try:
            int(self.users_to_generate_var.get())
        except:
            return
        k = int(self.users_to_generate_var.get())
        b = max([int(a.name[len('TestClient#'):]) for a in list(filter(lambda u : u.name.startswith('TestClient#'),self.app.getUsers()))])
        for i in range(k):
            username = f'TestClient#{i+b+1}'
            self.app.createUser(username)
            u = self.app.getUserByName(username)
            self.addUserUI(u)

    def testnet_fundTestClients(self):
        self.app.testnet_fundTestClients()


class UserToggle(ToggledFrame):
    def __init__(self, uimanager, app, user, parent, text, relief, borderwidth):
        super(UserToggle,self).__init__(parent, text=text, relief=relief, borderwidth=borderwidth)
        self.user = user
        self.app = app
        self.uimanager = uimanager

    def init_normal_ui(self):
        for item in self.sub_frame.winfo_children():
            item.destroy()
        self.vv = StringVar()
        ttk.Entry(self.sub_frame, textvariable=self.vv, width=80).pack(side = TOP)
        ttk.Label(self.sub_frame, text=self.user.addr).pack(side = TOP)
        self.vv.set(self.user.addr)

        self.user_utxo_table = UtxoTable(self.sub_frame, self.uimanager)
        self.user_utxo_table.pack()
        buttonsFrame = ttk.Frame(self.sub_frame)
        buttonsFrame.pack(side=RIGHT)

        Button(buttonsFrame, text='Load Utxos', command=self.loadUtxos).grid(row = 0, column = 1)

        self.toggle(2)

    def loadUtxos(self):
        if self.user.addr == None:
            raise Exception("what?")
        utxos = self.app.getUtxos(self.user.addr)
        self.user_utxo_table.clear()
        if len(utxos) == 0:
            self.user_utxo_table.addItem(None)
        for u in utxos:
            self.user_utxo_table.addItem(u)


    def init_faucet_ui(self):
        faucet_vkey_file = self.app.data['faucet_vkey_file']
        ttk.Label(self.sub_frame, text=f"faucet_vkey_file : {faucet_vkey_file}").grid(row = 0,column = 0)

        self.faucetAddressLabel = ttk.Label(self.sub_frame, text="")
        self.faucetAddressLabel.grid(row = 1,column = 0)

        Button(self.sub_frame, text='Load Faucet Data', command=self.loadFaucetData).grid(row = 2,column = 0)
        
        self.user_utxo_table = UtxoTable(self.sub_frame, self.uimanager)
        self.user_utxo_table.grid(row = 3,column = 0)

        Button(self.sub_frame, text='Load Utxos', command=self.loadUtxos).grid(row = 3,column = 1)
        
        self.sub_frame.pack()

        self.toggle(2)

    def loadFaucetData(self):
        # for item in self.faucetFrame.winfo_children():
            # item.destroy()
        self.app.loadFaucetData()
        self.faucetAddressLabel["text"] = self.app.data['faucet_addr']
        self.sub_frame.pack()
        self.user = self.app.getFaucetUser()
