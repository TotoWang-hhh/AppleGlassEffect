import typing

import pygame
from PIL import Image, ImageFilter, ImageDraw
import re
import numpy as np


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
            alpha: float = 0.2, 
            text: str = "", 
            text_color: str = "#000000", 
            ):
        self.parent: pygame.Surface = parent
        self.x: int = x
        self.y: int = y
        self.w: int = w
        self.h: int = h
        self.z: int = z
        self.radius: int = radius
        self.blur: int = blur
        bg_rgb: tuple = hex_to_rgb(background)
        self.translucent: tuple = (bg_rgb[0], bg_rgb[1], bg_rgb[2], int(alpha * 255))
        self.highlight_thickness: int = int(max(self.w, self.h) * 0.01)
        self.text: str = text
        self.text_color: tuple = hex_to_rgb(text_color)

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
        return result

    def calc_deflection_offset(self, distance_to_edge:int, max_deflection: int) -> int:
        if not 0 < distance_to_edge < self.z:
            return 0
        offset = (max_deflection / self.z ** 4) * (distance_to_edge - self.z) ** 4
        offset = int(round(offset, 0))
        return offset

    def render(self):
        """This is used to draw or update the liquid glass block"""
        ### Off-screen calculated layers
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
            arr = arr
        ## Deflection, the key part must be self-written :)
        pixels_origin = arr.copy()
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
        # Draw deflection
        match len(arr[0][0]):
            case 3:
                color_type = "RGB"
            case 4:
                color_type = "RGBA"
        handled_surface = pygame.image.frombuffer(arr.tobytes(), (self.w, self.h), 
                                                  color_type).convert_alpha()
        self.parent.blit(handled_surface, (self.x, self.y))
        ### Overlays
        ## Translucent layer
        overlay = pygame.Surface((self.w, self.h), pygame.SRCALPHA)
        pygame.draw.rect(
            overlay, 
            self.translucent, 
            pygame.Rect(0, 0, self.w, self.h), 
            border_radius = self.radius
            )
        self.parent.blit(overlay, (self.x, self.y))
        del overlay
        ## Outer frame (highlight)
        overlay = pygame.Surface((self.w, self.h), pygame.SRCALPHA)
        HIGHLIGHT_ALPHA = 0.4
        pygame.draw.rect(overlay, (255, 255, 255, int(HIGHLIGHT_ALPHA * 255)), 
                        (0, 0, self.w, self.h), self.highlight_thickness, 
                        border_radius=self.radius)
        self.parent.blit(overlay, (self.x, self.y))
        del overlay


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