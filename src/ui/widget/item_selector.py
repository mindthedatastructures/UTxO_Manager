from tkinter import *
import tkinter.ttk as ttk


class ItemSelector(Toplevel):

    def addButton(title,row,column,parent1,parent2,var,options, label=None):
        if label == None:
            a = Label(parent1, textvariable=var)
            a.grid(row=row, column=column)
            b = Button(parent1, text='..', command=lambda: ItemSelector(parent2, title, options, var))
            b.grid(row=row, column=column+1)
            return (a,b)
        else:
            b = Button(parent1, text=label, command=lambda: ItemSelector(parent2, title, options, var))
            b.grid(row=row, column=column)
            return (b,)


    def __init__(self, root, title, item_list, var):
        super(ItemSelector,self).__init__(root)
        self.root = root
        self.item_list = item_list
        self.var = var
        self.bind('<Escape>', lambda e: self.close_popup)

        self.protocol("WM_DELETE_WINDOW", self.close_popup)
        self.geometry(f"600x300")
        self.title(title)
        self.grab_set()

        frame = Frame(self)
        self.tree = SimpleListTreeview(frame, self)
        self.tree.pack(fill='both', expand=1)
        buttonsFrame = Frame(frame)
        Button(buttonsFrame, text='Select', command=self.useSelected).grid(row=0, column=0)
        Button(buttonsFrame, text='Cancel', command=self.close_popup).grid(row=0, column=1)
        buttonsFrame.pack(fill='x')
        frame.pack(fill='both', expand=1)

        [self.tree.addItem(item) for item in item_list]


    def close_popup(self):
        self.grab_release()
        self.destroy()

    def useSelected(self):
        sel = self.tree.getSelectedItem()
        if sel != None:
            self.var.set(sel)
        self.close_popup()



class SimpleListTreeview(ttk.Treeview):
    def __init__(self, parent, item_selector):
        super(SimpleListTreeview,self).__init__(parent)
        self.item_selector = item_selector
        self.my_index = 0
        self.models = []
        self.initView()


    def getSelectedItem(self):
        try:
            curItem = int(self.focus())
        except:
            return None
        if curItem in range(len(self.models)):
            return self.models[curItem]
        else:
            return None

    def initView(self):

        self['columns'] = ('Item')
        self.heading('#0', text='', anchor=CENTER)
        self.heading('Item', text='Item', anchor=CENTER) 

        self.column('#0', width=1)
        self.column('Item', width=200)
        self.bind("<Double-1>", lambda x:self.item_selector.useSelected())

    def addItem(self,item):
        if item == None:
            self.insert(parent='', my_index=self.my_index, iid=self.my_index, text='', values='None')
            return
        self.insert(parent='', index=self.my_index, iid=self.my_index, text='', values=(item))
        self.my_index += 1
        self.models.append(item)

