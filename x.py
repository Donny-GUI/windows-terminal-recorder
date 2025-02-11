"""
Windows Terminal Gif Maker

Author: Donald Guiles

Usage:
    python main.py

Description:
    This program will record the terminal screen and save it as an GIF file

"""

import time
import os
import numpy as np
from PIL import Image
import cv2
import mss
import imageio
import pygetwindow as gw
from rich.live import Live
from rich.table import (
    Table,
    Text
)
from typing import Tuple
from multiprocessing import Process, Queue, freeze_support
from rich.status import Status




dot      = ["         ", "         ", "         ", "         ", "  ██╗    ", "  ╚═╝    "]
zero     = [" ██████╗ ", "██╔═████╗", "██║██╔██║", "████╔╝██║", "╚██████╔╝", " ╚═════╝ "]
one      = ["   ██╗   ", "  ███║   ", "  ╚██║   ", "   ██║   ", "   ██║   ", "   ╚═╝   "]
two      = ["██████╗  ", "╚════██╗ ", " █████╔╝ ", "██╔═══╝  ", "███████╗ ", "╚══════╝ "]
three    = ["██████╗  ", "╚════██╗ ", " █████╔╝ ", " ╚═══██╗ ", "██████╔╝ ", "╚═════╝  "]
four     = ["██╗  ██╗ ", "██║  ██║ ", "███████║ ", "╚════██║ ", "     ██║ ", "     ╚═╝ "]
five     = ["███████╗ ", "██╔════╝ ", "███████╗ ", "╚════██║ ", "███████║ ", "╚══════╝ "]
six      = [" ██████╗ ", "██╔════╝ ", "███████╗ ", "██╔═══██╗", "╚██████╔╝", " ╚═════╝ "]
seven    = ["███████╗ ", "╚════██║ ", "    ██╔╝ ", "   ██╔╝  ", "   ██║   ", "   ╚═╝   "]
eight    = [" █████╗  ", "██╔══██╗ ", "╚█████╔╝ ", "██╔══██╗ ", "╚█████╔╝ ", " ╚════╝  "]
nine     = [" █████╗  ", "██╔══██╗ ", "╚██████║ ", " ╚═══██║ ", " █████╔╝ ", " ╚════╝  "]
textm = {
    ".":dot, "0":zero, "1":one, "2":two, "3":three, 
    "4":four, "5":five, "6":six, "7":seven, "8":eight, 
    "9":nine
    }

class MultilineInt:
    """
    A class to display a number in a multiline format.
    """
    def __init__(self, number:int|float):
        """
        Initializes a MultilineInt object with a given number.

        Args:
            number (int or float): The number to be displayed in a multiline format.

        The object will store the given number as an instance variable, and create a
        list of 6 strings, each representing a line of the display. It will then
        iterate over the given number as a string, and for each character, it will
        append the corresponding line from the textm dictionary to the
        corresponding line in the list.
        """
        self._number = number
        self._lines = ["", "", "", "", "", ""]
        for x in str(self._number):
            for line_index, _ in enumerate(self._lines):
                string = textm[x][line_index]
                self._lines[line_index] += string

    def __str__(self):
        return "\n".join(self._lines)

    def __repr__(self):
        return f"MLNumber({self._number})"


class BigInt:
    """
    A class to display a big integer in a multiline format.
    """
    def __init__(self, value, alignment="center"):
        """
        Initializes a BigInt object with a given value and alignment.

        Args:
            value (int or float): The value of the BigInt object.
            alignment (str): The alignment of the BigInt object in the text. Defaults to "center".

        """
        self.value = MultilineInt(value)
        self.alignment = alignment

    def __rich__(self):
        """Returns a Rich renderable for this BigInt object.

        The returned renderable is a Text object with the value of this BigInt
        object as its text, and the justification set to the alignment specified
        when this BigInt object was created.

        Returns:
            rich.Text: A Rich renderable for this BigInt object.
        """
        return Text(str(self.value), justify=self.alignment)



