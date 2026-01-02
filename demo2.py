# Please note that this is an UNFINISHED version that is aimed to render a rounded rectangle glass effect.
# I got stuck on calculating the distance from a specific point to the edge, as this may be out of my current knowledge base.
# Always remember I was never a CG expert but a ordinary high-school student.

import pygame

import tkinter
import tkinter.filedialog as filebox
tkroot = tkinter.Tk()
tkroot.withdraw()

from typing import Union
import os
import warnings

import webbrowser

import numpy as np
import math

from PIL import Image, ImageFilter, ImageDraw

class Config:
    HIGHLIGHT_DEFLECTION_HANDLED = False
    SHOW_GLASS_TOPOGRAPHY = False
    SHOW_HANDLED_ONLY = False
    OUTPUT_ROUNDED_CORNER_POINTS_DATA = False

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
                warnings.warn("Set onclick function, but will not do event check as loop_events_list is not given")
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

def get_between(original:Union[int, float], min_value:Union[int, float], 
                max_value:Union[int, float]) -> Union[int, float]:
    if original < min_value:
        result = min_value
    elif original > max_value:
        result = max_value
    else:
        result = original
    return result

def load_image(path):
    global win, option_buttons
    if path in [None, "", 0, False]:
        return
    image = pygame.image.load(path)
    image = resize(image)
    win.blit(image, (0,0))

def draw_all():
    # width, height = [int(item*0.7) for item in win.get_size()]
    glass_blocks = [
        LiquidGlass(50, 100, 250, 150),
        LiquidGlass(350, 50, 250, 250, radius=5),
        LiquidGlass(650, 50, 250, 250, blur=0),
        LiquidGlass(50, 350, 250, 250),
        LiquidGlass(350, 350, 250, 250, z=50),
        ]
    for block in glass_blocks:
        block.render()
    draw_options(win, option_buttons=option_buttons) # Draw options finally to get it on top

def change_image(path):
    load_image(path)
    draw_all()

def draw_options(win, option_buttons:list|None=[]):
    if option_buttons == None:
        option_buttons = []
    options = {"2025 by rgzz666": lambda: webbrowser.open("https://github.com/totowang-hhh"),
            "Load image": lambda: change_image(filebox.askopenfilename(title="Select an image to open")),
            "Set glass z-height": lambda: None,
            "Set blur radius": lambda: None,
            }
    if option_buttons in [[], "", 0, False, None]:
        option_buttons = []
        for option_index in range(len(options.keys())):
            option_buttons.append(Text(win, list(options.keys())[option_index], onclick=list(options.values())[option_index], 
                                    fontsize = 20, loop_events_list=loop_events))
    for button_index in range(len(option_buttons)):
        option_buttons[button_index].display((0,button_index * 20))
    return option_buttons

def resize(image):
    # 使用启动时保存的主屏分辨率
    screen_w, screen_h = SCREEN_SIZE

    img_w, img_h = image.get_width(), image.get_height()

    # 计算缩放比例，保证图片不超出屏幕，且短边不超过屏幕60%
    scale_w = screen_w / img_w
    scale_h = screen_h / img_h
    scale = min(scale_w, scale_h, 0.6 * screen_w / img_w, 0.6 * screen_h / img_h, 1.0)

    new_w = int(img_w * scale)
    new_h = int(img_h * scale)

    # 短边不超过屏幕60%
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

    # 缩放图片
    resized_img = pygame.transform.smoothscale(image, (new_w, new_h))
    # 缩放窗口
    pygame.display.set_mode((new_w, new_h))
    return resized_img

