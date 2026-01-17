# Code in this file references github.com/kurawlefaraaz/Tk-Themed-Utilities, using the MIT License. 
# The copy of the license is included below.

# MIT License
# 
# Copyright (c) 2023 kurawlefaraaz
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import tkinter as tk
import tkinter.ttk as ttk

class PopupEntry(tk.Entry):

    def __init__(self, parent, x, y, textvar,width = 10 ,entry_value='', text_justify = 'left', ):
        super().__init__(parent, relief = 'flat', justify = text_justify,bg='white', 
                         textvariable=textvar, font= "sublime 10")
        self.place(x=x, y=y, width=width)
        
        self.textvar = textvar
        self.textvar.set(entry_value)
        self.focus_set()
        self.select_range(0, 'end')
        # move cursor to the end
        self.icursor('end')

        self.wait_var = tk.StringVar(master=self)
        self._bind_widget()

        self.entry_value = entry_value
        self.wait_window()
    
    def _bind_widget(self):
        self.bind("<Return>", self.retrive_value)
        self.bind('<FocusOut>', self.retrive_value)

    def retrive_value(self, e):
        value = self.textvar.get()
        self.destroy()
        self.textvar.set(value)

class EditableTreeview(ttk.Treeview):

    def __init__(self, parent, columns, show, bind_key,data:list = None, 
                 non_editable_columns = None):
        super().__init__(parent, columns=columns, show=show)
        self.parent = parent
        self.column_name = columns
        self.data = data if data != None else []
        self.bind_key = bind_key
        self.non_editable_columns = non_editable_columns

        self.set_primary_key_column_attributes()
        self.set_headings()
        self.insert_data()
        self.set_edit_bind_key()

        self.editing_row = None
    
    def set_primary_key_column_attributes(self):
        self.column("#0",width=100,stretch=1)

    def set_headings(self):
        for i in self.column_name:
            self.heading(column=i, text=i)

    def insert_data(self):
        for index, values in enumerate(self.data):
            self.insert("", tk.END, values=values, iid=f"ITEM{index}")
    
    def set_edit_bind_key(self):
        self.bind('<Double Button-1>', self.edit)

    def get_absolute_x_cord(self):
        rootx = self.winfo_pointerx()
        widgetx = self.winfo_rootx()

        x = rootx - widgetx

        return x

    def get_absolute_y_cord(self):
        rooty = self.winfo_pointery()
        widgety = self.winfo_rooty()

        y = rooty - widgety

        return y
    
    def get_current_column(self):
        pointer = self.get_absolute_x_cord()
        return self.identify_column(pointer)

    def get_cell_cords(self,row,column):
        return self.bbox(row, column=column)
    
    def get_selected_cell_cords(self):
        row = self.focus()
        column = self.get_current_column()
        return self.get_cell_cords(row = row, column = column)

    def update_row(self, values):
        current_row = self.editing_row

        currentindex = self.index(current_row)

        self.delete(current_row)
        
        # Put it back in with the upated values
        self.insert('', currentindex, values = values)

        # Set editing row to none
        self.editing_row = None

    def check_region(self):
        result = self.identify_region(x=(self.winfo_pointerx() - self.winfo_rootx()), 
                                      y=(self.winfo_pointery()  - self.winfo_rooty()))
        # print(result)
        if result == 'cell':return True
        else: return False

    def check_non_editable(self):
        if self.get_current_column() in self.non_editable_columns:return False
        else: return True

    def edit(self, _):
        # _ param is for tkinter event
        if self.check_region() == False: return
        elif self.check_non_editable() == False: return
        self.editing_row = self.focus()
        current_row_values = list(self.item(self.editing_row,'values'))
        current_column = int(self.get_current_column().replace("#",''))-1
        current_cell_value = current_row_values[current_column]

        entry_cord = self.get_selected_cell_cords()
        entry_x = entry_cord[0]
        entry_y = entry_cord[1]
        entry_w = entry_cord[2]
        entry_h = entry_cord[3]

        entry_var = tk.StringVar()
        
        PopupEntry(self, x=entry_x, y=entry_y, width=entry_w,entry_value=current_cell_value, 
                   textvar= entry_var, text_justify='left')

        if entry_var != current_cell_value:
            current_row_values[current_column] = entry_var.get()
            self.update_row(values=current_row_values)