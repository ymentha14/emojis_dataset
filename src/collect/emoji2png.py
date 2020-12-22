"""
As the emoji format is not universally accepted across browsers types and versions, the chosen
solution consists in converting the emojis to an image file. As no emojis image dataset existed,
I generated scripts to convert a list of emojis to .png file by sequentially displaying them
and automating screenshots.
"""

from IPython.display import clear_output
import pyscreenshot as ImageGrab
from src.constants import PNG_PATH
import emoji
import pickle as pk
import time
from pathlib import Path

def print_and_capture(x,y,width,height,test=False,missing_emojis=None):
    """
    Allows to recreate the images from the emoji
    """
    bbox = (x,y,x+width,y+height)

    output_folder = PNG_PATH
    if missing_emojis is not None:
        emojis_dic = {key:val for key,val in emoji.EMOJI_UNICODE.items() if key.strip(":") in missing_emojis}
    else:
        emojis_dic = emoji.EMOJI_UNICODE
    if test:
        dic = {}
        for i,(_,em) in enumerate(emojis_dic.items()):
            path = output_folder.joinpath(str(i)).with_suffix(".png")
            print(em)
            time.sleep(0.15)
            im = ImageGrab.grab(bbox=bbox)
            im.save(path)
            clear_output()
            dic[em] = i
        pk.dump(dic,open(output_folder.joinpath("dic.pk"),"wb"))
    else:
        print("😃")