def extract_emojis(s):
    """return a list of unique emojis present in a text"""
    return list(set([c for c in s if c in emoji.UNICODE_EMOJI]))
