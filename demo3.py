import typing

import pygame

import tkinter as tk
import tkinter.ttk as ttk
import tkinter.filedialog as filebox
import tkinter.messagebox as msgbox
tkroot = tk.Tk()
tkroot.withdraw()

import webbrowser

import os

import random

import re
import time

from dependencies.pygame_text import Text
from liquidglass import LiquidGlass


def load_image(path):
    global win, wallpaper
    if path in [None, "", 0, False]:
        win.fill((0, 0, 0))
        return
    image = pygame.image.load(path)
    image = resize(image)
    wallpaper = image
    win.blit(image, (0,0))

def construct_blocks(config):
    glass_blocks: list[LiquidGlass] = []
    for block_args in config:
        glass_blocks.append(LiquidGlass(win, 
            block_args[1], block_args[2], block_args[3], block_args[4], block_args[5], 
            block_args[6], block_args[7], ))
    return glass_blocks

def draw_all():
    global glass_blocks_conf, glass_blocks, curr_img_path, option_buttons, fps_texts, fps_data, \
           render_start_time, render_end_time
    # load_image(curr_img_path) # Reload image first to cover any proviously drawn stuff
    win.blit(wallpaper, (0, 0))
    render_start_time = time.time()
    for block in glass_blocks:
        block.render()
    render_end_time = time.time()
    draw_options(option_buttons) # Draw options finally to get it on top

def select_image():
    change_image(filebox.askopenfilename
                 (title="Select an image to use as background"))

def change_image(path):
    global curr_img_path
    if path in [None, "", 0, False]:
        return
    curr_img_path = path
    load_image(path)
    # draw_all()

def make_option_buttons(win, option_buttons: list | None=[]):
    global fps
    if option_buttons == None:
        option_buttons = []
    options = {
        "Apple Liquid Glass Effect in Pygame: Demo 3 (Realtime)": \
            lambda: webbrowser.open("https://github.com/TotoWang-hhh/AppleGlassEffect/"),
        "Moving glass block (Test rendering speed)": None,
        "2025 by rgzz666": lambda: webbrowser.open("https://github.com/TotoWang-hhh"),
        "Load image": select_image,
            }
    if option_buttons in [[], "", 0, False, None]:
        option_buttons = []
        for option_index in range(len(options.keys())):
            option_buttons.append(Text(win, list(options.keys())[option_index], 
                                       onclick=list(options.values())[option_index], 
                                       fontsize = 20, loop_events_list=loop_events))
    return option_buttons

def draw_options(option_buttons: list=[]):
    for button_index in range(len(option_buttons)):
        option_buttons[button_index].display((0, button_index * 20))

def make_fps_texts(fps_data):
    fps_texts = []
    for text in fps_data:
        fps_texts.append(Text(win, text, fontsize=20))
    return fps_texts

def update_fps(fps_texts, fps_data):
    # global fps_texts, fps_data, win_h
    for line, text in enumerate(fps_texts):
        text.text = fps_data[line]
        text.display((0, win_h - len(fps_texts) * 20 + line * 20 - 5))

def resize(image):
    global win_w, win_h
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
    win_w = new_w
    win_h = new_h
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

# Initialize the main window
pygame.init()
win = pygame.display.set_mode(size=(1280,720))
pygame.display.set_caption("Liquid Glass Real-time Rendering")
SCREEN_SIZE = pygame.display.list_modes()[0]
loop_events = []

# Some global configs
curr_img_path = ""
glass_blocks_conf = [
    ("Moving rounded square glass block", 50, 200, 250, 250, 30, 30, 0, "#ffffff", 0.05), 
    ("Moving round glass block", 350, 200, 250, 250, 30, 125, 0, "#ffffff", 0.05), 
    ]
# glass_blocks = []
glass_blocks = construct_blocks(glass_blocks_conf)
movement_speed = 10

wallpaper = pygame.Surface((1280, 720))
win_w = 1280
win_h = 720

# # The below line is for testing error detection only. Comment it in normal cases!
# error_detected()

# Initialize directions for each block
block_directions = [(random.choice([-1, 1]), random.choice([-1, 1])) for _ in glass_blocks]

frame_start_time = 0
frame_end_time = 0
render_start_time = 0
render_end_time = 0
fps = 0

# Initialize texts and buttons on main window
option_buttons = make_option_buttons(win, [])
fps_data = [
    "NaN fps", 
    "NaNms for glass blocks rendering", 
    "NaN% of total rendering time", 
    "NaNms for each block"
    ]
fps_texts = make_fps_texts(fps_data)

while True:
    frame_start_time = time.time()

    for event in pygame.event.get():
        for loop_event in loop_events:
            loop_event(event)
        if event.type == pygame.QUIT:
            os._exit(0)

    for i, block in enumerate(glass_blocks):
        x_dir, y_dir = block_directions[i]

        # Update position
        block.x += x_dir * movement_speed
        block.y += y_dir * movement_speed

        # Check for collisions with screen edges
        if block.x <= 0 or block.x + block.w >= win_w - movement_speed:
            block_directions[i] = (-x_dir, y_dir)  # Reverse x direction
        if block.y <= 0 or block.y + block.h >= win_h - movement_speed:
            block_directions[i] = (x_dir, -y_dir)  # Reverse y direction

    draw_all()
    frame_end_time = time.time()
    fps_data = [
        f"{round(1 / (frame_end_time - frame_start_time), 2)} fps", 
        f"{round((render_end_time - render_start_time) * 1000, 2)}ms for glass blocks rendering", 
        f"{round((render_end_time - render_start_time) / (frame_end_time - frame_start_time) * 100, 
                 2)}% of total rendering time", 
        f"{round((render_end_time - render_start_time) * 1000 / len(glass_blocks), 
                 2)}ms for each block", 
        ] 
    update_fps(fps_texts, fps_data)
    pygame.display.update()
    tkroot.update()
