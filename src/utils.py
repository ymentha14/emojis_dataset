""" misc utilities functions"""
import resource
import emoji

def limit_memory(maxsize): 
    """ Prevent computer from crashing"""
    soft, hard = resource.getrlimit(resource.RLIMIT_AS) 
    resource.setrlimit(resource.RLIMIT_AS, (maxsize, maxsize))

def extract_emojis(text):
    """ return a list of the emojis from text in their apparition order"""
    return ''.join(c for c in text if c in emoji.UNICODE_EMOJI)

def print_mem_usage(df):
    """ print memory footprint of a pandas dataframe"""
    mb_usage = df.memory_usage(deep=True).sum() / 1e6
    print(f"Memory usage:{mb_usage:.2f} MB")
