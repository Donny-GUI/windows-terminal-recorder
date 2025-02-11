import multiprocessing as mp
import time
from PIL import Image
from termrec.util import reduce_by_percent
from typing import Tuple
import os


def process_frames(size: Tuple[int, int], outputfile:str, fps:int, reduction_percent:int=0, frameq: mp.Queue=mp.Queue()):
    newsize = reduce_by_percent(size, reduction_percent)
    frames = []

    try:
        while True:

            if frameq.qsize() == 0:
                time.sleep(0.1)
                continue

            frame = frameq.get()

            if frame == None:
                break

            img = Image.frombytes("RGB", frame.size, frame.rgb)
            if img.size != newsize:
                img = img.resize(newsize, Image.Resampling.LANCZOS)
            frames.append(img)

    except KeyboardInterrupt:
        while frameq.qsize() > 0:
            frame = frameq.get()
            if frame == None:
                break
            else:
                img = Image.frombytes("RGB", frame.size, frame.rgb)
                img = img.resize(newsize, Image.Resampling.LANCZOS)
                frames.append(img)

    if outputfile.endswith(".gif") == False:
        outputfile += ".gif"
    
    try:
        # Save using PIL's save method with appropriate parameters
        frames[0].save(
            outputfile,
            save_all=True,
            append_images=frames[1:],
            optimize=True,
            duration=int(1000/fps),  # Convert fps to milliseconds between frames
            loop=0  # 0 means loop forever
        )
    except Exception as e:
        print(f"Error saving GIF: {e}")


def new_process_frames_thread(frameq: mp.Queue, size: Tuple[int, int], reduction_percent:int=0, outputfile:str="output", fps:int=12) -> mp.Process:
    return mp.Process(target=process_frames, args=(size, outputfile, fps, reduction_percent, frameq,))
