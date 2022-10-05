
import tkinter as tk
import tkinter.ttk as ttk

from src.app.app import Application

class ConfigTab(tk.Frame):
    def __init__(self,tabControl,app, uimanager):
        super(ConfigTab,self).__init__(tabControl)
        self.app = app
        self.app.mode_changed_listeners.append(self)
        self.uimanager = uimanager
        self.used_ports = ''

        modeFrame = tk.Frame(self)
        modeFrame.grid(row = 0,column = 0)
        self.initModeForm(modeFrame)
        
        self.testnetConfigFormFrame = tk.Frame(self)
        self.testnetConfigFormFrame.grid(row = 1,column = 0)

        self.initTestnetConfigForm()

        self.initState()

    def initState(self):
        self.mode_var.set(int(Application.Modes.Mainnet))


    def initTestnetConfigForm(self):
        self.uiconfigs = {}
        self.initTestnetForm()
        self.updateMode()


    def initModeForm(self, modeFrame):
        self.mode_var = tk.IntVar()
        self.mode_var.trace('w', self.ui_modeChanged)

        tk.Label(modeFrame, text="SelectMode",justify = tk.LEFT,padx = 20).grid(row=0,column=0, columnspan=2)
        tk.Radiobutton(modeFrame, text="Testnet", padx = 20, variable=self.mode_var, value=int(Application.Modes.Testnet)).grid(row=1,column=0)
        tk.Radiobutton(modeFrame, text="Mainnet", padx = 20, variable=self.mode_var, value=int(Application.Modes.Mainnet)).grid(row=1,column=1)

    def ui_modeChanged(self, *args):
        self.app.setMode(self.mode_var.get())

    def updateMode(self):
        color = self.app.getColorForMode()
        self.configure(bg=color)

    def initTestnetForm(self):
        config = self.app.config
        i = 0
        for k,v in config.items():
            tk.Label(self.testnetConfigFormFrame ,text = k).grid(row = i,column = 0)
            var = tk.StringVar()
            var.set(v)
            var.trace('w', self.updatedConfig)
            a1 = tk.Entry(self.testnetConfigFormFrame, text=var, width= 150).grid(row = i,column = 1)
            self.uiconfigs[k] = var
            i += 1
        self.saveConfigButton = tk.Button(self.testnetConfigFormFrame, text='Save in config File', command=self.saveConfig)
        self.saveConfigButton.grid(row = i,column = 0)
        self.saveConfigButton["state"] = 'disabled'

        self.getLatestValuesButton = tk.Button(self.testnetConfigFormFrame, text='Load Latest Local Testnet Values', command=self.loadLatest)
        self.getLatestValuesButton.grid(row = i+1,column = 0)

    def updatedConfig(self, *args):
        for k,v in self.uiconfigs.items():
            self.app.config[k] = v.get()
        self.saveConfigButton["state"] = 'active'

    def saveConfig(self):
        self.app.saveLocalConfig()
        self.saveConfigButton["state"] = 'disabled'

    def loadLatest(self):
        self.app.loadLateststLocalTestnetValues()
        self.used_ports = '     '.join([f'{n} - {p}' for n,p in self.app.getPorts().items()])
        self.cleanTestnetFormFrame()
        self.initTestnetForm()


    def cleanTestnetFormFrame(self):
        for item in self.testnetConfigFormFrame.winfo_children():
            item.destroy()

    def getProtocolParameters(self):
        self.app.getProtocolParameters()
        self.getProtocolParameters_var.set('stored')