def screenshot_to_array(screenshot) -> np.ndarray:
    return np.array(Image.frombytes("RGB", screenshot.size, screenshot.rbg))



def get_active_window() -> gw.Window:
    """
    Returns the currently active window, or None if no window is active.

    The function tries to return the currently active window using
    pygetwindow's getActiveWindow method. If that fails, it tries to find
    the most recently used window by searching for windows with titles
    that start with "Administrator: Windows PowerShell", "Windows PowerShell",
    or "Terminal". If none of these windows are found, it returns None.

    Returns:
        pygetwindow.Window or None: The currently active window or None
    """
    try:
        return gw.getActiveWindow()
    except:
        for title in gw.getAllTitles():
            if title == "Administrator: Windows PowerShell" \
            or title.startswith("Windows PowerShell") \
            or title.startswith("Terminal"):
                return gw.getWindowsWithTitle(title)[0]
        return None

def new_avi_writer() -> cv2.VideoWriter:
    """
    Returns a new VideoWriter object to record the current window.

    The function finds the currently active window and creates a new
    VideoWriter object to record it. It automatically finds the next
    available filename in the form "window_recording_<number>.avi".
    The returned VideoWriter object records at a rate of 20 frames per
    second, with the same dimensions as the active window.

    Returns:
        VideoWriter: A VideoWriter object to record the active window.
    """
    window = get_active_window()
    fourcc = cv2.VideoWriter().fourcc(*'XVID')
    c = 0
    name = "window_recording_"
    path = name + str(c) + ".avi"
    while True:
        if os.path.exists(path):
            c += 1
            path = "window_recording_" + str(c) + ".avi"
        else:
            break

    return cv2.VideoWriter(path, fourcc, 12.0, (window.width, window.height))

def get_all_avis() -> list:
    """
    Retrieves and returns a list of all AVI files in the current directory.

    The function scans the current directory for files with the ".avi" extension.
    It extracts numerical digits from each filename to determine its position
    in the returned list. The list is filled with filenames based on these
    extracted numbers, ensuring the list maintains the order based on these
    numbers. Empty sublists are filtered out before returning the final list.

    Returns:
        list: A list of AVI filenames found in the current directory, ordered by
              the numerical digits extracted from their filenames.
    """

    items = [[], [], [], [], [], [], [], [], [], []]
    for f in os.listdir():
        if f.endswith(".avi"):
            num = int("".join([x for x in f if x.isdigit()]))
            items[num] = f
            items.append([])
    return [x for x in items if x]

def read_this_avi(avi):
    """
    Reads the given AVI file.

    Parameters
    ----------
    avi : str
        The path to the AVI file to be read.

    Returns
    -------
    reader : imageio.core.Format.Reader
        An imageio reader object set up to read the given AVI file.
    """
    return imageio.get_reader(avi, format="avi", mode="I")

def cleanup_local_avis():
    """
    Deletes all AVI files in the current directory.

    This function is useful for cleaning up the directory after converting
    all AVIs to a single GIF.

    Returns
    -------
    None
    """
    for f in os.listdir():
        if f.endswith(".avi"):
            os.remove(f)

def build_table(frames:int, window: gw.Win32Window, stime:float) -> Table:
    """
    Builds a Rich Table object with information about the recording process.

    Parameters
    ----------
    frames : int
        The number of frames captured so far.
    window : gw.Win32Window
        The window being recorded.
    stime : float
        The time at which the recording started.

    Returns
    -------
    Table
        A Rich Table object with the recording information.
    """
    t = Table(title="Recording Terminal",
                caption="Press Ctrl+C or q to stop.",
                show_header=False,
                show_footer=False,
                show_lines=False,
                show_edge=False)
    t.add_column("")
    t.add_row("[cyan]Frames   [/cyan]".ljust(35) + str(frames))
    t.add_row("[blue]Time     [/blue]".ljust(35) + str(time.time() - stime))
    t.add_row("[red]Fps       [/red]".ljust(35) + str(frames / (time.time() - stime)))
    t.add_row("[orange]Window [/orange]".ljust(35) + str(window.title))
    return t


