import typing

import pygame
import warnings
import numpy as np

import tkinter as tk
if __name__ == "__main__":
    root = tk.Tk()
    root.withdraw()


class Text(object,):
    def __init__(self, screen, text: str, color: tuple = (255, 255, 255), 
                 pos: tuple[int,int] = (0, 0), fontname: str | None = "Arial", fontsize: int = 28, 
                 onclick: typing.Callable | None = None, loop_events_list:list|None=None, 
                 click_again_tip: bool = True):
        self.screen = screen
        self.text = text
        self.fontname = fontname
        self.fontsize = fontsize
        self.font = pygame.font.SysFont(fontname, fontsize)
        self.font.set_underline(onclick != None)
        self.surface = self.font.render(text, True, color)

        self.WIDTH = self.surface.get_width()
        self.HEIGHT = self.surface.get_height()

        self.x = pos[0]
        self.y = pos[1]

        if onclick == None:
            self.onclick = lambda:False
        else:
            if loop_events_list != None:
                loop_events_list.append(lambda event: self.check_click(event))
            else:
                warnings.warn("Set onclick function, but will not do event check "
                              "as loop_events_list is not given")
            self.onclick = onclick
        
        self.click_again_tip = click_again_tip

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
            text_surface = self.font.render(self.text, True, text_color)
            self.screen.blit(text_surface, (self.x, self.y))
        except Exception:
            # If error, back to the original text
            warnings.warn("Not able to inver color, falling back to default (white).")
            self.screen.blit(self.surface, (self.x, self.y))
         
    def check_click(self, event: pygame.event.Event):
        if event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:
                position = event.pos
                x_match = self.x < position[0] < self.x + self.WIDTH
                y_match = self.y < position[1] < self.y + self.HEIGHT
                if x_match and y_match:
                    return self.onclick()
                else:
                    return False
        elif event.type == pygame.WINDOWFOCUSGAINED and self.click_again_tip:
            position = pygame.mouse.get_pos()
            x_match = self.x < position[0] < self.x + self.WIDTH
            y_match = self.y < position[1] < self.y + self.HEIGHT
            if x_match and y_match:
                show_click_again_tip("Click again to activate button")


def show_click_again_tip(text="Click once more..."):
    tip = tk.Toplevel()
    tip.overrideredirect(True)
    tip.attributes("-topmost", True)
    tip.attributes("-disabled", True)
    label = tk.Label(tip, text=text, bg="green", fg="white", padx=10, pady=5)
    label.pack()

    # Place at mouse pos
    x, y = tip.winfo_pointerx() + 16, tip.winfo_pointery() + 16
    tip.geometry(f"+{x}+{y}")

    # 1.5 秒后自动关闭
    tip.after(1500, tip.destroy)