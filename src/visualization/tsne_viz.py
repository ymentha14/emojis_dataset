import matplotlib, mplcairo
matplotlib.use("module://mplcairo.qt")
import matplotlib.pyplot as plt
import tensorflow as tf
import numpy as np
import sklearn.manifold as man
import pickle as pk
import gensim.models as gs
from src.constants import E2V_PATH, MAPPING_PATH, W2V_PATH
from matplotlib.font_manager import FontProperties
from src.constants import emotions_faces
import argparse
from pathlib import Path

def tsne_plot(e2v,em_list,name="emojis_tsne",fontsize=12,w2v=None,word_list=None):
    """ create the array of shape N_emoji x embedding_dimension"""
    assert((w2v is None and word_list is None) or (w2v is not None and word_list is not None))
    prop = FontProperties(fname="/home/ymentha/Downloads/Apple Color Emoji.ttf")
    embedding = [e2v.get_vector(em) for em in em_list]
    if w2v is not None:
        embedding = embedding + [w2v.get_vector(word) for word in word_list]
    embedding = np.array(embedding)
    fig,ax = plt.subplots(1,figsize=(10,20))
    tsne = man.TSNE(perplexity=30, n_components=2, init='pca', n_iter=5000,verbose=1)
    trans = tsne.fit_transform(embedding)
    x, y = zip(*trans)
    plt.scatter(x, y, marker='o', alpha=0.0)

    for em,vec in zip(em_list,trans):
        ax.annotate(em, xy=vec, textcoords='data',fontproperties=prop,fontsize=fontsize)
    for word,vec in zip(word_list,trans[len(em_list):]):
        ax.annotate(word, xy=vec, textcoords='data',fontsize=8)

    plt.grid()

    save_path = Path('../../results/tsne/')
    plt.savefig(save_path.joinpath(name).with_suffix(".jpeg"))
    plt.show()
    
    
# def tsne_plot(e2v,em_list,name="emojis_tsne",fontsize=12):
#     """ create the array of shape N_emoji x embedding_dimension"""
#     prop = FontProperties(fname="/home/ymentha/Downloads/Apple Color Emoji.ttf")
#     embedding = np.array([e2v.get_vector(em) for em in em_list])
#     fig,ax = plt.subplots(1,figsize=(10,20))
#     tsne = man.TSNE(perplexity=30, n_components=2, init='pca', n_iter=5000,verbose=1)
#     trans = tsne.fit_transform(embedding)
#     x, y = zip(*trans)
#     plt.scatter(x, y, marker='o', alpha=0.0)

#     for em,vec in zip(em_list,trans):
#         ax.annotate(em, xy=vec, textcoords='data',fontproperties=prop,fontsize=fontsize)
#     plt.grid()

#     save_path = Path('../../results/tsne/')
#     plt.savefig(save_path.joinpath(name).with_suffix(".jpeg"))
#     plt.show()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("-f", "--faces", help="compute faces tsne exclusively",
                    action="store_true")
    parser.add_argument("-w", "--words", help="compute words with faces",
                    action="store_true")
    args = parser.parse_args()

    # mapping from id to emoji
    mapping = pk.load(open(MAPPING_PATH, 'rb'))
    # emojis embedding

    e2v = gs.KeyedVectors.load_word2vec_format(E2V_PATH, binary=True)
    if args.faces:
        print("Computing tsne for emotions faces exclusively")
        if args.words:
            word_list = ["happy","enthusiastic","sad","melancholic","angry","annoyed","perplex","neutral","hilarious","afraid","love","surprised"]
            w2v = gs.KeyedVectors.load_word2vec_format(W2V_PATH, binary=True)
            tsne_plot(e2v,emotions_faces,name="faces_tsne_words",fontsize=25,w2v=w2v,word_list=word_list)
        else:
            tsne_plot(e2v,emotions_faces,name="faces_tsne",fontsize=25)
    else:
        print("Computing tsne for all emojis")
        tsne_plot(e2v,mapping.values())
