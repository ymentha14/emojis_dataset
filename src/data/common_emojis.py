"""
Functions and methods to extract statistics concerning the most used emojis in twitter datasets.
"""

from collections import Counter
import emoji
import seaborn as sns
import pandas as pd
import resource
from tqdm import tqdm
from IPython.core.debugger import set_trace
from tqdm import tqdm
import matplotlib.pyplot as plt
from pathlib import Path
import numpy as np
import bz2
import json
from IPython.core.debugger import set_trace
import warnings
warnings.filterwarnings('ignore')
sns.set()


def read_twitter_data(tweet_path=None,N_LIM=10):
    """
    Gather randomized subset of the data present at tweets_pritzer_sample.

    Args:
        N_LIM (int): number of files we take from each day directory
    
    Returns:
        [pd.df]: dataframe with columns 'id','lang', and 'text'
    """
    if tweet_path is not None:
        print("loading existing file..")
        tweet_df = pd.read_csv(tweet_path,index_col=0,nrows=3000000)
        return tweet_df
    tweet_df = []
    main_path = Path("/dlabdata1/gligoric/spritzer/tweets_pritzer_sample/")
    np.random.seed(13)
    subpaths = np.random.permutation(list(main_path.iterdir()))
    # we only take the twitter_stream
    subpaths = [path for path in subpaths if path.stem.startswith("twitter_stream")]
    tweet_paths = [tweet_path for subpath in subpaths for tweet_path in np.random.permutation(list(subpath.rglob("*.json.bz2")))[:N_LIM]]
    print(f"Analyzing {len(tweet_paths)} files")
    for tweet_path in tqdm(tweet_paths):
        new_tweets = []
        with bz2.open(tweet_path, "rt") as bzinput:
            for line in bzinput: 
                try:
                    tweet = json.loads(line)
                except json.JSONDecodeError:
                    continue
                if len(tweet.keys()) < 5 :
                    continue
                tweet = {key:tweet[key] for key in ['id','lang','text']}
                new_tweets.append(tweet)
        tweet_df += new_tweets
    tweet_df = pd.DataFrame(tweet_df)
    tweet_df.to_csv("/home/ymentha/tweet.csv")
    return tweet_df

def update_emoji_count(dic,text):
    """
    Update the counts of each emoji wrt to text
    
    Args:
        dic(dict): mapping emojis--> count
        text (str): text to use to update dic
    """
    for char in text:
        if char in emoji.UNICODE_EMOJI:
            dic[char] = dic.get(char,0) + 1

def get_em_df(path,tweet_df=None):
    """
    extract the em_df from tweet_df. em_df = mapping from emojis to their counts
    in tweet_df

    Args:
        path (str): path to em_df
        tweet_df (pd.df): dataframe as returned by read_twitter_data
    
    Returns:
        [pd.df]: em_df
    """
    if Path(path).exists() and tweet_df is None:
        return pd.read_csv(path,index_col=0,names=['counts'],header=0)['counts']
    emojis_count = {}
    for text in tqdm(tweet_df['text']):
        update_emoji_count(emojis_count,text)
    em_df = pd.Series(emojis_count).sort_values(ascending=False)
    em_df = em_df.reset_index().dropna().set_index('index')
    em_df.to_csv(path)
    return em_df

def print_tot_emoji_ratio(em_df):
    """
    Print the ratio of total emojis represented in em_df 
    (the emoji lib is used as a reference)
    """
    absent_emojis = set(emoji.UNICODE_EMOJI) - set(em_df.index)
    print(f"Grasped {len(em_df) / len(emoji.UNICODE_EMOJI)* 100:.2f}% of the total emojis")

def display_cover_app_ratio(em_df,ax=None):
    """
    Display the covered emojis apparition ratio wrt to the number of emojis taken into account
    """
    if ax is None:
        fig,ax = plt.subplots(1)
    df = em_df.to_frame(name='counts')
    df['tot_ratio'] = df['counts'].cumsum() / df['counts'].sum()
    df['tot_ratio'].reset_index().head(1000).plot(ax=ax)
    ax.get_legend().remove()
    ax.set_xlabel("# of emojis [sorted wrt counts]")
    ax.set_ylabel("Ratio of Covered emojis apparition")
    ax.set_title("Covered emojis apparition ratio")

def display_log_hist(em_df,ax=None):
    """
    Display the log histogram of counts wrt to emojisi
    """
    if ax is None:
        fig,ax = plt.subplots(1)
    em_df.hist(ax = ax,bins=50)
    ax.set_yscale('log')
    q25,q50,q75,q99 = em_df.quantile(0.25),em_df.quantile(0.75),em_df.quantile(0.5),em_df.quantile(0.99)
    ax.axvline(q25,color='blue',label = 'q25')
    ax.axvline(q75,color='green',label = 'q75')
    ax.axvline(q99,color='red',label = 'q99')
    ax.legend()
    ax.set_title("Log histogram of counts for emojis")
    print(f"Q25:{q25}")
    print(f"Q50:{q50}")
    print(f"Q75:{q75}")
    print(f"Q99:{q99}")