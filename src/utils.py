""" misc utilities functions"""
import resource
import emoji

def limit_memory(maxsize): 
    """ Prevent computer from crashing"""
    soft, hard = resource.getrlimit(resource.RLIMIT_AS) 
    resource.setrlimit(resource.RLIMIT_AS, (maxsize, maxsize))

def extract_emojis(text,find_tone=False):
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
        next_char = analyze_char(char,chariter,emojis,find_tone)
        if next_char is None:
            return emojis
        char = next_char

def analyze_char(char,chariter,emojis,find_tone=False):
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
        test_char = next(chariter,None)
        while test_char in ["\u200d","\ufe0f"] + skin_tones:
            next_char = next(chariter,None)
            if test_char == "\ufe0f":
                test_char = next_char
            elif test_char == "\u200d":
                if next_char not in (list(emoji.UNICODE_EMOJI.keys()) +["\ufe0f"]):
                    test_char = next_char
                    print("Weird string detected")
                    break
                em = em + test_char
                em = em + next_char
                test_char = next(chariter,None)  
            else:
                if find_tone:
                    em = em + test_char
                test_char = next_char
        emojis.append(em)
        return test_char
    else:
        return next(chariter,None)

def print_mem_usage(df):
    """ print memory footprint of a pandas dataframe"""
    mb_usage = df.memory_usage(deep=True).sum() / 1e6
    print(f"Memory usage:{mb_usage:.2f} MB")

def tononymize(em):
    """
    Return the non-tone (yellow) corresponding emoji
    
    Args:
        em (str): emoji to detone
    """
    return "".join([char for char in em if char not in skin_tones])

def tononymize_dic(tone_dic):
    """
    Remove the skin tone from all the keys of the dic and sum all the values
    of the emoji that share a common untone emoji.
    
    Args:
        tone_dic (dic): value_counts of emojis
    
    Return:
        [dic]: same version with no skin tone<
    """
    dic = copy(tone_dic)
    keys = list(dic.keys())
    for em in keys:
        for char in em:
            if char in skin_tones:
                counts = dic[em]
                untone_em = tononymize(em)
                dic[untone_em] = dic.get(untone_em,0) + counts
                del dic[em]
                break
    assert(len(dic) <= len(tone_dic))
    assert(sum(dic.values()) == sum(tone_dic.values()))
    return dic
