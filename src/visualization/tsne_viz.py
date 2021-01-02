import matplotlib
# import mplcairo
# matplotlib.use("module://mplcairo.qt")

import os
import matplotlib.pyplot as plt
import tensorflow as tf
import numpy as np
import sklearn.manifold as man
import pickle as pk
import gensim.models as gs
from src.constants import W2V_PATH,EMOJI_FONT_PATH,EXPORT_DIR,EMOJI_2_TOP_INDEX_PATH
from matplotlib.font_manager import FontProperties
from src.constants import emotions_faces
import argparse
from pathlib import Path
from src.validation.bert_embedder import BertWrapper



def tsne_plot(e2v, em_list, name="emojis_tsne", fontsize=12, w2v=None, word_list=None,fig=None,ax=None):
    """
    create the array of shape N_emoji x embedding_dimension

    Args:
        e2v: object with get_vector function returning an np.array embedding given an emoji
        in parameter
        em_list (list of str): list of emojis to compute the plot for
    """
    assert (w2v is None and word_list is None) or (
        w2v is not None and word_list is not None
    )
    # Special Font required to plot emojis
    if matplotlib.get_backend() == "module://mplcairo.qt":
        prop = FontProperties(fname=EMOJI_FONT_PATH)
    else:
        prop=None

    # Extract embeddingsd
    embedding = [e2v.get_vector(em) for em in em_list]
    if w2v is not None:
        embedding = embedding + [w2v.get_vector(word) for word in word_list]
    embedding = np.array(embedding)
    n_iter = 5000
    if os.environ.get('DEBUG') is not None:
        n_iter = 500
    tsne = man.TSNE(perplexity=30, n_components=2, init="pca", n_iter=n_iter, verbose=1)
    trans = tsne.fit_transform(embedding)
    x, y = zip(*trans)
    plt.scatter(x, y, marker="o", alpha=0.0)

    for em, vec in zip(em_list, trans):
        ax.annotate(
            em, xy=vec, textcoords="data", fontproperties=prop, fontsize=fontsize
        )
    # Add word information
    if word_list is not None:
        for word, vec in zip(word_list, trans[len(em_list) :]):
            ax.annotate(word, xy=vec, textcoords="data", fontsize=8)
    

    plt.grid()


def main(model_type,embedding_type,use_faces=False,use_words=False):
    assert(model_type in ["e2v","em_dataset"])
    assert(embedding_type in ["w2v","bert"])

    if embedding_type == "bert":
        if model_type == "em_dataset":
            input_path = EXPORT_DIR.joinpath("data/embeddings/bert/em_dataset.pk")
            mapping = pk.load(open(EMOJI_2_TOP_INDEX_PATH,"rb"))
            mapping = {val:key for key,val in mapping.items()}
        else:
            input_path = EXPORT_DIR.joinpath("data/embeddings/bert/e2v.pk")
            mapping_path = EXPORT_DIR.joinpath("data/embeddings/word2vec/e2v/mapping.pk")
            mapping = pk.load(open(mapping_path,"rb"))
        e2v = BertWrapper(input_path)
    else:
        if model_type == "e2v":
            input_dir = EXPORT_DIR.joinpath("data/embeddings/word2vec/e2v/")
        else:
            input_dir = EXPORT_DIR.joinpath("data/embeddings/word2vec/em_dataset/")
        input_path = input_dir.joinpath("emoji2vec.bin")
        e2v = gs.KeyedVectors.load_word2vec_format(input_path, binary=True)
        mapping_path = str(input_dir.joinpath("mapping.pk"))
        mapping = pk.load(open(mapping_path, "rb"))

    fig, ax = plt.subplots(1, figsize=(10, 20))

    if use_faces:
        print("Computing tsne for emotions faces exclusively")
        if use_words:
            word_list = [
                "happy",
                "enthusiastic",
                "sad",
                "melancholic",
                "angry",
                "annoyed",
                "perplex",
                "neutral",
                "hilarious",
                "afraid",
                "love",
                "surprised",
            ]
            w2v = gs.KeyedVectors.load_word2vec_format(W2V_PATH, binary=True)
            tsne_plot(
                e2v,
                emotions_faces,
                name="faces_tsne_words",
                fontsize=25,
                w2v=w2v,
                word_list=word_list,
            )
        else:
            tsne_plot(e2v, emotions_faces, name="faces_tsne", fontsize=25)
    else:
        print("Computing tsne for all emojis")
        tsne_plot(e2v, mapping.values(),fig=fig,ax=ax)
    ax.set_title(f"TSNE embedding of {model_type} using {embedding_type}",fontsize=25)
    out_path = f"{model_type}_{embedding_type}_tsne.jpeg"
    plt.savefig(EXPORT_DIR.joinpath("report_files/" + out_path))



if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-f", "--faces", help="compute faces tsne exclusively", action="store_true"
    )
    parser.add_argument(
        "-w", "--words", help="compute words with faces", action="store_true"
    )
    parser.add_argument(
        "-m", "--model_type", help="either e2v or em_dataset",default="em_dataset"
    )
    args = parser.parse_args()

