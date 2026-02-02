import typing

import pygame

import tkinter as tk
import tkinter.filedialog as filebox
import tkinter.messagebox as msgbox
tkroot = tk.Tk()
tkroot.update()
tkroot.withdraw()

import os

import webbrowser

import random

import re

from dependencies.edit_window import EditWindow
from dependencies.pygame_text import Text
# from dependencies.error_detected import error_detected

from liquidglass import LiquidGlass, LiquidGlassButton


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

def load_image(path):
    global win, option_buttons
    if path in [None, "", 0, False]:
        win.fill((0, 0, 0))
        return
    image = pygame.image.load(path)
    image = resize(image)
    win.blit(image, (0,0))

def construct_blocks(window, config):
    glass_blocks: list[LiquidGlassButton] = []
    for block_configs in config:
        block_args = [v for v in block_configs]
        block_args[0] = window
        # print(block_args)
        glass_blocks.append(LiquidGlassButton(*block_args))
    return glass_blocks

def draw_all():
    global win, glass_blocks_conf, curr_img_path, option_buttons
    load_image(curr_img_path) # Reload image first to cover any proviously drawn stuff
    glass_blocks = construct_blocks(win, glass_blocks_conf)
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


class Test():
    @staticmethod
    def calc_distance_edge(w: int, h: int, r: int) -> list[list[list[int]]]:
        test_matrix = [[[0, 0, 0] for _ in range(w)] for _ in range(h)]
        for y, line in enumerate(test_matrix):
            for x, point in enumerate(line):
                test_matrix[y][x] = [int(item) for item in LiquidGlass.calc_distance_to_edge(\
                    LiquidGlass(pygame.Surface((w, h)), 0, 0, w, h, radius=r), (x, y))]
            print(line)
        return test_matrix


# Some global configs
curr_img_path = ""
glass_blocks_conf = []

# Initialize the main window
pygame.init()
win = pygame.display.set_mode((1280,720), pygame.SCALED)
pygame.display.set_caption("Liquid Glass Playground")
SCREEN_SIZE = (tkroot.winfo_screenwidth(), tkroot.winfo_screenheight())
loop_events = []

# Initialize the edit window
glass_options = {
    "Comment": "str", 
    "X-position": "int", 
    "Y-position": "int", 
    "Width": "int", 
    "Height": "int", 
    "Depth (Z-height)": "int", 
    "Round corner radius": "int", 
    "Blur radius": "int", 
    "Background color": "hex_color", 
    "Alpha": "float", 
    "Text": "str", 
    "Text font": "str", 
    "Text size": "int", 
    "Text color": "hex_color", 
    }
new_glass_template = [
    "New glass button {new_blocks_count}", 
    lambda: random.randint(0, 300), 
    lambda: random.randint(0, 300), 
    250, 
    250, 
    30, 
    15, 
    2, 
    "#ffffff", 
    0.2, 
    "Hello world! {new_blocks_count}", 
    "Arial", 
    32, 
    "#000000", 
    ]
edit_window = EditWindow(
    glass_blocks_conf, 
    glass_options=glass_options, 
    new_template=new_glass_template, 
    on_hide=draw_all, 
    )

# Initialize texts and buttons on main window
options = {
    "Apple Liquid Glass Effect in Pygame: Demo 2 (Playground)": \
        lambda: webbrowser.open("https://github.com/TotoWang-hhh/AppleGlassEffect/"),
    "Duplicatable glass blocks & Faster rendering": None,
    "2025 by rgzz666": lambda: webbrowser.open("https://github.com/TotoWang-hhh"),
    "Load image": \
        lambda: change_image(filebox.askopenfilename(
            title="Select an image to use as background")),
    "Open edit window": edit_window.show,
    "Redraw all": draw_all,
    }
option_buttons = make_option_buttons(win, options)

# Default glass
default_glass_conf = [v() if callable(v) else v for v in new_glass_template]
default_glass_conf[0] = "Default glass button"
default_glass_conf[list(glass_options.keys()).index("Text")] = "Hello world!"
glass_blocks_conf.append(tuple(default_glass_conf))

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
