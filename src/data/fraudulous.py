import pickle as pk
from src.constants import emotions_faces,REF_PATH,MAPPING_PATH, E2V_PATH, W2V_PATH, DATA_PATH
import sys
sys.path.append("../../emoji2vec_working/")
from phrase2vec import Phrase2Vec
from src.data.form10_eda import *
import seaborn as sns
import numpy as np
from src.constants import COLOR_FRAUD,COLOR_TRUE


def plot_double_hist(user_serie,fraud):
    user_serie = user_serie.astype(int)
    user_serie_true = user_serie[~user_serie.index.isin(fraud)]
    user_serie_fraud = user_serie[user_serie.index.isin(fraud)]
    fig,ax = plt.subplots(1)
    ax.set_title("Rates of constant-answering users")
    user_serie = user_serie.value_counts()
    #user_serie_true.plot(kind='bar',color=COLOR_TRUE,label=,rot=0,ax=ax,alpha=0.5)
    #user_serie_fraud.plot(kind='bar',color=COLOR_FRAUD,label="fraud",rot=0,ax=ax,alpha=0.5)
    ax.hist([user_serie_true,user_serie_fraud],color=[COLOR_TRUE,COLOR_FRAUD],label=["non-fraud","fraud"])
    ax.set_xlabel("Fraudulent")
    ax.set_ylabel("Users count")
    ax.legend()

# CONSTANTS
def get_users_cstt(form_df):
    if type(form_df) is list:
        return pd.concat([get_users_cstt(df) for df in form_df])
    formset_df = form_df.applymap(lambda x: frozenset(x.split(",")))
    # detect users giving constant answers
    cstt_mask = (formset_df.applymap(len) ==1).any(axis=1)
    return cstt_mask

def dtct_cstt_answer(form_df):
    """ detect users giving at least one cstt answer (3 times the same word)"""
    cstt_mask = get_users_cstt(form_df)
    cstt_users = cstt_mask.index[cstt_mask].tolist()
    return cstt_users

# DUPLICATES
def get_users_duplicate(form_df,ratio=0.9):
    if type(form_df) is list:
        return pd.concat([get_users_duplicate(df) for df in form_df])
    n_cols = form_df.shape[1]
    # transform the strings in frozen sets
    form_df = form_df.applymap(lambda x: frozenset(x.split(",")))
    duplicate_mask = form_df.apply(lambda x:len(set(x)) < int(n_cols * ratio),axis=1)
    return duplicate_mask

def dtct_duplicate_answer(form_df,ratio=0.95):
    """detect users giving many times the same answer (up to ratio * the number of answers)"""
    duplicate_mask = get_users_duplicate(form_df,ratio)
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
    return form_df.apply(lambda x:len(set("".join(x).split(","))),axis=1)   

def plot_voc(tot_voc,fraud):
    """
    Plot overlapping histograms of vocabulary size for fraudulent
    and non fraudulent users
    
    Args:
        tot_voc (pd.Series): serie associating a voc size to each user
        fraud (set): set of fraudulent users
    """
    fig,ax = plt.subplots(1)
    ax.set_title("Vocabulary size for non/fraudulent users")
    bins = 10
    tot_voc_true = tot_voc[~tot_voc.index.isin(fraud)]
    tot_voc_fraud = tot_voc[tot_voc.index.isin(fraud)]
    ax.hist([tot_voc_true,tot_voc_fraud],
            color=[COLOR_TRUE,COLOR_FRAUD],
            bins=bins)
    ax.set_xlabel("Voc size")
    ax.set_ylabel("Users count")
    ax.legend()

def dtct_poor_voc(form_df,ratio=0.55):
    voc = compute_voc_size(form_df)
    N = form_df.shape[1]
    N_lim = int(ratio*N*3)
    poor_users = voc[voc <= N_lim].index.tolist()
    return poor_users

# SEMANTIC
def get_vec_error(form_df,w2v,e2v,ref="mean",loss="l1"):
    """
    return the mean MSE over each emoji for each user
    """
    cols = [col for col in form_df.columns if col in e2v.vocab]
    form_df = form_df[cols]
    vec_error = form_df.applymap(lambda x: np.mean([w2v.get_vector(word) 
                                         for word in x.split(",") if word in w2v.vocab],
                                        axis=0)
                     )
    if ref == "mean":
        # using average of batch as reference
        mean_vecs = np.mean(vec_error.values,axis=0).tolist()
    else:
        assert(ref == "em")
        # using emojis vec as reference
        mean_vecs = [e2v.get_vector(em) for em in form_df.columns]
    # normalize
    if loss == "l2":
        vec_error = (vec_error - mean_vecs).applymap(lambda x: x**2).applymap(sum)
    else:
        assert(loss=="l1")
        vec_error = abs(vec_error -mean_vecs).applymap(sum)
    vec_error = vec_error.sum(axis=1).sort_values()
    return vec_error

def dtct_vec_error(form_df):
    vec_error = get_vec_error(form1_df)
    return vec_error.head(3).index.tolist()

def plot_vec_error(vec_error,fraud,ax=None):
    """
    Plot the error for each user as a barplot

    Args:
        vec_error(pd.Series): vector associating the L1orL2 error to each user (index)
        fraud (set): set of fraudulous users
    """
    if ax is None:
        fig,ax = plt.subplots(1)
    vec_error = vec_error.to_frame("error")
    vec_error['color'] = [COLOR_FRAUD if ind in fraud else COLOR_TRUE for ind in vec_error.index]
    vec_error['error'].plot.bar(color=vec_error.color,ax=ax)
    ax.set_title("mean L2orL1 error between user and emoji representations")
    ax.set_xlabel("user id")
    ax.set_ylabel("L2orL1")

#FRAUDULOUS DETECTION
def gather_users(*args):
    """ gather the users of every formdf passed in parameter into a single set"""
    return set.union(*[set(form_df.index.tolist()) for form_df in args])

def find_fraudulous(form_df,filter_funcs):
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

def fraud_metrics(users,fraud,fraud_hat):
    """
    Plot the fraudulous analysis metrics
    """
    TP = len(fraud.intersection(fraud_hat))
    FP = len(fraud_hat - fraud)
    FN = len(fraud - fraud_hat)
    TN = len((users - fraud.union(fraud_hat)))

    accuracy = (TN + TP)/(TP + TN + FP + FN)
    precision = TP / (TP + FP)
    recall = TP / (TP + FN)
    confusion_matrix = np.array([[TP,FP],[FN,TN]])
    print(f"Accuracy:{accuracy}\nPrecision:{precision}\nRecall:{recall}")
    fig,ax = plt.subplots(1)
    sns.heatmap(confusion_matrix, annot=True,ax=ax,xticklabels=['P','N'],yticklabels=['P','N'])
    ax.set_xlabel("True")
    ax.set_ylabel("Predicted")
