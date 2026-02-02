import typing

import tkinter as tk
import tkinter.ttk as ttk

import re
import random

if __name__ == "__main__":
    from error_detected import error_detected
    from editable_treeview import EditableTreeview
else:
    from .error_detected import error_detected
    from .editable_treeview import EditableTreeview


class EditWindow(tk.Toplevel):

    def __init__(
            self, 
            glass_blocks_conf: list, 
            glass_options: dict, 
            new_template: list | None = None, 
            on_hide: typing.Callable | None = None, 
            ):
        # Initialize as a tkinter window
        tk.Toplevel.__init__(self)
        # Options list
        self.option_names = list(glass_options.keys())
        self.option_types = list(glass_options.values())
        # New glass block template
        self.new_template = [""] * len(self.option_names)
        if new_template != None:
            if len(new_template) == len(self.option_names):
                self.new_template = new_template
        # Current config buffer
        self.glass_blocks_conf = glass_blocks_conf
        self.curr_config = []
        # Misc
        self.on_hide = on_hide
        self._new_blocks_count = 0
        self.selected_block_index = -1 # -1 for not selected
        # Widgets inside window
        ## State part
        self.state_part = tk.Label(self, text="Initializing...", bg="yellow", anchor=tk.W)
        self.state_part.pack(fill=tk.X, side=tk.BOTTOM)
        ## Left part
        self.left_part = ttk.LabelFrame(self, text="Glass blocks")
        ttk.Button(self.left_part, text="+ Add", 
                   command=self.add_block).pack(fill=tk.X, side=tk.BOTTOM)
        ttk.Button(self.left_part, text="× Remove", 
                   command=self.del_block).pack(fill=tk.X, side=tk.BOTTOM)
        self.glass_list = tk.Listbox(self.left_part, selectmode=tk.SINGLE)
        self.glass_list.pack(fill=tk.BOTH, expand=True)
        self.glass_list.bind("<<ListboxSelect>>", self.select_block)
        self.left_part.pack(side = tk.LEFT, fill = tk.Y)
        ## Rendering order
        self.order_area = ttk.LabelFrame(self, text="Rendering Order")
        tk.Label(self.order_area, 
                 text="Rendering order decides the occlusion relationship of the glass blocks.")\
                 .pack(fill=tk.X)
        ttk.Button(self.order_area, text="↑ Move current block up", 
                   command=lambda: self.move_block(-1))\
            .pack(side=tk.LEFT, fill=tk.X, expand=True)
        ttk.Button(self.order_area, text="↓ Move current block down", 
                   command=lambda: self.move_block(+1))\
            .pack(side=tk.RIGHT, fill=tk.X, expand=True)
        self.order_area.pack(fill=tk.X)
        ## Options
        self.options_area = ttk.LabelFrame(self, text="Options")
        self.options_area.pack(fill = tk.BOTH, expand = True)
        self.option_entries = EditableTreeview(self.options_area, ["Attribute", "Value"], 
                                               bind_key='<Double-Button-1>', show='headings', 
                                               data=[(option_name, "") for option_name in \
                                                     self.option_names], non_editable_columns="#1")
        self.option_entries.pack(fill=tk.BOTH, expand=True)
        tk.Label(self.options_area, text="💡 Double click a field to edit").pack(fill = tk.BOTH)
        # Rename the window
        self.title("Edit Glass Blocks Configuration")
        # Event binding while editing and finishing editing
        self.option_entries.on_enter_edit = self.on_enter_edit
        self.option_entries.on_finish_edit = self.on_finish_edit
        # Set close button hides the window to prevent close
        self.protocol("WM_DELETE_WINDOW", self.hide)
        # Auto set size
        self.update()
        self.minsize(int(self.winfo_width() * 1.2), self.winfo_height())
        # Hide the edit window at initial state
        self.withdraw()

    def show(self):
        """Show edit window."""
        self.deiconify()
        self.update()
        # Load in current config and glass block list
        self.read_config()
        self.load_curr_config()
        self.set_state("Ready.", color="lightgreen")
    
    def hide(self):
        """Hide the window."""
        self.set_state("Saving configurations...", color="yellow")
        converted = self.convert_attrs()
        if converted == None:
            return
        self.save_config()
        # print(glass_blocks_conf)
        self.withdraw()
        self.set_state("The window should be hidden now.", color="pink")
        self.on_hide() if self.on_hide != None else None
    
    def set_state(self, text: str, color: str | None="lightgreen"):
        """Set content in state indicator."""
        self.state_part["text"] = text
        if color != None:
            self.state_part["bg"] = color
        self.update()

    def read_config(self):
        """Read current global config to buffer."""
        self.curr_config = [list(block_args) for block_args in self.glass_blocks_conf]
    
    def save_config(self):
        """Save current buffer to global config."""
        # self.glass_blocks_conf = [tuple(block_args) for block_args in self.curr_config]
        self.glass_blocks_conf.clear()
        self.glass_blocks_conf.extend([tuple(block_args) for block_args in self.curr_config])

    def load_curr_config(self):
        """Load glass list in current config buffer into the edit window."""
        self.glass_list.delete(0, tk.END)
        for index, block in enumerate(self.curr_config):
            # print(f"Load {block[0]} into edit window")
            self.glass_list.insert(tk.END, f"[{index + 1}] {block[0]}")

    def select_block(self, _: typing.Any=None, silent: bool=False):
        """When selecting a glass block in list."""
        list_selected = self.glass_list.curselection()
        if len(list_selected) == 0:
            # self.option_entries.set("ITEM0", 1, "Select a glass block to edit...")
            return
        else:
            self.selected_block_index = list_selected[0]
        for attr_index, value in enumerate(self.curr_config[self.selected_block_index]):
            self.option_entries.set(f"ITEM{attr_index}", 1, str(value))
        if not silent:
            self.set_state(f"Selected: {self.glass_list.get(self.selected_block_index)}.")

    def select_field(self, block_index: int, attr_index: int, silent: bool=False):
        """Jump user focus to a specified field."""
        self.glass_list.selection_clear(1, tk.END)
        self.glass_list.selection_set(block_index)
        self.update()
        self.select_block(silent=silent)
        self.option_entries.selection_set(f"ITEM{attr_index}")

    def convert_attr_value(self, value: str, target_type: str) \
        -> tuple[bool, typing.Any]:
        """Validate and convert one given attribute value."""
        match target_type.lower():
            case "str":
                return True, value
            case "int":
                if value == "":
                    value = "0"
                if (value[1:] if value[0] == "-" else value).isdigit():
                    return True, int(value)
                else:
                    return False, 0
            case "float":
                if value == "":
                    value = "0.0"
                if (value[1:] if value[0] == "-" else value).replace('.', '', 1).isdigit():
                    return True, float(value)
                else:
                    return False, 0
            case "hex_color":
                if re.fullmatch(r"#?([0-9a-fA-F]{6})$", value):
                    return True, value
                else:
                    return False, "#00ff00"
            case _:
                error_detected()
                return (False, value)

    def convert_attrs(self) -> list | None:
        """Converts attr config string into types they should be."""
        for block_index, attrs in enumerate(self.curr_config):
            result = []
            if len(attrs) != len(self.option_types):
                self.set_state(f"Wrong number of attribute values: expected "
                               f"{len(self.option_types)} but got {len(attrs)}",color="pink")
                error_detected()
            for index, attr in enumerate(attrs):
                if type(attr) is str: # Only handles string
                    convert_result = self.convert_attr_value(attr, self.option_types[index])
                    if not convert_result[0]: # Convert not success
                        self.set_state(f"Value '{attr}' for {self.option_names[index]} "
                                       f"must be in type {self.option_types[index]}! Check your "
                                        "entered value and retry.", color="pink")
                        self.select_field(block_index, index, silent=True)
                        return None
                    result.append(convert_result[1])
                else: # If is not string, we treat it as already in correct type
                    result.append(attr)
            self.curr_config[block_index] = result.copy()
        return self.curr_config

    def add_block(self):
        """When adding a new glass block."""
        self._new_blocks_count += 1
        dynamics = {
            "new_blocks_count": str(self._new_blocks_count), 
            }
        self.curr_config.append(
            [v() if callable(v) else str(v).format(**dynamics) for v in self.new_template]
            )
        self.load_curr_config()
        self.set_state(f"Added new glass block {self._new_blocks_count}.")

    def del_block(self):
        """When removing a new glass block."""
        selected_index = self.glass_list.curselection()
        if len(selected_index) == 0:
            retry_hint = f"Do you mean glass block [{self.selected_block_index}]? " + \
                         "Select it again from list and retry." if \
                         self.selected_block_index != -1 else ""
            self.set_state("No glass block selected! " + retry_hint, color="pink")
            return
        self.curr_config.pop(selected_index[0])
        self.load_curr_config()

    def move_block(self, to: int):
        """Move selected block up / down."""
        target_place = self.selected_block_index + to
        if target_place < 0 or target_place > len(self.curr_config) - 1:
            # If target place if out of the list
            return
        temp = self.curr_config[self.selected_block_index]
        self.curr_config.pop(self.selected_block_index)
        self.curr_config.insert(self.selected_block_index + to, temp)
        self.selected_block_index = target_place
        self.load_curr_config()

    def on_enter_edit(self, editing_row):
        """When entering edit attribute mode."""
        if self.option_entries.editing_row == None:
            return
        attr_name = self.option_entries.item(editing_row,'values')[0]
        glass_name = self.glass_list.get(self.selected_block_index) 
        self.set_state(f"Editing attribute '{attr_name}' for {glass_name}.", color="yellow")
    
    def on_finish_edit(self, editing_row, after_values):
        """When exiting edit attribute mode."""
        if self.option_entries.editing_row == None:
            return
        # Change state text
        attr_name = self.option_entries.item(editing_row,'values')[0]
        glass_name = self.glass_list.get(self.selected_block_index)
        after_value = after_values[1]
        self.set_state(f"Modified attribute '{attr_name}' for {glass_name} to '{after_value}'.")
        # Save to config buffer and reload
        self.curr_config[self.selected_block_index][self.option_entries.index(editing_row)] = \
            after_value
        self.load_curr_config()


if __name__ == "__main__":
    # Test
    test_conf = []
    conf_list = {
        "Comment": "str", 
        "Test attr 1 (String)": "str", 
        "Test attr 2 (Integer)": "int", 
        "Test attr 2 (Hex color)": "hex_color", 
        }
    root = tk.Tk()
    edit_window = EditWindow(test_conf, glass_options=conf_list)
    ttk.Button(root, text = "Hit me to show edit window", command=edit_window.show)\
        .pack(padx=15, pady=15, fill=tk.BOTH, expand=True)
    ttk.Button(root, text = "Print current config", command=lambda: print(test_conf))\
        .pack(padx=15, pady=15, fill=tk.BOTH, expand=True)
    root.title("Root tkinter window")
    root.minsize(240, 200)
    # edit_window.show()
    root.mainloop()