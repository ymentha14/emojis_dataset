import pandas as pd
import matplotlib.pyplot as plt
import tensorflow as tf
import numpy as np
import emoji

from utils import build_kb, get_examples_from_kb, generate_embeddings, get_metrics
import pandas as pd
import gensim.models as gs
from pathlib import Path
import gensim.models as gs
import warnings
from scipy.stats import hmean
from scipy import spatial
warnings.filterwarnings("ignore")


def read_form(path):
    """
    Read the .csv file as returned by the google form
    """
    form_df = (pd.read_csv(path)
              .set_index('Worker ID'))
    form_df = (form_df.rename(columns={col_name:col_name.strip() for col_name in form_df.columns})
                  .drop(columns=["Timestamp"]))
    return form_df

def user_representation(formdf,w2v):
    """
    represent an emoji from a specific user by summing the answer representations together
    
    Args:
        formdf (pd.DataFrame): the data as received in the formular
        emoji (string): emoji to 
    """
    df = formdf.transpose().copy()
    em_reps = []
    for em,row in df.iterrows():
        new_row = [em]
        em_rep = []
        for word3 in row:
            rep3 = []
            for word in word3.split(","):
                try:
                    wordvec = w2v.get_vector(word)
                    rep3.append(wordvec)
                except KeyError:
                    pass
            if len(rep3) > 0:
                rep3 = np.sum(rep3,axis=0)
                em_rep.append(rep3)
        new_row.append(np.array(em_rep))
        em_reps.append(new_row)

    em_reps = (pd.DataFrame(em_reps,columns=["em","reps"])
               .set_index('em'))
    return em_reps

def unif_representation(form1_df,w2v):
    """
    represent an emoji by the sum of each word answers'vector
    """
    df = form1_df.transpose().copy()
    em_reps = []
    for em,row in df.iterrows():
        new_row = [em]
        em_rep = []
        for word3 in row:
            for word in word3.split(","):
                try:
                    wordvec = w2v.get_vector(word)
                    em_rep.append(wordvec)
                except KeyError:
                    pass
        new_row.append(np.array(em_rep))
        em_reps.append(new_row)

    em_reps_df = (pd.DataFrame(em_reps,columns=["em","reps"])
               .set_index('em'))
    return em_reps_df

def compute_det(df):
    """
    compute the determinant of the correlation matrix for each emoji
    """
    df['det'] = df['reps'].apply(lambda x:np.linalg.det(np.corrcoef(x)))

def print_det(df,ax=None,fig=None):
    """
    print the determinant
    """
    compute_det(df)
    if ax is None:
        fig,ax = plt.subplots(1)
    df = df.sort_values('det')
    ax.set_title("Determinant of correlation matrix amongst crowdsourced words vectors")
    df['det'].plot.bar(ax=ax)
    print("Emojis:",end="")
    for i in df.index:
        print(i,end=" ")

def print_num_words(df,ax=None,fig=None):
    """
    plot the number of unique words used to describe an emoji in teh formular
    """
    if ax is None:
        fig,ax = plt.subplots(1)
    df = df.applymap(lambda x: x.split(","))
    df = df.apply(lambda k:len(set([y for x in k for y in x ])),axis=0)
    ax.set_title("Number of unique words")
    df = df.sort_values()
    df.plot(kind='bar',ax=ax)

    print("Emojis:",end="")
    for i in df.index:
        print(i,end=" ")


    
def compute_em2v_vecs(df,e2v):
    """
    add the emoji2vec representation, the mean/median rep of the crowdsourced data
    along with the corresponding correlations    
    """
    df['em2vec_rep'] = df.index.map(lambda x: e2v.get_vector(x))
    
    # mean representation of the crowdsourced vectors
    df['mean_rep'] = df['reps'].apply(lambda x: np.mean(x,axis=0))
    df['corr_mean'] = df[['mean_rep','em2vec_rep']].apply(lambda x:np.corrcoef(x[0],x[1])[0,1],axis=1)
    
    # median representation of the crowdsourced vectors
    df['median_rep'] = df['reps'].apply(lambda x: np.median(x,axis=0))
    df['corr_median'] = df[['median_rep','em2vec_rep']].apply(lambda x:np.corrcoef(x[0],x[1])[0,1],axis=1)