def reduce_by_percent(items:list[int]|tuple[int], percent:int=20) -> None:
    """
    Reduces the width and height of the given tuple of integers.

    Parameters
    ----------
    size : Tuple[int, int]
        The tuple of integers to reduce.

    Returns
    -------
    None
    """
    factor = (100 - percent) / 100
    return [int(value * factor) for value in items]

def process_frames(size: Tuple[int, int], fps:int, frameq: Queue):
    newsize = reduce_by_percent(size, 20)
    print(f"Original size: {size}, New size: {newsize}")  # Debug print
    frames = []
    
    try:
        while True:
            if frameq.qsize() == 0:
                time.sleep(0.1)
        
            frame = frameq.get()
        
            if frame == None:
                break

            img = Image.frombytes("RGB", frame.size, frame.rgb)
            img = img.resize(newsize, Image.Resampling.LANCZOS)
            frames.append(img)

    except KeyboardInterrupt:
        print("Stopping...")
        while frameq.qsize() > 0:
            frame = frameq.get()
            if frame == None:
                break
            else:
                img = Image.frombytes("RGB", frame.size, frame.rgb)                
                frames.append(img)
                
    os.makedirs("output", exist_ok=True)

    try:
        # Save using PIL's save method with appropriate parameters
        frames[0].save(
            "output" + os.sep + "capture.gif",
            save_all=True,
            append_images=frames[1:],
            optimize=True,
            duration=int(1000/fps),  # Convert fps to milliseconds between frames
            loop=0  # 0 means loop forever
        )
    except Exception as e:
        print(f"Error saving GIF: {e}")    


def main():
    
    frameq = Queue()
    window: gw.Win32Window = get_active_window()        
    fps = 12
    frame_processor = Process(target=process_frames, args=(window.size, fps, frameq,))
    frames = 0
    frame_interval = 1 / fps
    coutdown_countfrom = time.time() + 5
    if not isinstance(window, gw.Win32Window):
        print("No window found")
        return
    
    monitor = {
        "top": window.top, 
        "left": window.left, 
        "width": window.width,
        "height": window.height
    }

    with Live("Starting...") as status:

        while True:
            if time.time() > coutdown_countfrom:
                break
            countdown = int(coutdown_countfrom - time.time())
            status.update(str(MultilineInt(countdown)))
    status.stop()

    with mss.mss() as sct:

        try:

            frame_processor.start() 
            proc_start_time = time.time()
            while True:
                start_time = time.time()

                frameq.put(sct.grab(monitor))
                frames+=1
    
                #status.update(build_table(frames, window, stime))
                
                remaining_time = frame_interval - (time.time() - start_time)
                
                if remaining_time > 0:
                    time.sleep(remaining_time)
                
        except KeyboardInterrupt:
            print("Stopping...")
            frameq.put(None)
            

    proc_finish_time = time.time()

    with Status("Converting to Gif...", spinner="bouncingBar") as status:
    
        while True:
            time.sleep(0.15)
            if frame_processor.is_alive() == True:
                status.update(f"Converting: {time.time()-proc_finish_time}")
                continue
            else:
                status.update("Converting: Done!")
                frame_processor.join()
                break
        
        status.update("optimizing...")
    
    print("Gif Name:          window_capture.gif")
    print("Total Record Time: " + str(proc_finish_time - proc_start_time))
    print("Total Frames:      " + str(frames))
    print("Fps:               " + str(frames / (proc_finish_time - proc_start_time)))
    print("Window:            " + window.title)


if __name__ == "__main__":
    freeze_support()
    main()
