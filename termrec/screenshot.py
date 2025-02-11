import pygetwindow as gw
import multiprocessing as mp
import time
import mss


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


def new_capture_window_thread(frameq: mp.Queue, fps:int=12) -> mp.Process:
    return mp.Process(target=capture_window_at_interval, args=(frameq, fps,))

def capture_window_at_interval(frameq: mp.Queue, fps:int=12):
    window = get_active_window()
    frame_interval = 1 / fps
    frames = 0
    monitor = {
        "top": window.top,
        "left": window.left,
        "width": window.width,
        "height": window.height
    }

    with mss.mss() as sct:

        try:
            while True:
                s = time.time()
                frame = sct.grab(monitor)
                frameq.put(frame)
                frames += 1
                d = time.time() - s
                if d < frame_interval:
                    time.sleep(frame_interval - d)

        except KeyboardInterrupt:
            frameq.put(None)
