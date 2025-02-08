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
from concurrent import futures
import numpy as np
import cv2
import mss
import imageio
import pygetwindow as gw
from rich.live import Live
from rich.table import (
    Table,
    Text
)


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

    return cv2.VideoWriter(path, fourcc, 20.0, (window.width, window.height))

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

def main():
    """
    Main function for the script. It is responsible for:

    1. Cleaning up all AVI files from the current directory.
    2. Building a live table for displaying recording information.
    3. Obtaining the active window.
    4. Creating an AVI writer and start recording the window.
    5. Converting the recorded AVIs to a single GIF.
    6. Removing all AVIs after conversion.

    The function will break if Ctrl+C is pressed.
    """
    stime = time.time()

    cleanup_local_avis()

    with Live() as live:
        live.console.clear()
        live.update("Starting...")
        window: gw.Win32Window = get_active_window()

        if isinstance(window, gw.Win32Window):

            wleft, wtop, wright, wbottom =\
                window.left, window.top, \
                window.left + window.width, window.top + window.height

            with mss.mss() as sct:
                monitor = {
                    "top": wtop, 
                    "left": wleft, 
                    "width": wright - wleft, 
                    "height": wbottom - wtop
                    }
                out = new_avi_writer()
                frames = 0

                countfrom = time.time() + 3
                while True:
                    if time.time() > countfrom:
                        break
                    countdown = int(countfrom - time.time())
                    live.update(str(MultilineInt(countdown)))

                limit = 200
                while True:
                    try:
                        out.write(
                            cv2.cvtColor(
                                np.array(sct.grab(monitor)),
                                cv2.COLOR_BGRA2BGR
                                )
                            )
                        frames += 1
                        limit -= 1
                        if limit == 0:
                            out.release()
                            out = new_avi_writer()
                            limit = 200
                        live.update(build_table(frames, window, stime))
                    except KeyboardInterrupt:
                        break

                out.release()

                live.update("Converting to Gif...")
                allavis = get_all_avis()
                for x in allavis:
                    if x == []:
                        allavis.remove(x)

                with futures.ThreadPoolExecutor(10) as executor:
                    results = executor.map(read_this_avi, allavis)

                live.console.clear()

                with imageio.get_writer('window_recording.avi', mode='I') as writer:
                    c = 0
                    for index, result in enumerate(results):
                        live.console.clear()
                        live.update("Building Gif...")
                        for x in result:
                            c+=1
                            writer.append_data(x)
                        live.console.clear()
                        live.update(f"Frames: {c}")
                        result.close()
                        os.remove(allavis[index])

                live.console.clear()
                live.update("Done!")


if __name__ == "__main__":
    main()
