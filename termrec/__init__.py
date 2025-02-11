from .countdown import initialize_countdown
from .processor import new_process_frames_thread
from .screenshot import new_capture_window_thread
from .table import build_table
from .screenshot import get_active_window
from .app import get_parser
from multiprocessing import Process, Queue, freeze_support
import time
from rich.live import Live
from rich.status import Status





def record_current_terminal(output_file:str, fps:int=12, reduce_percent:int=20, countdown:int=5):
    window = get_active_window()
    frameq = Queue()
    process_frames_thread = new_process_frames_thread(frameq, window.size, reduce_percent, output_file, fps)
    sshot_thread = new_capture_window_thread(frameq, fps)

    initialize_countdown(countdown)
    sshot_thread.start()
    process_frames_thread.start()
    start_time = time.time()
    
    with Live("Recording...") as status:
        status.console.clear()
        while True:
            try:
                delta = time.time() - start_time
                frames = int(delta * fps)
                status.update(build_table(frames, window, start_time))
            except KeyboardInterrupt:
                sshot_thread.terminate()
                frameq.put(None)
                break
        
    write_start = time.time()
    with Status("Writing Gif...") as status:
        while True:
            if process_frames_thread.is_alive() == False:
                process_frames_thread.join()
                break
            status.update("Writing Gif:  Seconds: " + str(time.time() - write_start))   
            time.sleep(0.1)
        status.console.clear()
    
    print("Gif saved to " + output_file)
    print("Done.")