def plot_corr(df,agg_type="mean",ax=None):
    """
    plot the emojis along with the correlation of their
    mean/median representation
    """
    if ax is None:
        fig,ax = plt.subplots(1)
    df = df.sort_values(f'corr_{agg_type}')
    ax.set_title(f"Correlations between {agg_type} of crowdsourced rep and emojivec rep")
    df[f'corr_{agg_type}'].plot.bar(ax=ax)
    print("Emojis:",end="")
    for i in df.index:
        print(i,end=" ")

def get_words_scores(form1_df,user_df,w2v,col="mean_rep"):
    """
    return the words appearing with each emoji along with the cosine similarity and the correlation
    with the emoji in question
    """
    words_scores_df = form1_df.transpose().agg(",".join,axis=1)

    words_scores_df = (words_scores_df.apply(lambda x: list(set(x.split(","))))
                         .reset_index()
                         .rename(columns={0:'word','index':'em'}))

    words_scores_df = words_scores_df.explode("word")

    # we keep the words that are present in the vocabulary of word2vec
    words_scores_df = words_scores_df[words_scores_df.word.isin(w2v.vocab)]
    # extract the word vectors
    words_scores_df['wordvec'] = words_scores_df['word'].apply(lambda word: w2v.get_vector(word))

    words_scores_df = pd.merge(words_scores_df,user_df[col],on='em',how='inner')
    words_scores_df['word_corr'] = words_scores_df[['wordvec',col]].apply(lambda x:np.corrcoef(x[0],x[1])[0,1],axis=1)

    words_scores_df['word_cossim'] = words_scores_df[['wordvec',col]].apply(lambda x:(1-spatial.distance.cosine(x[0], x[1])),axis=1)
    return words_scores_df

def print_best_words_emojis(words_scores_df,col='word_corr',em=None):
    """
    Plots the most correlated words alongs with the score for each emoji
    
    Args:
        words_scores_df (pd.DataFrame): as returned by get_words_scores
        col (str): metric of interest: either "word_corr" or "word_cossim"
        em (str): if specified, plots the scores only for this emoji
    """
    words_scores_df = words_scores_df.sort_values(['em',col],ascending=False)
    words_scores_df = words_scores_df.groupby('em')[['word',col]].agg(list)
    
    if em is not None:
        words_scores_df = words_scores_df[words_scores_df.index == em]
    print("Closest words in vector space:")
    for em,(words,words_corr) in words_scores_df[['word',col]].iterrows():
        print(f"Emoji{em}:")
        for word,word_corr in zip(words,words_corr):
            print(f"\t{word} {word_corr:.2f}")

def get_words_counts(form1_df,em):
    """
    Print the most common words in the crowdsourced data for the emoji
    passed in parameter
    
    Args:
        form1_df (pd.DataFrame): as defined above
        em (str): emoji of interest
    """
    print("Sorted most common words in crowdsourced data:")
    word_counts = pd.Series(form1_df
                  .transpose()
                  .agg(",".join,axis=1)
                  .loc[em]
                  .split(",")).value_counts()
    print(f"Emoji:{em}:")
    for word,count in word_counts.iteritems():
        print(f"\t{word} {count}")

def plot_best_words_emojis(words_scores_df,em,col='word_corr',ax=None):
    """
    Plots the most correlated words alongs with the score for each emoji
    
    Args:
        words_scores_df (pd.DataFrame): as returned by get_words_scores
        col (str): metric of interest: either "word_corr" or "word_cossim"
        em (str): if specified, plots the scores only for this emoji
    """
    if ax is None:
        fig,ax = plt.subplots(1,1)
    words_scores_df = words_scores_df[words_scores_df['em'] == em]
    words_scores_df = words_scores_df.sort_values(['em',col],ascending=False)
    print(f"Emoji {em}:")
    words_scores_df.plot.bar(ax=ax,x="word",y="word_corr")
    ax.set_title("Word Correlation between crowdsourced data and emoji")