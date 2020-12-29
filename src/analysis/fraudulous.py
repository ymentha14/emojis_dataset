"""
Fraudulous users detection

As many ways exist for a user input to be invalid (garbage repeated input, random words answering etc)
One need to either
    (1): perform a workers selection on-the-fly (possible with mt2gf)
    (2): accept all data in a first time and filter it afterwards
The second option was chosen for the emojis dataset: this file contains the functions to filter out such
fraudulous inputs
"""


import pickle as pk
from src.constants import (
    emotions_faces,
    REF_PATH,
    MAPPING_PATH,
    E2V_PATH,
    W2V_PATH,
    DATA_PATH,
)
import sys

sys.path.append("../../emoji2vec_working/")
import seaborn as sns
import numpy as np
from src.constants import COLOR_FRAUD, COLOR_TRUE, EMOJIS
import Levenshtein
from pdb import set_trace
from src.utils import extract_emojis
from IPython.display import display

###################### SINGLE WORD ######################


def detect_repeat_frauders(form_df, min_voc_size=0.8):
    """
    Detect the fraudulous workers i.e. the one who repeated the same word too many times
    
    Args:
        form_df (pd.Dataframe): df obtained from a formular
        min_voc_size (float): if the vocabulary size of the worker goes below this limit,
        its answer is considered as fraudulent
    
    Returns:
        [set of str]: set of fraudulent worker ids
    """
    form_df = form_df.copy()
    columns = [col for col in form_df.columns if col in EMOJIS]
    form_df["vocsize"] = form_df[columns].apply(lambda x: len(set(x)), axis=1)
    fraud_workers = form_df[form_df["vocsize"] < min_voc_size * len(columns)][
        "WorkerID"
    ].values.tolist()
    return set(fraud_workers)


def filter_repeat_frauders(form_df, min_voc_size=0.8, verbose=False):
    frauders = detect_repeat_frauders(form_df, min_voc_size=min_voc_size)
    if len(frauders) > 0 and verbose:
        display(form_df[form_df["WorkerID"].isin(frauders)])
    return form_df[~form_df["WorkerID"].isin(frauders)]


def detect_honey_frauders(form_df, honeypots, dist_lshtein=2):
    """
    Returns the worker_ids of the workers who did not manage to find the honeypots

    Args:
        form_df (pd.df): as saved by download_multi_emoji_csv
        dist_lshteing (int): distance tolerated to accept a honeypot
    """
    if not form_df["WorkerID"].is_unique:
        form_df = form_df.groupby("WorkerID").first().reset_index()
    form_df = form_df.set_index("WorkerID").copy()
    honey_columns = [em for em in form_df.columns if em in honeypots.keys()]
    em_cols = [col for col in form_df.columns if col in EMOJIS]
    n = len(em_cols)
    honey_col_idx = n // 2 - (n + 1) % 2
    em = em_cols[honey_col_idx]
    corr_words = honeypots[em]
    em_serie = form_df[em].apply(
        lambda word: min(
            [Levenshtein.distance(word, corr_word) for corr_word in corr_words]
        )
        > dist_lshtein
    )
    frauder_list = em_serie[em_serie].index.tolist()
    return set(frauder_list)


def filter_out(forms_df, detect_func, *args, verbose=False, display_=False, **kwargs):
    n_frauders = 0
    clean_dfs = []
    for form_df in forms_df:
        frauders = detect_func(form_df, *args, **kwargs)
        if len(frauders) > 0:
            n_frauders += len(frauders)
            if display_:
                display(form_df[form_df["WorkerID"].isin(frauders)])
        form_df = form_df[~form_df["WorkerID"].isin(frauders)]
        clean_dfs.append(form_df)
    if verbose:
        print(f"Discarded {n_frauders} rows")
    return n_frauders, clean_dfs


def get_wrong_honey_entries(form_df, honeypots, dist_lshtein=2):
    """
    Returns the row of form_df which did not pass the honeypots test

    Args:
        form_df (pd.df): dataframe from a gform

    Return:
        [pd.df]: same df with honey frauders entries exclusively
    """
    form_df = form_df.set_index("WorkerID").copy()
    honey_columns = [em for em in form_df.columns if em in honeypots.keys()]
    form_df = form_df[honey_columns]
    assert form_df.shape[1] > 0
    for em in honey_columns:
        corr_words = honeypots[em]
        form_df[em] = form_df[em].apply(
            lambda word: min(
                [Levenshtein.distance(word, corr_word) for corr_word in corr_words]
            )
            > dist_lshtein
        )
    return form_df


