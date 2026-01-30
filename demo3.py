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
import time

from PIL import Image, ImageFilter, ImageDraw


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
        except Exception as e:
            # If error, back to the original text
            text_color = (255, 255, 255)
        font = pygame.font.SysFont(self.fontname, self.fontsize)
        text_surface = font.render(self.text, True, text_color)
        self.screen.blit(text_surface, (self.x, self.y))
         
    def check_click(self, event: pygame.event.Event):
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


class LiquidGlass():

    def __init__(
            self, 
            parent: pygame.Surface, 
            x: int, 
            y: int, 
            w: int, 
            h: int, 
            z: int = 15, 
            radius: int = 15, 
            blur: int = 2, 
            background: str = "#ffffff", 
            alpha: float = 0.2
            ):
        self.parent = parent
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
        ## Basic backdrop blur, written by GitHub Copilot
        rect = pygame.Rect(self.x, self.y, self.w, self.h)
        bg_surface = self.parent.subsurface(rect).copy()
        arr = pygame.surfarray.array3d(bg_surface)
        arr = np.transpose(arr, (1, 0, 2))
        if self.blur != 0:
            pil_img = Image.fromarray(arr)
            # Blur
            pil_img = pil_img.filter(ImageFilter.GaussianBlur(radius=self.blur))
            # Round corner mask
            mask_img = Image.new("L", (self.w, self.h), 0)
            draw = ImageDraw.Draw(mask_img)
            draw.rounded_rectangle([0, 0, self.w-1, self.h-1], radius=self.radius, fill=255)
            pil_img.putalpha(mask_img)
            # Convert to pygame surface and draw
            arr = np.array(pil_img)
        else:
            arr =arr
        ## Deflection, the key part must be self-written :)
        pixels_origin: list[list[tuple]] = arr.copy()
        for y in range(len(arr)):
            for x in range(len(arr[y])):
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
                    arr[y][x] = pixels_origin[after_y][after_x]
                if Config.SHOW_GLASS_TOPOGRAPHY: 
                    approx_pixel_z_height = distance_to_edge[2]
                    approx_pixel_z_height = get_between(approx_pixel_z_height, 0, 1)
                    arr[y][x] = (int(255*approx_pixel_z_height),
                                    int(255-255*approx_pixel_z_height),0,255)
        # Draw deflection
        handled_surface = pygame.image.frombuffer(arr.tobytes(), (self.w, self.h), "RGB").convert_alpha()
        self.parent.blit(handled_surface, (self.x, self.y))
        ## Translucent layer
        overlay = pygame.Surface((self.w, self.h), pygame.SRCALPHA)
        pygame.draw.rect(
            overlay, 
            self.translucent, 
            pygame.Rect(0, 0, self.w, self.h), 
            border_radius = self.radius
            )
        self.parent.blit(overlay, (self.x, self.y))
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
