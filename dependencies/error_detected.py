import sys
import subprocess
import ctypes
import shutil
import os
import webbrowser


def askyesno(title: str, message: str) -> bool:

    match sys.platform:
    # ---------------- Windows ----------------
        case "win32":
            # MB_YESNO = 0x04
            # IDYES = 6, IDNO = 7
            res = ctypes.windll.user32.MessageBoxW(
                0,
                message,
                title,
                0x04 | 0x20  # YESNO | ICON_QUESTION
            )
            return res == 6

    # ---------------- macOS ----------------
        case "darwin":
            # AppleScript display dialog
            script = f'''
            display dialog "{message.replace('"', '\\"')}" ¬
            with title "{title.replace('"', '\\"')}" ¬
            buttons {{"No", "Yes"}} default button "Yes"
            '''
            try:
                subprocess.check_output(
                    ["osascript", "-e", script],
                    stderr=subprocess.DEVNULL
                )
                return True
            except subprocess.CalledProcessError:
                return False

    # ---------------- Linux / Unix ----------------
        case _:
            # Try Zenity first (GNOME / general)
            if shutil.which("zenity"):
                proc = subprocess.run(
                    [
                        "zenity",
                        "--question",
                        "--title", title,
                        "--text", message
                    ]
                )
                return proc.returncode == 0

            # Then try kdialog（KDE）
            if shutil.which("kdialog"):
                proc = subprocess.run(
                    [
                        "kdialog",
                        "--title", title,
                        "--yesno", message
                    ]
                )
                return proc.returncode == 0

            # If no GUI tool
            return input(f"{title}: {message} (y/N)").lower() == "y"


def error_detected():
    if askyesno("Liquid Glass Playground: Error Detected", 
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
        if askyesno(
            "Feedback Anyway?", "Would you still like to go to the issues page for a feedback?"
            ):
            webbrowser.open("https://github.com/TotoWang-hhh/AppleGlassEffect/issues")

if __name__ == "__main__":
    # Test
    error_detected()