#########################################################


def plot_double_hist(user_serie, fraud):
    user_serie = user_serie.astype(int)
    user_serie_true = user_serie[~user_serie.index.isin(fraud)]
    user_serie_fraud = user_serie[user_serie.index.isin(fraud)]
    fig, ax = plt.subplots(1)
    ax.set_title("Rates of constant-answering users")
    user_serie = user_serie.value_counts()
    # user_serie_true.plot(kind='bar',color=COLOR_TRUE,label=,rot=0,ax=ax,alpha=0.5)
    # user_serie_fraud.plot(kind='bar',color=COLOR_FRAUD,label="fraud",rot=0,ax=ax,alpha=0.5)
    ax.hist(
        [user_serie_true, user_serie_fraud],
        color=[COLOR_TRUE, COLOR_FRAUD],
        label=["non-fraud", "fraud"],
    )
    ax.set_xlabel("Fraudulent")
    ax.set_ylabel("Users count")
    ax.legend()


# CONSTANTS
def get_users_cstt(form_df):
    if type(form_df) is list:
        return pd.concat([get_users_cstt(df) for df in form_df])
    formset_df = form_df.applymap(lambda x: frozenset(x.split(",")))
    # detect users giving constant answers
    cstt_mask = (formset_df.applymap(len) == 1).any(axis=1)
    return cstt_mask


def dtct_cstt_answer(form_df):
    """ detect users giving at least one cstt answer (3 times the same word)"""
    cstt_mask = get_users_cstt(form_df)
    cstt_users = cstt_mask.index[cstt_mask].tolist()
    return cstt_users


# DUPLICATES
def get_users_duplicate(form_df, ratio=0.9):
    if type(form_df) is list:
        return pd.concat([get_users_duplicate(df) for df in form_df])
    n_cols = form_df.shape[1]
    # transform the strings in frozen sets
    form_df = form_df.applymap(lambda x: frozenset(x.split(",")))
    duplicate_mask = form_df.apply(lambda x: len(set(x)) < int(n_cols * ratio), axis=1)
    return duplicate_mask


def dtct_duplicate_answer(form_df, ratio=0.95):
    """detect users giving many times the same answer (up to ratio * the number of answers)"""
    duplicate_mask = get_users_duplicate(form_df, ratio)
    duplicate_users = set(duplicate_mask.index[duplicate_mask].tolist())
    return duplicate_users


# VOCABULARY
def compute_voc_size(form_df):
    """
    Compute the vocabulary size for each user

    Args:
        form_df(pd.DataFrame): formular df

    Return:
        [pd.Series]: series associating the voc size to each user
    """
    if type(form_df) is list:
        return pd.concat([compute_voc_size(df) for df in form_df])
    return form_df.apply(lambda x: len(set("".join(x).split(","))), axis=1)


def plot_voc(tot_voc, fraud):
    """
    Plot overlapping histograms of vocabulary size for fraudulent
    and non fraudulent users

    Args:
        tot_voc (pd.Series): serie associating a voc size to each user
        fraud (set): set of fraudulent users
    """
    fig, ax = plt.subplots(1)
    ax.set_title("Vocabulary size for non/fraudulent users")
    bins = 10
    tot_voc_true = tot_voc[~tot_voc.index.isin(fraud)]
    tot_voc_fraud = tot_voc[tot_voc.index.isin(fraud)]
    ax.hist([tot_voc_true, tot_voc_fraud], color=[COLOR_TRUE, COLOR_FRAUD], bins=bins)
    ax.set_xlabel("Voc size")
    ax.set_ylabel("Users count")
    ax.legend()


def dtct_poor_voc(form_df, ratio=0.55):
    voc = compute_voc_size(form_df)
    N = form_df.shape[1]
    N_lim = int(ratio * N * 3)
    poor_users = voc[voc <= N_lim].index.tolist()
    return poor_users