class LiquidGlass():

    def __init__(self, x, y, w, h, z=15, radius=15, blur=2):
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.z = z
        self.radius = radius
        self.blur = blur
        self.rect_mask_cache = None
        self.rect_mask_cache_params = (-1, -1, -1)

    def draw_rect(self):
        pygame.draw.rect(win, (100, 100, 100), 
                         (self.x, self.y, self.w, self.h), 
                         1, border_radius=self.radius)

    def get_rounded_rect_mask(self, width, height, radius):
        global rect_mask_cache, rect_mask_cache_params
        if self.rect_mask_cache_params == (width, height, radius):
            return self.rect_mask_cache
        # Use PIL to draw mask
        mask_img = Image.new("L", (width, height), 0)
        draw = ImageDraw.Draw(mask_img)
        draw.rounded_rectangle([0, 0, width-1, height-1], radius=radius, fill=255)
        mask = np.array(mask_img) > 0  # shape: (height, width)
        # Cache it!
        rect_mask_cache = mask.copy()
        rect_mask_cache_params = (width, height, radius)
        return rect_mask_cache

    def pixel_is_in_rounded_rect(self, x, y, mask):
        # 现在 mask.shape = (height, width)
        if 0 <= y < mask.shape[0] and 0 <= x < mask.shape[1]:
            return bool(mask[y, x])
        return False

    def calc_distance_to_edge(self, rect_radius:int, rect_size:tuple[int, int], 
                              point:tuple[int, int]):
        if not self.pixel_is_in_rounded_rect(point[0], point[1], 
                                             self.get_rounded_rect_mask(rect_size[0], rect_size[1], 
                                                                        rect_radius)):
            return (0,0)
        distance_x_handleedge = min(point[0], rect_size[0] - point[0])
        distance_y_handleedge = min(point[1], rect_size[1] - point[1])
        # This place is reserved for calculating distance from the point to edge of any other shapes.
        # The function currently simply returns the distance from the point to the handling edge.
        distance_x = distance_x_handleedge
        distance_y = distance_y_handleedge
        if (point[0] < rect_radius or point[0] > (rect_size[0] - rect_radius)) and \
            (point[1] < rect_radius or point[1] > (rect_size[1] - rect_radius)):
            if distance_x_handleedge != 0:
                distance_y = (rect_radius ** 2 - (rect_radius - distance_x_handleedge) ** 2) \
                    ** 0.5 - (rect_radius - distance_y_handleedge)
            else:
                distance_y = 0
            if distance_y_handleedge != 0:
                distance_x = (rect_radius ** 2 - (rect_radius - distance_y_handleedge) ** 2) \
                    ** 0.5 - (rect_radius - distance_x_handleedge)
            else:
                distance_x = 0
        data_error = type(distance_x) not in [int, float] or type(distance_y) not in [int, float]
        if Config.OUTPUT_ROUNDED_CORNER_POINTS_DATA or data_error:
            if not False in [point[0] < rect_radius or point[0] > (rect_size[0] - rect_radius),
                            point[1] < rect_radius or point[1] > (rect_size[1] - rect_radius),
                            self.pixel_is_in_rounded_rect(point[0],point[1], 
                                                          self.get_rounded_rect_mask(rect_size[0],
                                                                                     rect_size[1],
                                                                                     rect_radius)),
                            ] or data_error:
                print(f"Point {point} has distance to:")
                print(f"  Shape edge on x: {int(distance_x) if not data_error else distance_x}, "
                      f"on y: {int(distance_y) if not data_error else distance_y}"
                    "     * Note: Shape edge refers to the edge of the rounded rectangle part that "
                    "the glass taken up.")
                print(f"  Handle edge on x: {distance_x_handleedge}, on y: "
                      f"{int(distance_y_handleedge)}"
                    "     * Note: Handle edge refers to the edge of the rectangle region that the "
                    "rendering function handles.")
                if data_error:
                    print("  * This output is due to a data error.")
                    return (0, 0)
        return (int(distance_x), int(distance_y))

    deflection_offset_cache = {}
    def calc_deflection_offset(self, z_height:int, distance_to_edge:int) -> int:
        global deflection_offset_cache
        try:
            if str(distance_to_edge) in self.deflection_offset_cache.keys():
                offset = self.deflection_offset_cache[str(distance_to_edge)]
            else:
                point_z_height = (z_height ** 2 - distance_to_edge ** 2) ** 0.5
                slope_gradient = 0.5 * math.pi - math.atan(distance_to_edge / point_z_height)
                offset = math.tan(slope_gradient) * point_z_height
                self.deflection_offset_cache[str(distance_to_edge)] = offset
        except:
            offset = 0
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
        z_height = self.z
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
        blur_surface = pygame.image.frombuffer(arr_blur.tobytes(), (width, height), "RGBA").convert_alpha()
        win.blit(blur_surface, (base_x, base_y))
        ## Deflection, the key part must be self-written :)
        rect_mask = self.get_rounded_rect_mask(width, height, rect_radius)
        pixels = []
        for y in range(height):
            pixels.append([])
            for x in range(width):
                pixels[y].append(tuple(win.get_at((base_x+x,base_y+y))))
            # print(base_pixels[y]) # Never uncomment this line unless u wanna blow up ur console
        # base_pixels = pixels # Use base_pixels to store original pixels info after blur
        for y in range(len(pixels)):
            for x in range(len(pixels[y])):
                pixel_handled = [False, False]
                after_x = x
                after_y = y
                distance_to_edge = self.calc_distance_to_edge(rect_radius, (width, height), (x, y))
                if (y < z_height or (y > (height - z_height))) and self.pixel_is_in_rounded_rect(x, y, rect_mask):
                    pixel_handled[1] = True
                    try:
                        y_offset = self.calc_deflection_offset(z_height, distance_to_edge[1])
                        if y > (height - z_height):
                            y_offset = -y_offset
                            # y_offset = 0
                    except:
                        y_offset = 0
                    y_offset = int(round(y_offset, 0))
                    after_y = get_between(y + y_offset, 0, height-1)
                if (x < z_height or (x > (width - z_height))) and \
                   self.pixel_is_in_rounded_rect(x, y, rect_mask):
                    pixel_handled[0] = True
                    try:
                        x_offset = self.calc_deflection_offset(z_height, distance_to_edge[0])
                        if x > (width - z_height):
                            x_offset = -x_offset
                            # x_offset = 0
                    except:
                        x_offset = 0
                    x_offset = int(round(x_offset, 0))
                    # x_offset = 0
                    after_x = get_between(x + x_offset, 0, width-1)
                pixels[y][x] = pixels[after_y][after_x]
                # pixels[y][x] = (0,0,255,255)
                # pixels[after_y][after_x] = (int(y * (255 / z_height)), 0, 0, 255)
                if Config.HIGHLIGHT_DEFLECTION_HANDLED:
                    g_value = 155 if self.pixel_is_in_rounded_rect(x, y, rect_mask) else 0
                    if not False in pixel_handled:
                        pixels[y][x] = (255,g_value,155,255)
                    elif pixel_handled[0]:
                        pixels[y][x] = (255,g_value,0,255)
                    elif pixel_handled[1]:
                        pixels[y][x] = (0,g_value,255,255)
                if Config.SHOW_GLASS_TOPOGRAPHY: 
                    approx_pixel_z_height = min(distance_to_edge[0], distance_to_edge[1]) / z_height
                    approx_pixel_z_height = get_between(approx_pixel_z_height, 0, 1)
                    pixels[y][x] = (int(255*approx_pixel_z_height),int(255-255*approx_pixel_z_height),0,255)
        ## Draw!
        if Config.SHOW_HANDLED_ONLY:
            win.fill((0,0,0,255))
        for y in range(len(pixels)):
            for x in range(len(pixels[y])):
                try:
                    win.set_at((base_x+x, base_y+y), pixels[y][x])
                except:
                    print(f"Invalid pixel color @ ({base_x+x},{base_y+y}) with RGB(A) {pixels[y][x]}")
                    win.set_at((base_x+x, base_y+y), (155,0,255,255))
        # Finally draw the outer frame
        self.draw_rect()

pygame.init()
win = pygame.display.set_mode(size=(1280,720))
pygame.display.set_caption("Apple Glass Reflection Effect Demo")
SCREEN_SIZE = pygame.display.list_modes()[0]
loop_events = []

option_buttons = draw_options(win, [])

while True:
    for event in pygame.event.get():
        for loop_event in loop_events:
            loop_event(event)
        if event.type == pygame.QUIT:
            os._exit(0)
    pygame.display.update()