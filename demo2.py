import pygame

import tkinter as tk
import tkinter.ttk as ttk
import tkinter.filedialog as filebox
import tkinter.messagebox as msgbox
tkroot = tk.Tk()
tkroot.withdraw()

import typing
import os
import warnings

import webbrowser

import numpy as np
import random

import re

from PIL import Image, ImageFilter, ImageDraw

from editable_treeview import EditableTreeview

class Config:
    SHOW_GLASS_TOPOGRAPHY = False

class Text(object,):
    def __init__(self, screen, text:str, color=(255, 255, 255), pos:tuple[int,int]=(0, 0), 
                 fontname:str="Arial", fontsize:int=28, onclick=lambda:None, 
                 loop_events_list:list|None=None, **kwargs):
        self.screen = screen
        self.text = text
        self.fontname = fontname
        self.fontsize = fontsize
        font = pygame.font.SysFont(fontname, fontsize)
        self.surface = font.render(text, True, color)

        self.WIDTH = self.surface.get_width()
        self.HEIGHT = self.surface.get_height()

        self.x = pos[0]
        self.y = pos[1]

        if onclick in [False, None, 0]:
            self.onclick = lambda:False
        else:
            if loop_events_list != None:
                loop_events_list.append(lambda event: self.check_click(event))
            else:
                warnings.warn("Set onclick function, but will not do event check "
                              "as loop_events_list is not given")
            self.onclick = onclick

    def display(self,pos:tuple[int,int]=(0,0)):
        self.x = pos[0]
        self.y = pos[1]

        rect = pygame.Rect(self.x, self.y, self.WIDTH, self.HEIGHT)
        # Code to inverse text color, written by GitHub Copilot
        try:
            # Sample background at text area
            sub_surface = self.screen.subsurface(rect).copy()
            arr = pygame.surfarray.array3d(sub_surface)
            # Calc avg color
            avg_color = np.mean(arr.reshape(-1, 3), axis=0)
            r, g, b = avg_color.astype(int)
            # Invert color
            inv_r, inv_g, inv_b = 255 - r, 255 - g, 255 - b
            # Calc lightness, and change if necessary
            lum = 0.299*inv_r + 0.587*inv_g + 0.114*inv_b
            if lum < 128 and lum > 100:
                # If too dark
                inv_r = min(inv_r + 150, 255)
                inv_g = min(inv_g + 150, 255)
                inv_b = min(inv_b + 150, 255)
            elif lum >= 128 and lum < 150:
                # If too light
                inv_r = max(inv_r - 150, 0)
                inv_g = max(inv_g - 150, 0)
                inv_b = max(inv_b - 150, 0)
            text_color = (int(inv_r), int(inv_g), int(inv_b))
            # Re-render text with inverted color
            font = pygame.font.SysFont(self.fontname, self.fontsize)
            text_surface = font.render(self.text, True, text_color)
            self.screen.blit(text_surface, (self.x, self.y))
        except Exception:
            # If error, back to the origina; text
            self.screen.blit(self.surface, (self.x, self.y))
         
    def check_click(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                position = event.pos
                x_match = position[0] > self.x and position[0] < self.x + self.WIDTH
                y_match = position[1] > self.y and position[1] < self.y + self.HEIGHT
                if x_match and y_match:
                    return self.onclick()
                else:
                    return False

def get_between(original: int | float, min_value: int | float, 
                max_value: int | float) -> int | float: 
    if original < min_value:
        result = min_value
    elif original > max_value:
        result = max_value
    else:
        result = original
    return result

def hex_to_rgb(hex_color: str) -> tuple[int, int, int]:
    if hex_color.startswith("#"):
        hex_color = hex_color[1:]
    
    if not re.fullmatch(r"([0-9a-fA-F]{6})$", hex_color):
        # If not a valid hex color, return green
        return (0, 255, 0)

    return (
        int(hex_color[0:2], 16),
        int(hex_color[2:4], 16),
        int(hex_color[4:6], 16),
    )

def error_detected():
    if msgbox.askokcancel("Liquid Glass Playground: Error Detected", 
        "An error may be detected by internal code, and a force quit of this program was "
        "requested. \n\n"
        "You may also choose to ignore anyway, but please note that continue running this program "
        "may cause unexpected behavior and more following errors.\n\n"
        "The issues page of this project, where you can provide feedback, will then be opened in "
        "your browser. The console will be left open for you to copy relavent debug information "
        "if you accept to quit before the program actually terminates.\n\n"
        "\nProceed?"
        ):
        webbrowser.open("https://github.com/TotoWang-hhh/AppleGlassEffect/issues")
        input("\n\nCopy anything helpful from the console, then hit [ENTER] to quit... ")
        os._exit(1)
    else:
        if msgbox.askyesno(
            "Feedback Anyway?", "Would you still like to go to the issues page for a feedback?"
            ):
            webbrowser.open("https://github.com/TotoWang-hhh/AppleGlassEffect/issues")

def load_image(path):
    global win, option_buttons
    if path in [None, "", 0, False]:
        win.fill((0, 0, 0))
        return
    image = pygame.image.load(path)
    image = resize(image)
    win.blit(image, (0,0))

def construct_blocks(config):
    glass_blocks: list[LiquidGlass] = []
    for block_args in config:
        glass_blocks.append(LiquidGlass(
            block_args[1], block_args[2], block_args[3], block_args[4], block_args[5], 
            block_args[6], block_args[7], ))
    return glass_blocks

def draw_all():
    global glass_blocks_conf, curr_img_path, option_buttons
    load_image(curr_img_path) # Reload image first to cover any proviously drawn stuff
    glass_blocks = construct_blocks(glass_blocks_conf)
    for block in glass_blocks:
        block.render()
    draw_options(option_buttons=option_buttons) # Draw options finally to get it on top

def change_image(path):
    global curr_img_path
    if path in [None, "", 0, False]:
        return
    curr_img_path = path
    draw_all()

def make_option_buttons(win, options: dict = {}):
    option_buttons = []
    for option_index in range(len(options.keys())):
        option_buttons.append(Text(win, list(options.keys())[option_index], 
                                    onclick=list(options.values())[option_index], 
                                    fontsize = 20, loop_events_list=loop_events))
    return option_buttons

def draw_options(option_buttons: list=[]):
    for button_index in range(len(option_buttons)):
        option_buttons[button_index].display((0,button_index * 20))

def resize(image):
    # Get screen and image size
    screen_w, screen_h = SCREEN_SIZE

    img_w, img_h = image.get_width(), image.get_height()

    # Calc destinate size, short side not longer than 60% of screen size
    scale_w = screen_w / img_w
    scale_h = screen_h / img_h
    scale = min(scale_w, scale_h, 0.6 * screen_w / img_w, 0.6 * screen_h / img_h, 1.0)

    new_w = int(img_w * scale)
    new_h = int(img_h * scale)

    if new_w < new_h:
        max_short = int(screen_w * 0.6)
        if new_w > max_short:
            scale = max_short / img_w
            new_w = max_short
            new_h = int(img_h * scale)
    else:
        max_short = int(screen_h * 0.6)
        if new_h > max_short:
            scale = max_short / img_h
            new_h = max_short
            new_w = int(img_w * scale)

    # Resize image
    resized_img = pygame.transform.smoothscale(image, (new_w, new_h))
    # Resize window
    pygame.display.set_mode((new_w, new_h))
    return resized_img

class EditWindow(tk.Toplevel):

    def __init__(self):
        # Initialize as a tkinter window
        tk.Toplevel.__init__(self)
        # Options list
        self.OPTION_NAMES = [
            "Comment", "X-position", "Y-position", "Width", "Height", "Depth (Z-height)", 
            "Round corner radius", "Blur radius", "Background color", "Alpha"
            ]
        # Current config buffer
        self.curr_config = []
        # Misc
        self._new_blocks_count = 0
        self.selected_block_index = -1 # -1 for not selected
        # Widgets inside window
        self.state_part = tk.Label(self, text="Initializing...", bg="yellow", anchor=tk.W)
        self.state_part.pack(fill=tk.X, side=tk.BOTTOM)
        self.left_part = ttk.LabelFrame(self, text="Glass blocks")
        ttk.Button(self.left_part, text="+ Add", 
                   command=self.add_block).pack(fill=tk.X, side=tk.BOTTOM)
        ttk.Button(self.left_part, text="× Remove", 
                   command=self.del_block).pack(fill=tk.X, side=tk.BOTTOM)
        self.glass_list = tk.Listbox(self.left_part, selectmode=tk.SINGLE)
        self.glass_list.pack(fill=tk.BOTH, expand=True)
        self.glass_list.bind("<<ListboxSelect>>", self.select_block)
        self.left_part.pack(side = tk.LEFT, fill = tk.Y)
        self.options_area = ttk.LabelFrame(self, text="Options")
        self.options_area.pack(fill = tk.BOTH, expand = True)
        self.option_entries = EditableTreeview(self.options_area, ["Attribute", "Value"], 
                                               bind_key='<Double-Button-1>', show='headings', 
                                               data=[(option_name, "") for option_name in \
                                                     self.OPTION_NAMES], non_editable_columns="#1")
        self.option_entries.pack(fill=tk.BOTH, expand=True)
        tk.Label(self.options_area, text="💡 Double click a field to edit").pack(fill = tk.BOTH)
        # Rename the window
        self.title("Edit Glass Blocks Configuration")
        # Event binding while editing and finishing editing
        self.option_entries.on_enter_edit = self.on_enter_edit
        self.option_entries.on_finish_edit = self.on_finish_edit
        # Set close button hides the window to prevent close
        self.protocol("WM_DELETE_WINDOW", self.hide)
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
        draw_all()
    
    def set_state(self, text: str, color: str | None="lightgreen"):
        """Set content in state indicator."""
        self.state_part["text"] = text
        if color != None:
            self.state_part["bg"] = color
        self.update()

    def read_config(self):
        """Read current global config to buffer."""
        global glass_blocks_conf
        self.curr_config = [list(block_args) for block_args in glass_blocks_conf]
    
    def save_config(self):
        """Save current buffer to global config."""
        global glass_blocks_conf
        glass_blocks_conf = [tuple(block_args) for block_args in self.curr_config]

    def load_curr_config(self):
        """Load glass list in current config buffer into the edit window."""
        self.glass_list.delete(0, tk.END)
        for index, block in enumerate(self.curr_config):
            # print(f"Load {block[0]} into edit window")
            self.glass_list.insert(tk.END, f"[{index}] {block[0]}")

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

    def convert_attrs(self) -> list | None:
        """Converts attr config string into types they should be."""
        ATTR_TYPES = [
            "str", "int", "int", "int", "int", "int", "int", "int", "hex_color", "float", 
            ]
        for block_index, attrs in enumerate(self.curr_config):
            result = []
            if len(attrs) != len(ATTR_TYPES):
                self.set_state(f"Wrong number of attribute values: expected {len(ATTR_TYPES)} but "
                               f"got {len(attrs)}", color="pink")
                error_detected()
            for index, attr in enumerate(attrs):
                if type(attr) is str: # Only handles string
                    match ATTR_TYPES[index].lower():
                        case "str":
                            result.append(attr)
                        case "int":
                            if attr.isdigit():
                                result.append(int(attr))
                            else:
                                self.set_state(f"Value '{attr}' for {self.OPTION_NAMES[index]} "
                                                "must be an integer! Check your entered value and "
                                                "retry.", color="pink")
                                result.append(0)
                                self.select_field(block_index, index, silent=True)
                                return
                        case "float":
                            if attr.isdigit():
                                result.append(float(attr))
                            else:
                                self.set_state(f"Value '{attr}' for {self.OPTION_NAMES[index]} "
                                                "must be a float! Check your entered value and "
                                                "retry.", color="pink")
                                result.append(0)
                                self.select_field(block_index, index, silent=True)
                                return
                        case "hex_color":
                            if re.fullmatch(r"#?([0-9a-fA-F]{6})$", attr):
                                result.append(attr)
                            else:
                                self.set_state(f"Value '{attr}' for {self.OPTION_NAMES[index]} "
                                                "must be a hex color! Check your entered value and "
                                                "retry.", color="pink")
                                result.append("#00ff00")
                                self.select_field(block_index, index, silent=True)
                                return
                        case _:
                            self.set_state(f"Wrong required type '{ATTR_TYPES[index]}' for arg "
                                           f"{self.OPTION_NAMES[index]}!", color="pink")
                            result.append(attr)
                            error_detected()
                            return
                else: # If is not string, we treat it as already in correct type
                    result.append(attr)
            self.curr_config[block_index] = result.copy()
        return self.curr_config

    def add_block(self):
        """When adding a new glass block."""
        self._new_blocks_count += 1
        self.curr_config.append(
            [f"New glass block #{self._new_blocks_count}", 
            random.randint(0, 300), random.randint(0, 300), 250, 250, 30, 15, 2, "#ffffff", 0.3]
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
        # Save to config buffer
        self.curr_config[self.selected_block_index][self.option_entries.index(editing_row)] = \
            after_value

class LiquidGlass():

    def __init__(
            self, 
            x: int, 
            y: int, 
            w: int, 
            h: int, 
            z: int = 15, 
            radius: int = 15, 
            blur: int = 2, 
            background: str = "#ffffff", 
            alpha: float = 0.3
            ):
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.z = z
        self.radius = radius
        self.blur = blur
        bg_rgb = hex_to_rgb(background)
        self.translucent = (bg_rgb[0], bg_rgb[1], bg_rgb[2], int(alpha * 255))

    def draw_rect(self):
        pygame.draw.rect(win, (100, 100, 100), 
                         (self.x, self.y, self.w, self.h), 
                         1, border_radius=self.radius)

    def calc_distance_to_edge(self, point: tuple[int, int]) -> list[int]:
        # Handle edge: The rectangle shaped edge where the code handles
        # Shape edge: The actual shape where the glass block takes up
        rect_size = [self.w, self.h]
        result: list[int] = [0, 0]
        for direction, d_handle_neighbor in enumerate(point): 
            # (var) direction: int, either 0 for x or 1 for y
            # (expression) 1 - direction: mask (invert) the direction value to indicate direction 
            #                             of the calculation result
            # The coords of the point is the distance to handle edge.
            # For such distance in each direction, we sort them into 3 cases to treat in different 
            # way when getting the distance to the shape edge in the other direction (e.g. 
            # d_handle in x => Recognized as case A => d_shape in y): 
            d_handle = point[1-direction]
            if self.radius <= d_handle_neighbor <= (rect_size[direction] - self.radius):
                # Case 1: in middle rect part
                # Shape edge is the handle edge
                result[1-direction] = min(d_handle, rect_size[1-direction] - d_handle)
            else:
                # Case 2 & 3: Point is in either edge in such direction (within round corner region)
                # |- Case 2: Left / Upper edges
                # |- Case 3: Right / Lower edges
                # Treat round corner regions region as a segment (1/4 circle), we convert them into 
                # case 3 to make calculations easier
                # (var) d_edge: distance of a point to edge of inner rectangle area
                if d_handle_neighbor > (rect_size[direction] - d_handle_neighbor):
                    d_handle_neighbor_abs = rect_size[direction] - d_handle_neighbor
                else:
                    d_handle_neighbor_abs = d_handle_neighbor
                d_neighbor_edge = (self.radius - d_handle_neighbor_abs)
                d_edge = min(d_handle, (rect_size[1-direction] - d_handle)) - self.radius
                d_shape = d_edge + (self.radius ** 2 - d_neighbor_edge ** 2) ** 0.5
                result[1-direction] = d_shape
        # result.append((result[0] ** 2 + result[1] ** 2) ** 0.5) # Shortest straight line distance
        return result

    def calc_deflection_offset(self, distance_to_edge:int, max_offset: int) -> int:
        if not 0 < distance_to_edge < self.z:
            return 0
        # point_z_height = (2 * self.z * distance_to_edge - distance_to_edge ** 2) ** 0.5
        offset = (max_offset / self.z ** 4) * (distance_to_edge - self.z) ** 4
        offset = int(round(offset, 0))
        return offset

    def render(self):
        """This is used to draw or update the liquid glass block"""
        global win
        ## Load self config
        base_x = self.x
        base_y = self.y
        width = self.w
        height = self.h
        rect_radius = self.radius
        blur_radius = self.blur
        ## Basic backdrop blur, written by GitHub Copilot
        rect = pygame.Rect(base_x, base_y, width, height)
        bg_surface = win.subsurface(rect).copy()
        arr = pygame.surfarray.array3d(bg_surface)
        arr = np.transpose(arr, (1, 0, 2))
        pil_img = Image.fromarray(arr)
        # Blur
        pil_img = pil_img.filter(ImageFilter.GaussianBlur(radius=blur_radius))
        # Round corner mask
        mask_img = Image.new("L", (width, height), 0)
        draw = ImageDraw.Draw(mask_img)
        draw.rounded_rectangle([0, 0, width-1, height-1], radius=rect_radius, fill=255)
        pil_img.putalpha(mask_img)
        # Convert to pygame surface and draw
        arr_blur = np.array(pil_img)
        blur_surface = pygame.image.frombuffer(arr_blur.tobytes(), 
                                               (width, height), "RGBA").convert_alpha()
        win.blit(blur_surface, (base_x, base_y))
        ## Deflection, the key part must be self-written :)
        pixels: list[list[tuple]] = []
        # Add calculated blurred region to a pixel array
        for y in range(height):
            pixels.append([])
            for x in range(width):
                pixels[y].append(tuple(win.get_at((base_x+x,base_y+y))))
        # Calculate deflection
        pixels_origin: list[list[tuple]] = pixels.copy()
        for y in range(len(pixels)):
            for x in range(len(pixels[y])):
                pixel_handled = [False, False]
                # x and y after deflection
                after_x = x
                after_y = y
                # Calc distance to edge
                distance_to_edge = self.calc_distance_to_edge((x, y))
                if distance_to_edge[0] > 0 and distance_to_edge[1] > 0: 
                    # ↑ This means that the pixel is within the shape
                    # Calc after x and y base on distance to edge
                    x_offset = self.calc_deflection_offset(distance_to_edge[0], self.w)
                    y_offset = self.calc_deflection_offset(distance_to_edge[1], self.h)
                    # If is right / bottom side, negative the offset
                    if x > (self.w - self.z):
                        x_offset = - x_offset
                    if y > (self.h - self.z):
                        y_offset = - y_offset
                    after_x += x_offset
                    after_y += y_offset
                    # Correct out of range destinate x and y values
                    after_x = int(get_between(after_x, 0, self.w - 1))
                    after_y = int(get_between(after_y, 0, self.h - 1))
                    # Handle the offset
                    pixels[y][x] = pixels_origin[after_y][after_x]
                if Config.SHOW_GLASS_TOPOGRAPHY: 
                    approx_pixel_z_height = distance_to_edge[2]
                    approx_pixel_z_height = get_between(approx_pixel_z_height, 0, 1)
                    pixels[y][x] = (int(255*approx_pixel_z_height),
                                    int(255-255*approx_pixel_z_height),0,255)
        # Draw deflection
        for y in range(len(pixels)):
            for x in range(len(pixels[y])):
                try:
                    win.set_at((base_x+x, base_y+y), pixels[y][x])
                except:
                    print(f"Invalid pixel color @ ({base_x+x},{base_y+y}) "
                           "with RGB(A) {pixels[y][x]}")
                    win.set_at((base_x+x, base_y+y), (155,0,255,255))
        ## Translucent layer
        overlay = pygame.Surface((self.w, self.h), pygame.SRCALPHA)
        pygame.draw.rect(
            overlay, 
            self.translucent, 
            pygame.Rect(0, 0, self.w, self.h), 
            border_radius = self.radius
            )
        win.blit(overlay, (self.x, self.y))
        ## Finally draw the outer frame
        self.draw_rect()


class Test():
    @staticmethod
    def calc_distance_edge(w: int, h: int, r: int) -> list[list[list[int]]]:
        test_matrix = [[[0, 0, 0] for _ in range(w)] for _ in range(h)]
        for y, line in enumerate(test_matrix):
            for x, point in enumerate(line):
                test_matrix[y][x] = [int(item) for item in LiquidGlass.calc_distance_to_edge(\
                    LiquidGlass(0, 0, w, h, radius=r), (x, y))]
            print(line)
        return test_matrix

# Initialize the main window
pygame.init()
win = pygame.display.set_mode(size=(1280,720))
pygame.display.set_caption("Liquid Glass Playground")
SCREEN_SIZE = pygame.display.list_modes()[0]
loop_events = []

# Initialize the edit window
edit_window = EditWindow()

# Initialize texts and buttons on main window
options = {
    "Apple Liquid Glass Effect in Pygame: Demo 2 (Playground)": \
        lambda: webbrowser.open("https://github.com/TotoWang-hhh/AppleGlassEffect/"),
    "Moving glass block (Test rendering speed)": None,
    "2025 by rgzz666": lambda: webbrowser.open("https://github.com/TotoWang-hhh"),
    "Load image": lambda: change_image(filebox.askopenfilename\
                                        (title="Select an image to use as background")),
    }
option_buttons = make_option_buttons(win, options)

# Some global configs
curr_img_path = ""
glass_blocks_conf = [
    ("Default glass block", 50, 200, 250, 250, 30, 15, 2, "#ffffff", 0.3)
    ]

# Initial draw
draw_all()

# # The below line is for testing error detection only. Comment it in normal cases!
# error_detected()

while True:
    for event in pygame.event.get():
        for loop_event in loop_events:
            loop_event(event)
        if event.type == pygame.QUIT:
            os._exit(0)
    pygame.display.update()
    tkroot.update()
