"""
Functions and methods to extract statistics concerning the most used emojis in twitter datasets.
"""

from collections import Counter
import emoji
import seaborn as sns
import pandas as pd
import sys
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
import pickle as pk
from numpy.random import permutation
import pdb
import traceback
import sys
from src.constants import (
    flags,
    em_letters,
    em_numbers,
    em_hours,
    TWEET_EM_COUNT_PATH,
    TWEET_PATHS_PATH,
    EXPORT_DIR,
    TWEET_PATH,
    TWEET_SAMPLES_DIR,
    COLOR1,
    COLOR2,
    TITLE_SIZE,
    LABEL_SIZE,
)

from src.utils import tononymize_list, genderonymize_list, keep_fe0f_emojis

warnings.filterwarnings("ignore")
sns.set()


def filter_access_paths(tweet_paths):
    """
    filter the paths we have rights for
    """
    access_paths = []
    print(f"Length before filtering{len(tweet_paths)}")
    for tweet_path in tqdm(tweet_paths):
        try:
            bz2.open(tweet_path, "rt")
            access_paths.append(tweet_path)
        except PermissionError as e:
            continue
    print(f"Length after filtering: {len(access_paths)}")
    return access_paths


def load_or_compute_tweetpaths(tweetpaths_path):
    """
    Return a list of the paths we search information in
    """
    if Path(tweetpaths_path).exists():
        print("Loading precomputed paths structure")
        tweet_paths = pk.load(open(tweetpaths_path, "rb"))
    else:
        print("Computing paths structure")
        main_path = TWEET_SAMPLES_DIR
        if not main_path.exists():
            raise ValueError(
                "You need to be on the DLab machine to run the Tweeter function"
            )

        subpaths = np.random.permutation(list(main_path.iterdir()))
        # we are only interested in the twitter_stream directories
        subpaths = [
            path for path in subpaths if path.stem.startswith("twitter_stream")]
        tweet_paths = [
            tweet_path
            for subpath in subpaths
            for tweet_path in list(subpath.rglob("*.json.bz2"))
        ]
        tweet_paths = filter_access_paths(tweet_paths)
        pk.dump(tweet_paths, open(tweetpaths_path, "wb"))
    return tweet_paths


def compute_twitter_data(save_path, N_LIM=30000, seed=15):
    """
    Gather randomized subset of the data present at tweets_pritzer_sample.

    Args:
        save_path (str): path to save the generated file to
        N_LIM (int): number of files we take from each day directory

    Returns:
        [pd.df]: dataframe with columns 'id','lang', and 'text'
    """
    N_SAVE = 100
    assert N_LIM > N_SAVE
    save_path = Path(save_path)
    np.random.seed(seed)

    tweet_paths = load_or_compute_tweetpaths(TWEET_PATHS_PATH)

    tweet_paths = np.random.permutation(tweet_paths)[:N_LIM]

    tweet_df = []
    print(f"Analyzing {N_LIM} files")
    first_pass = True
    tweet_paths = [
        Path(
            "/dlabdata1/gligoric/spritzer/tweets_pritzer_sample/twitter_stream_2019_03_13/13/09/13.json.bz2"
        )
    ] + tweet_paths.tolist()
    for i, tweet_path in enumerate(tqdm(tweet_paths)):

        # tweeter file reading
        new_tweets = []
        try:
            with bz2.open(tweet_path, "rt") as bzinput:
                for line in bzinput:
                    try:
                        tweet = json.loads(line)
                    except json.JSONDecodeError:
                        continue
                    if len(tweet.keys()) < 5:
                        continue
                    tweet = {key: tweet[key] for key in ["id", "lang", "text"]}
                    # we only care for english-labelled data
                    if tweet["lang"] != "en":
                        continue
                    new_tweets.append(tweet)
            tweet_df += new_tweets
        except KeyboardInterrupt:
            sys.exit()
            pass
        except Exception as e:
            print("Exception!", type(e), e)
            continue

        # RAM saving on the shared machine
        if i % N_SAVE == 0 and i != 0:
            if first_pass:
                mode = "w"
                header = True
                first_pass = False
            else:
                mode = "a"
                header = False
            tweet_df = pd.DataFrame(tweet_df)
            tweet_df.to_csv(save_path, mode=mode, header=header)
            tweet_df = []

    # type conversion and saving
    tweet_df = pd.DataFrame(tweet_df)
    tweet_df.to_csv(save_path, mode="a", header=False)
    print("Tweet information generation terminated successfully.")


