"""
Functions to convert emojis to png files
"""

from IPython.display import clear_output
import pyscreenshot as ImageGrab
import emoji
import time
from pathlib import Path

def print_and_capture(bbox,test=False,missing_emojis=None):
    """
    Allows to recreate the images from the emoji
    """
    if missing_emojis is not None:
        emojis_dic = {key:val for key,val in emoji.EMOJI_UNICODE.items() if key.strip(":") in missing_emojis}
    else:
        emojis_dic = emoji.EMOJI_UNICODE
    output_folder = Path("../data/processed/emojis_png/all/")
    if test:
        for i,(label,em) in enumerate(emojis_dic.items()):
            label = label.strip(":").replace(".","")
            path = output_folder.joinpath(label).with_suffix(".png")
            print(em)
            time.sleep(0.15)
            im = ImageGrab.grab(bbox=bbox)
            im.save(path)
            clear_output()
    else:
        print("😃")