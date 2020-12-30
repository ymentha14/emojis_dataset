import matplotlib, mplcairo
matplotlib.use("module://mplcairo.qt")
import matplotlib.pyplot as plt
import tensorflow as tf
import numpy as np
import sklearn.manifold as man
import pickle as pk
import gensim.models as gs
from src.constants import W2V_PATH, EMOJI_FONT_PATH,EXPORT_DIR
from matplotlib.font_manager import FontProperties
from src.constants import emotions_faces
import argparse
from pathlib import Path


def tsne_plot(e2v, em_list, name="emojis_tsne", fontsize=12, w2v=None, word_list=None,fig=None,ax=None):
    """ create the array of shape N_emoji x embedding_dimension"""
    assert (w2v is None and word_list is None) or (
        w2v is not None and word_list is not None
    )
    # Special Font required to plot emojis
    prop = FontProperties(fname=EMOJI_FONT_PATH)

    # Extract embeddingsd
    embedding = [e2v.get_vector(em) for em in em_list]
    if w2v is not None:
        embedding = embedding + [w2v.get_vector(word) for word in word_list]
    embedding = np.array(embedding)
    tsne = man.TSNE(perplexity=30, n_components=2, init="pca", n_iter=5000, verbose=1)
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


def main(model_type,use_faces=False,use_words=False):
    assert(model_type in ["e2v","em_dataset"])
    if model_type == "e2v":
        input_dir = EXPORT_DIR.joinpath("data/word2vec/e2v")
    else:
        input_dir = EXPORT_DIR.joinpath("data/word2vec/em_dataset")

    mapping_path = str(input_dir.joinpath("mapping.pk"))
    bin_path = str(input_dir.joinpath("emoji2vec.bin"))

    # emojis embedding
    e2v = gs.KeyedVectors.load_word2vec_format(bin_path, binary=True)
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

    model_type = model_type + "_tsne.jpeg"
    plt.savefig(EXPORT_DIR.joinpath(model_type))



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