def update_emoji_count(dic, text):
    """
    Update the counts of each emoji wrt to text

    Args:
        dic(dict): mapping emojis--> count
        text (str): text to use to update dic
    """
    for em in extract_emojis(text, True):
        if em not in emoji.UNICODE_EMOJI:
            print("EMOJI NOT PRESENT")
            continue
        dic[em] = dic.get(em, 0) + 1


def compute_emdf(path, tweet_df):
    """
    compute the em_df from tweet_df. em_df = mapping from emojis to their counts
    in tweet_df

    Args:
        path (str): path to em_df
        tweet_df (pd.df): dataframe as returned by read_twitter_data

    Returns:
        [pd.df]: em_df
    """
    emojis_count = {}
    for text in tqdm(["text"]):
        update_emoji_count(emojis_count, text)
    em_df = pd.Series(emojis_count).sort_values(ascending=False)
    em_df = em_df.reset_index().dropna().set_index("index")
    em_df.to_csv(path)
    return em_df


def load_or_compute_em_df(em_path, tweet_path=None):
    """
    load or compute the em_df depending if the provided path exists or not

    Args:
        path (str): path to em_df
        tweet_df (pd.df): dataframe as returned by read_twitter_data

    Returns:
        [pd.df]: em_df
    """
    if Path(em_path).exists():
        return pd.read_csv(em_path, index_col=0, names=["counts"], header=0)["counts"]

    emojis_count = {}
    reader = pd.read_csv(tweet_path, chunksize=10000)
    for df in reader:
        for text in tqdm(tweet_df["text"]):
            update_emoji_count(emojis_count, text)
    em_df = pd.Series(emojis_count).sort_values(ascending=False)
    em_df = em_df.reset_index().dropna().set_index("index")
    em_df.to_csv(em_path)
    return em_df


def get_tot_emoji_ratio(em_set):
    """
    Print the ratio of total emojis represented in em_df
    (the emoji lib is used as a reference)
    """
    absent_emojis = set(emoji.UNICODE_EMOJI) - set(em_set)
    return len(em_set) / len(emoji.UNICODE_EMOJI)


def plot_top_10(em_df, ax=None):
    if ax is None:
        fig, ax = plt.subplots(1)
    tot_count = em_df.sum()
    top10 = em_df.head(10) / tot_count

    for em in top10.index:
        print(em, end="")
        top10.plot.bar(ax=ax, color=COLOR1)
    ax.set_xlabel("Top 10 most used emojis", fontsize=LABEL_SIZE)
    ax.set_ylabel("Proportion of total use", fontsize=LABEL_SIZE)
    ax.set_title(
        "Proportion of total use of top 10 most used emojis", fontsize=TITLE_SIZE
    )


def display_cover_app_ratio(em_df, ax=None):
    """
    Display the covered emojis apparition ratio wrt to the number of emojis taken into account
    """
    if ax is None:
        fig, ax = plt.subplots(1)
    df = em_df.to_frame(name="counts")
    df["tot_ratio"] = df["counts"].cumsum() / df["counts"].sum()
    df["tot_ratio"].reset_index().head(1000).plot(ax=ax, color=COLOR1)
    ax.get_legend().remove()
    ax.set_xlabel("nmb of emojis [sorted wrt counts]", fontsize=LABEL_SIZE)
    ax.set_ylabel("Ratio of Covered emojis apparition", fontsize=LABEL_SIZE)
    ax.set_title("Covered emojis apparition ratio", fontsize=TITLE_SIZE)


