
from tkinter import *
import tkinter.ttk as ttk


from tkinter import *
import tkinter.ttk as ttk
import platform




class AbstractTable(ttk.Frame):
    def __init__(self, parent, uimanager):
        super(AbstractTable,self).__init__(parent)
        scroll = False
        if scroll:
    ## Scroll Things
    ############
            self.frame = Frame(self)
            self.frame.pack(fill='both', expand=1)
            self.canvas = Canvas(self.frame, borderwidth=0, background="#ffffff", width=1500)
            # self.grid(row=1,column=0)
            self.viewPort = ttk.Treeview(self.canvas)
            self.vsb = Scrollbar(self.frame, orient="vertical", command=self.canvas.yview)
            self.vsb = Scrollbar(self.frame, orient="vertical", command=self.canvas.yview)
            self.vsb.pack(side="right", fill="y")
            self.canvas.pack(side="left", fill="both", expand=True)
            self.canvas.configure(yscrollcommand=self.vsb.set)  
            self.canvas_window = self.canvas.create_window((4,4), window=self.viewPort, anchor="nw", tags="self.viewPort")
            self.viewPort.bind("<Configure>", self.onFrameConfigure)
            self.canvas.bind("<Configure>", self.onCanvasConfigure)
                
            self.viewPort.bind('<Enter>', self.onEnter)
            self.viewPort.bind('<Leave>', self.onLeave)
    
            self.canvas.pack()
    ############
        else:
            self.viewPort = ttk.Treeview(self)
            self.viewPort.pack(fill='both', expand=1)


        self.models = []
        self.uimanager = uimanager
        self.initView()

    def onFrameConfigure(self, event):                                              
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def onCanvasConfigure(self, event):
        canvas_width = event.width
        self.canvas.itemconfig(self.canvas_window, width = canvas_width)

    def onMouseWheel(self, event):
        if platform.system() == 'Windows':
            self.canvas.yview_scroll(int(-1* (event.delta/120)), "units")
        elif platform.system() == 'Darwin':
            self.canvas.yview_scroll(int(-1 * event.delta), "units")
        else:
            if event.num == 4:
                self.canvas.yview_scroll( -1, "units" )
            elif event.num == 5:
                self.canvas.yview_scroll( 1, "units" )
    
    def onEnter(self, event):
        if platform.system() == 'Linux':
            self.canvas.bind_all("<Button-4>", self.onMouseWheel)
            self.canvas.bind_all("<Button-5>", self.onMouseWheel)
        else:
            self.canvas.bind_all("<MouseWheel>", self.onMouseWheel)

    def onLeave(self, event):
        if platform.system() == 'Linux':
            self.canvas.unbind_all("<Button-4>")
            self.canvas.unbind_all("<Button-5>")
        else:
            self.canvas.unbind_all("<MouseWheel>")
###############


    def getColumnNames(self):
        raise NotImplementedError("Implement Child getColumnNames Function")

    def getColumnWidths(self):
        raise NotImplementedError("Implement Child getColumnWidth Function")

    def doubleClickFn(self, uimanager, model):
        raise NotImplementedError("Implement Child doubleClickFn Function")

    def getItemView(self, item):
        raise NotImplementedError("Implement Child getItemView Function")

    def getItemDefaultView(self):
        raise NotImplementedError("Implement Child getItemDefaultView Function")


    def getSelectedItem(self):
        try:
            curItem = int(self.viewPort.focus())
        except:
            return None
        if curItem in range(len(self.viewPort.models)):
            return self.viewPort.models[curItem]
        else:
            return None

    def initView(self):
        columns = self.getColumnNames()
        widths = self.getColumnWidths()

        self.viewPort['columns'] = self.getColumnNames()
        self.viewPort.heading('#0', text='', anchor=CENTER)
        [self.viewPort.heading(c, text=c, anchor=CENTER) for c in self.getColumnNames()]

        self.viewPort.column('#0', width=1)
        [self.viewPort.column(columns[i], width=widths[i]) for i in range(len(columns))]
        self.viewPort.bind("<Double-1>", lambda x:self.OnDoubleClick(x))
        self.index = 0

    def OnDoubleClick(self,x):
        curItem = int(self.viewPort.focus())
        if curItem not in range(len(self.models)):
            print('Double Click on invalid Element')
        self.doubleClickFn(self.uimanager, self.models[curItem])

    def addItem(self,item):
        if item == None:
            self.viewPort.insert(parent='', index=self.index, iid=self.index, text='', values=self.getItemDefaultView())
            return
        vals = self.getItemView(item)
        self.viewPort.insert(parent='', index=self.index, iid=self.index, text='', values=vals)
        self.index += 1
        self.models.append(item)

    def removeItem(self, item):
        found = False
        for i in range(len(self.models)):
            if self.models[i] == item:
                found = True
                break
        if not found:
            return
        self.models.pop(i)
        self.viewPort.remove(i)
        self.index -= 1

    def clear(self):
        self.viewPort.delete(*self.viewPort.get_children())
        self.models = []
        self.index = 0
