""" misc utilities functions"""
import resource
import emoji
from src.constants import (
    skin_tones,
    em_letters,
    EMOJIS,
    man_woman,
    FE0F_DICT,
    sex_symbols,
)

from copy import copy
from pdb import set_trace
import pandas as pd
from pathlib import Path


def limit_memory(maxsize):
    """ Prevent computer from crashing"""
    soft, hard = resource.getrlimit(resource.RLIMIT_AS)
    resource.setrlimit(resource.RLIMIT_AS, (maxsize, maxsize))

def em_2_unicode(em):
    """
    Takes into account the NotoEmoji package for lualatex 
    """
    if len(em) > 1:
        return "?"
    hex_rep = hex(ord(em)).split("x")[1].upper()
    return '{\\NotoEmoji \symbol{"%s} }' % (hex_rep)

def write_to_latex(path,df,index=False):
    df = df.copy()
    if 'emoji' in df.columns:
        df['emoji'] = df['emoji'].apply(em_2_unicode)
    with open(path,"w") as f:
        f.write(df.to_latex(index=index,label="fig::" + path.stem,escape=False))

def extract_emojis(text, find_tone=False):
    """
    Extract all emojis present in the text.

    Args:
        text (str): text to search emojis in
        find_tone (Bool): whether to care about skin tone or not

    Returns:
        [list of str]: list of found emojis in the same order
    """
    emojis = []
    chariter = iter(text)
    char = next(chariter)
    while True:
        next_char = analyze_char(char, chariter, emojis, find_tone)
        if next_char is None:
            return emojis
        char = next_char


def analyze_char(char, chariter, emojis, find_tone=False):
    """
    Analyze the current char of the text, chaining as long as necessary
    if present on a complex emoji.

    Args:
        char (str): character of length one
        chariter (iter): iterator over the text
        emojis (list): list of emojis to append to
        find_tone (Bool): whether to care about skin tone or not

    Return:
        [str]: next character to analyze
    """
    if char in emoji.EMOJI_UNICODE.values():
        em = char
        test_char = next(chariter, None)
        if em in em_letters:
            # flag case
            if test_char in em_letters:
                em = em + test_char
                test_char = next(chariter, None)
        else:

            while test_char in ["\u200d", "\ufe0f"] + skin_tones:
                next_char = next(chariter, None)
                # dummy character
                if test_char == "\ufe0f":
                    test_char = next_char

                # liaison character
                elif test_char == "\u200d":
                    if next_char not in (list(emoji.UNICODE_EMOJI.keys()) + ["\ufe0f"]):
                        test_char = next_char
                        print("Weird string detected")
                        break
                    em = em + test_char
                    em = em + next_char
                    test_char = next(chariter, None)
                else:
                    if find_tone:
                        em = em + test_char
                    test_char = next_char
        emojis.append(em)
        return test_char
    else:
        return next(chariter, None)


def print_mem_usage(df):
    """ print memory footprint of a pandas dataframe"""
    mb_usage = df.memory_usage(deep=True).sum() / 1e6
    print(f"Memory usage:{mb_usage:.2f} MB")


def detect_hold_hands(em):
    has_2_manwoman = sum([char in man_woman for char in em]) == 2
    return "🤝" in em and has_2_manwoman


def tononymize(
    em,
):
    """
    Return the non-tone (yellow) corresponding emoji

    Args:
        em (str): emoji to detone
    """
    assert em in EMOJIS
    if detect_hold_hands(em):
        return "🧑‍🤝‍🧑"
    em_no_tone = "".join([char for char in em if char not in skin_tones])
    if em_no_tone == "":
        return em_no_tone
    em_no_tone = "".join([char for char in em_no_tone if char != "\ufe0f"])
    assert em_no_tone in EMOJIS
    return em_no_tone


def tononymize_list(emojis):
    emojis = set([tononymize(em) for em in emojis])
    # remove the pure skin tones
    emojis = emojis - {""}
    return emojis


def genderonymize(em):
    """
    Return the neutral version of an emoji

    Args:
        em (str): emoji to degender
    """
    assert em in EMOJIS
    if em in sex_symbols:
        return ""
    elif len(em) == 1:
        return em
    else:
        neutral_em = []
        for char, next_char in zip(em, em[1:]):
            if char in sex_symbols:
                continue
            elif next_char in sex_symbols and char == "\u200d":
                continue
            elif char != "\ufe0f":
                neutral_em.append(char)
        if em[-1] not in sex_symbols + ["\ufe0f"]:
            neutral_em.append(em[-1])
        neutral_em = "".join(neutral_em)

        assert neutral_em in EMOJIS
        return neutral_em


def genderonymize_list(emlist):
    emlist = set([genderonymize(em) for em in emlist])
    emlist = emlist - {""}
    emlist = list(emlist)
    assert all([em in EMOJIS for em in emlist])
    return emlist


def group_tone_dic(tone_dic):
    """
    Remove the skin tone from all the keys of the dic and sum all the values
    of the emoji that share a common untone emoji.

    Args:
        tone_dic (dic): value_counts of emojis

    Return:
        [dic]: same version with no skin tone<
    """
    sum_tone = sum([tone_dic.get(tone, 0) for tone in skin_tones])
    dic = copy(tone_dic)
    keys = list(dic.keys())
    for em in keys:
        for char in em:
            if char in skin_tones:
                counts = dic[em]
                untone_em = tononymize(em)
                dic[untone_em] = dic.get(untone_em, 0) + counts
                del dic[em]
                break
    # pure skin tone emojis
    del dic[""]
    assert len(dic) <= len(tone_dic)
    assert sum(dic.values()) == sum(tone_dic.values()) - sum_tone
    return dic


def group_fe0f_dic(emojis_dic):
    dic = copy(emojis_dic)
    keys = list(dic.keys())
    for em in keys:
        fe0f_em = FE0F_DICT[em]
        if fe0f_em != em:
            counts = emojis_dic[em]
            dic[fe0f_em] = dic.get(fe0f_em, 0) + counts
            del dic[em]
    assert len(dic) <= len(emojis_dic)
    assert sum(dic.values()) == sum(emojis_dic.values())
    return dic


def keep_fe0f_emojis(emojis):
    assert all([em in EMOJIS for em in emojis])
    emojis_ret = set([FE0F_DICT[em] for em in emojis])
    return emojis_ret


def print_em_set(emset):
    """
    print the emojis in a packed manner and sequentially
    """
    for em in emset:
        print(em, end="")


def generate_password(i):
    a = i * 324 + 932
    return str(a)[:3]