def display_log_hist(em_df, ax=None):
    """
    Display the log histogram of counts wrt to emojisi
    """
    if ax is None:
        fig, ax = plt.subplots(1)
    em_df.hist(ax=ax, bins=50, color=COLOR1)
    ax.set_yscale("log")
    q25, q50, q75, q99 = (
        em_df.quantile(0.25),
        em_df.quantile(0.75),
        em_df.quantile(0.5),
        em_df.quantile(0.99),
    )
    ax.axvline(q25, color="blue", label="q25")
    ax.axvline(q75, color="green", label="q75")
    ax.axvline(q99, color="red", label="q99")
    ax.legend()
    ax.set_title("Log histogram of counts for emojis", fontsize=TITLE_SIZE)
    print(f"Q25:{q25}")
    print(f"Q50:{q50}")
    print(f"Q75:{q75}")
    print(f"Q99:{q99}")


def estimate_covered_ratio(em_df, emojis):
    """
    Estimates the ratios of uses covered by the emojis set wrt to em_df value_counts

    Args:
        em_df (pd.Series): value counts of emojis on a tweeter dataset
        emojis (list of str): list of selected emojis
    """

    tweet_ems = set(em_df.index)
    selected_em = set(emojis)
    tot_em = set()
    for tem in tweet_ems:
        if tem in selected_em:
            tot_em.add(tem)
        if any([(tem in em or em in tem) for em in selected_em]):
            tot_em.add(tem)

    covered_ratio = em_df[tot_em].sum() / em_df.sum()
    print(f"Covered tweeter data ratio: {covered_ratio * 100:.2f} %")
    print


def main():
    # Export path creation
    selection_export_dir = EXPORT_DIR.joinpath("report_files")
    selection_export_dir.mkdir(exist_ok=True, parents=True)

    # Loading of the value counts
    em_df = load_or_compute_em_df(TWEET_EM_COUNT_PATH)
    ratio = get_tot_emoji_ratio(em_df.index)
    print(f"Approx {ratio* 100:.2f}% of all emojis covered by the tweeter data")

    # Top 10 proportion
    fig, ax = plt.subplots(1, figsize=(10, 5))
    plot_top_10(em_df, ax=ax)
    plt.savefig(selection_export_dir.joinpath("top10.jpeg"))

    # Covered emojis ratio
    fig, ax = plt.subplots(1, figsize=(10, 5))
    display_cover_app_ratio(em_df, ax=ax)
    plt.savefig(selection_export_dir.joinpath("covered_emojis.jpeg"))

    # Emojis selection
    emojis = set(emoji.UNICODE_EMOJI.keys())
    print(f"Original length:{len(emojis)}")

    emojis = [
        em for em in emojis if em not in (flags + em_letters + em_numbers + em_hours)
    ]
    print(f"Removing flags and letters and numbers:{len(emojis)}")

    emojis = tononymize_list(emojis)
    print(f"Removing tones:{len(emojis)}")

    emojis = genderonymize_list(emojis)
    print(f"Removing gender:{len(emojis)}")

    emojis = sorted(keep_fe0f_emojis(emojis))
    print(f"Removing fe0f equivalent:{len(emojis)}")
    print("=" * 24 + "\n")
    print(f"Total number of emojis {len(emojis)}\n")
    estimate_covered_ratio(em_df, emojis)

    ratio = get_tot_emoji_ratio(emojis)
    print(f"Approx {ratio*100:.2f}% of all emojis covered by the selection")


if __name__ == "__main__":
    try:
        # compute_twitter_data(TWEET_PATH)
        main()
    except:
        extype, value, tb = sys.exc_info()
        traceback.print_exc()
        pdb.post_mortem(tb)
