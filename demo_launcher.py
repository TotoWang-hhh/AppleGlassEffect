import tkinter as tk
import tkinter.ttk as ttk
import tkinter.messagebox as msgbox
import os


DESCRIPTION = (
"This program is used as an entrance of all demos on some platforms to reduce disk space of "
"executables. You may select one of the demos from below and have a try.")
DEMO_NAMES = [
    "Old Method (Demo 1)", 
    "Playground (Demo 2)", 
    "Real-time Rendering (Demo 3)", 
    ]


def launch_demo(demo_num: int):
    global DEMO_NAMES, win
    win.destroy()
    match demo_num:
        case 1:
            import demo1
        case 2:
            import demo2
        case 3:
            import demo3
        case _:
            msgbox.showerror("No Such Demo", "No such demo registered in this launcher!")
    print("The demo was closed or has been terminated.")
    os._exit(0)


win = tk.Tk()
win.title("Liquid Glass in Pygame: Demo Launcher")

desc_text = tk.Label(win, text=DESCRIPTION, wraplength=300)
desc_text.pack(fill=tk.X)
desc_text.master.bind("<Configure>", lambda event: \
    desc_text.config(wraplength=event.width) if event.widget == desc_text.master else None)

for demo_index, demo_name in enumerate(DEMO_NAMES):
    ttk.Button(win, text=demo_name, command=lambda demo_num=demo_index + 1: launch_demo(demo_num))\
        .pack(fill=tk.X)

# Size related stuff
win.update()
win.minsize(win.winfo_width(), win.winfo_height())
win.resizable(False, False)

win.mainloop()