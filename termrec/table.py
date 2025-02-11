from pygetwindow import Win32Window
from rich.table import Table
import time

def build_table(frames:int, window: Win32Window, stime:float) -> Table:
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
    if frames != 0:
        t.add_row("[red]Fps       [/red]".ljust(35) + str(frames / (time.time() - stime)))
    t.add_row("[orange]Window [/orange]".ljust(35) + str(window.title))
    return t

