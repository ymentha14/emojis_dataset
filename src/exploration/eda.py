"""
Exploratory data analysis functions
"""


import matplotlib
import matplotlib.pyplot as plt
import tensorflow as tf
import pickle as pk
import numpy as np
import sklearn.manifold as man
from tensorflow.python.framework import ops
import emoji
import sys
from emoji2vec.phrase2vec import Phrase2Vec
from emoji2vec.utils import (
    build_kb,
    get_examples_from_kb,
    generate_embeddings,
    get_metrics,
)
import pandas as pd
import gensim.models as gs
from pathlib import Path
from src.constants import (
    emotions_faces,
    REF_PATH,
    MAPPING_PATH,
    E2V_PATH,
    W2V_PATH,
    DATA_PATH,
)
import gensim.models as gs


def get_desc_emojis_df(phraseVecModel):
    """create the emojis description dataframe with respective embeddings"""
    desc_words_df = pd.read_csv(DATA_PATH, sep="\t", header=None, names=["desc", "em"])
    desc_words_df["vec"] = desc_words_df["desc"].apply(lambda x: phraseVecModel[x])
    return desc_words_df


def gather_descs_vecs(desc_words_df, inv_map):
    """
    gather the vectors and descriptions of the different
    description for a same emojis by applying a groupby
    """
    grouped_desc_df = desc_words_df.groupby("em")
    grp_vec = grouped_desc_df.vec.apply(list)
    grp_desc = grouped_desc_df.desc.apply(list)

    grouped_desc_df = pd.concat([grp_vec, grp_desc], axis=1).reset_index()

    grouped_desc_df.index = grouped_desc_df.em.map(inv_map)

    grouped_desc_df.sort_index(inplace=True)

    grouped_desc_df["length"] = grouped_desc_df.vec.apply(len)

    return grouped_desc_df


def plot_num_desc_per_emoji(grouped_desc_df):
    """ plot the hist of number of desc for an emoji"""
    fig, ax = plt.subplots(1)
    grouped_desc_df["length"].hist(bins=30, ax=ax)
    ax.set_title("Number of descriptions for a single emoji")


def dispersion(vecs):
    """
    Calculate the dispersion of vecs using L1 norm

    Args:
        vecs(list np.array): vectors representations of the multiple descriptions of an emoji

    Returns:
        [float]: measure of the dispersion
    """
    if len(vecs) == 1:
        return 0
    mean_vec = np.mean(vecs, axis=0)
    l1 = np.mean([np.abs(mean_vec - vec) for vec in vecs])
    return l1


def display_emoji_desc(df):
    """print the texts of an emoji along with its dispersion"""
    for _, row in df.iterrows():
        em = row.em
        descs = row.desc
        disp = row.dispersion
        print(f"{em} (disp={disp:.2f})")
        for desc in descs:
            print(f"\t{desc}")


def get_emoji_df(e2v, mapping):
    """ create the emoji-vec dataframe"""
    em_df = [
        {"index": i, "em": em, "vec": e2v.get_vector(em)} for i, em in mapping.items()
    ]
    em_df = pd.DataFrame(em_df).set_index("index")
    return em_df


def get_10_faces(em, e2v, num_faces=5):
    """returns the top 10 most similar faces"""
    topn = num_faces
    faces = [i[0] for i in e2v.similar_by_word(em, topn=topn)]
    while not (
        all([face in emotions_faces for face in faces]) and len(faces) == num_faces
    ):
        topn += 1
        faces = [i[0] for i in e2v.similar_by_word(em, topn=topn)]
        faces = [face for face in faces if face in emotions_faces]
        # if topn > 100:
        #    raise ValueError("Nonsense representation of an emoji")
    return faces
