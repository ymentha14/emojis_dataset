"""
As the emoji format is not universally accepted across browsers types and versions, the chosen
solution consists in converting the emojis to an image file. As no emojis image dataset existed,
I generated scripts to convert a list of emojis to .png file by sequentially displaying them
and automating screenshots.

The Global index describes an indexing [0-3859] of all 3860 emojis present in the emoji package.

The Top index describes an indexing [0-1324] of the 1325 emojis that were selected to be present in the
dataset.
"""

from IPython.display import clear_output
import pyscreenshot as ImageGrab
from src.constants import PNG_PATH
import emoji
import pickle as pk
import time
from pathlib import Path


def print_and_capture(
    x, y, width, height, output_dir_png, mapping_path, emojis, test=False
):
    """
    Print and screenshot the emojis for a universal representation: you first need to calibrate
    the x,y,height,width coordinate by trial and error untill the desired format is obtained.
    NB: the x,y coordinate start from top-left corner of the screen

    Args:
        x (int): x coordinate of the capturing are
        y (int): y coordinate of the capturing are
        width (int): width of the capturing are
        height (int): height of the capturing are
        output_dir_png (str): directory where to store the screenshots of the emojis
        mapping_path (str): path to the file where to store the mapping associating each
        emoji to its global index
        emojis (list of str): emojis we wish to convert to an image
        test (bool, optional): if set to True display a dummy emoji
    """
    output_dir_png = Path(output_dir_png)
    not_empty = any(output_dir_png.glob("*.png"))
    if not_empty:
        raise ValueError("Directory not empty: please provide an empty directory.")

    bbox = (x, y, x + width, y + height)

    if test:
        print("😃")
    else:
        dic = {}
        for i, em in enumerate(emojis):
            path = output_dir_png.joinpath(str(i)).with_suffix(".png")
            print(em)
            time.sleep(0.15)
            im = ImageGrab.grab(bbox=bbox)
            im.save(path)
            clear_output()
            dic[em] = i
        pk.dump(dic, open(mapping_path, "wb"))