# SEMANTIC
def get_vec_error(form_df, w2v, e2v, ref="mean", loss="l1"):
    """
    return the mean MSE over each emoji for each user
    """
    cols = [col for col in form_df.columns if col in e2v.vocab]
    form_df = form_df[cols]
    vec_error = form_df.applymap(
        lambda x: np.mean(
            [w2v.get_vector(word) for word in x.split(",") if word in w2v.vocab], axis=0
        )
    )
    if ref == "mean":
        # using average of batch as reference
        mean_vecs = np.mean(vec_error.values, axis=0).tolist()
    else:
        assert ref == "em"
        # using emojis vec as reference
        mean_vecs = [e2v.get_vector(em) for em in form_df.columns]
    # normalize
    if loss == "l2":
        vec_error = (vec_error - mean_vecs).applymap(lambda x: x ** 2).applymap(sum)
    else:
        assert loss == "l1"
        vec_error = abs(vec_error - mean_vecs).applymap(sum)
    vec_error = vec_error.sum(axis=1).sort_values()
    return vec_error


def dtct_vec_error(form_df):
    vec_error = get_vec_error(form1_df)
    return vec_error.head(3).index.tolist()


def plot_vec_error(vec_error, fraud, ax=None):
    """
    Plot the error for each user as a barplot

    Args:
        vec_error(pd.Series): vector associating the L1orL2 error to each user (index)
        fraud (set): set of fraudulous users
    """
    if ax is None:
        fig, ax = plt.subplots(1)
    vec_error = vec_error.to_frame("error")
    vec_error["color"] = [
        COLOR_FRAUD if ind in fraud else COLOR_TRUE for ind in vec_error.index
    ]
    vec_error["error"].plot.bar(color=vec_error.color, ax=ax)
    ax.set_title("mean L2orL1 error between user and emoji representations")
    ax.set_xlabel("user id")
    ax.set_ylabel("L2orL1")


# FRAUDULOUS DETECTION
def gather_users(*args):
    """ gather the users of every formdf passed in parameter into a single set"""
    return set.union(*[set(form_df.index.tolist()) for form_df in args])


def find_fraudulous(form_df, filter_funcs):
    """
    Find the fraudulous users in form_df using each of the filter_functions

    Args:
        form_df (pd.Df): formular to filter
        filter_funcs(func): function returning a list of fraudulous user from a df

    Return:
        [list of str]: list of fraudulent users
    """

    fraudulous_users = {}
    for filter_func in filter_funcs:
        func_name = str(filter_func).split()[1]
        new_fraud_users = filter_func(form_df)
        fraudulous_users[func_name] = new_fraud_users
    return fraudulous_users


def fraud_metrics(users, fraud, fraud_hat):
    """
    Plot the fraudulous analysis metrics
    """
    TP = len(fraud.intersection(fraud_hat))
    FP = len(fraud_hat - fraud)
    FN = len(fraud - fraud_hat)
    TN = len((users - fraud.union(fraud_hat)))

    accuracy = (TN + TP) / (TP + TN + FP + FN)
    precision = TP / (TP + FP)
    recall = TP / (TP + FN)
    confusion_matrix = np.array([[TP, FP], [FN, TN]])
    print(f"Accuracy:{accuracy}\nPrecision:{precision}\nRecall:{recall}")
    fig, ax = plt.subplots(1)
    sns.heatmap(
        confusion_matrix,
        annot=True,
        ax=ax,
        xticklabels=["P", "N"],
        yticklabels=["P", "N"],
    )
    ax.set_xlabel("True")
    ax.set_ylabel("Predicted")


def study_outsiders(form_dfs, honeypots, dist_lshtein):
    """ "
    Display the words considered as outsiders by the honey_pots detector

    Args:
        honeypots (list of str): honeypots
        dist_lshtein (int): levenshtein tolerance
    """
    outsiders = {}
    for form_df in form_dfs:
        em = form_df.columns[7]
        form_df[em].unique()
        frauders = detect_honey_frauders(
            form_df, honeypots=honeypots, dist_lshtein=dist_lshtein
        )
        if len(frauders) > 0:
            weird_words = form_df[form_df["WorkerID"].isin(frauders)][em].unique()
            if em in outsiders:
                outsiders[em].update(weird_words)
            else:
                outsiders[em] = set(weird_words)
    return outsiders
