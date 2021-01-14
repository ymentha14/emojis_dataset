import matplotlib
import matplotlib.pyplot as plt
import pandas as pd
import os
import tensorflow as tf
import pickle as pk
import numpy as np
import sklearn.manifold as man
from tensorflow.python.framework import ops

from emoji2vec.model import Emoji2Vec, ModelParams
from emoji2vec.phrase2vec import Phrase2Vec
from emoji2vec.utils import (
    build_kb,
    get_examples_from_kb,
    generate_embeddings,
    get_metrics,
)
from emoji2vec.train import train_save_evaluate

from src.constants import (
    E2V_MAPPING_PATH,
    EMOJI_2_TOP_INDEX_PATH,
    E2V_DATA_DIR,
    EXPORT_DIR,
    EMBEDDING_TRAINING_DATA_DIR,
    W2V_PATH,
)


def split_dataset_df(dataset_df, ratios):
    """
    Split the dataset into 3 random parts respecting the ratios describes in the
    ratios parameter for every emoji ==> every emoji is represented

    Args:
        dataset_df (pd.df): dataset to split
        ratio (tuple of float): 3 ratios for train/dev/test summing up to 1
    """
    assert sum(ratios) == 1
    grouped_df = dataset_df.groupby("emoji")
    train = []
    dev = []
    test = []
    for em in dataset_df["emoji"].unique():
        df = grouped_df.get_group(em).sample(frac=1)
        n = df.shape[0]
        n1 = int(n * ratios[0])
        n2 = int(n * (ratios[0] + ratios[1]))
        train.append(df.iloc[:n1])
        dev.append(df.iloc[n1:n2])
        test.append(df.iloc[n2:])
    train = pd.concat(train, axis=0)
    dev = pd.concat(dev, axis=0)
    test = pd.concat(test, axis=0)
    return train, dev, test


def convert_to_e2v_format(df):
    """
    Converts the dataframe in production format to an emoji2vec compliant format
    """
    df = df.copy()
    df["label"] = True
    df = df[["word", "emoji", "label"]].reset_index(drop=True).sample(frac=1)
    return df


def get_neg_df(df):
    """
    Create a negative sampling copy of the dataframe in e2v format
    """
    df_neg = df.copy()

    emojis = set(df_neg["emoji"].unique())

    em_vocs = df_neg.groupby("emoji")["word"].agg(lambda x: set(x)).to_dict()

    tot_voc = set.union(*em_vocs.values())

    neg_words = [
        np.random.choice(list(tot_voc - em_vocs[em])) for em in df_neg["emoji"]
    ]
    df_neg["word"] = neg_words
    df_neg["label"] = False
    return df_neg


def get_train_val_test(dataset_df):
    """
    Generate the dataframe associated to the right format to train
    a w2v model on the emojis

    Args:
        dataset_df (pd.df): dataframe in production format

    Return:
        [pd.df]: train dataframe
        [pd.df]: validation dataframe with neg sampling
        [pd.df]: test dataframe with neg sampling
    """
    ratios = (0.8, 0.1, 0.1)
    train_df, dev_df, test_df = split_dataset_df(dataset_df, ratios)

    train_df = convert_to_e2v_format(train_df)

    dev_df = convert_to_e2v_format(dev_df)
    dev_df_neg = get_neg_df(dev_df)
    dev_df = dev_df.append(dev_df_neg).sample(frac=1)

    test_df = convert_to_e2v_format(test_df)
    test_df_neg = get_neg_df(test_df)
    test_df = test_df.append(test_df_neg).sample(frac=1)

    n_emojis = dataset_df["emoji"].unique().shape[0]
    assert train_df["emoji"].unique().shape[0] == n_emojis
    assert test_df["emoji"].unique().shape[0] == n_emojis
    assert dev_df_neg["emoji"].unique().shape[0] == n_emojis

    return train_df, dev_df, test_df


def compute_w2v_data():
    # We read the data we just produced
    dataset_df = pd.read_csv(EXPORT_DIR.joinpath(
        "data/dataset/emoji_dataset_prod.csv"))
    # and create/save the word2vec data from it
    train_df, dev_df, test_df = get_train_val_test(dataset_df)
    train_df.to_csv(
        EMBEDDING_TRAINING_DATA_DIR.joinpath("train.txt"),
        sep="\t",
        header=None,
        index=False,
    )
    dev_df.to_csv(
        EMBEDDING_TRAINING_DATA_DIR.joinpath("dev.txt"),
        sep="\t",
        header=None,
        index=False,
    )
    test_df.to_csv(
        EMBEDDING_TRAINING_DATA_DIR.joinpath("test.txt"),
        sep="\t",
        header=None,
        index=False,
    )


def main(model_type="em_dataset"):
    assert model_type in ["e2v", "em_dataset"]

    if model_type == "em_dataset":
        # compute word2vec complient data
        compute_w2v_data()
        export_dir = EXPORT_DIR.joinpath("data/embeddings/word2vec/em_dataset")
        export_dir.mkdir(exist_ok=True, parents=True)
        word2vec_path = str(W2V_PATH)
        data_dir = str(EMBEDDING_TRAINING_DATA_DIR)
        mapping_path = str(export_dir.joinpath("mapping.pk"))
        embeddings_file = str(export_dir.joinpath("embeddings.pk"))
        ckpt_path = str(export_dir.joinpath("model.ckpt"))
        e2v_path = str(export_dir.joinpath("emoji2vec.bin"))
        dataset_name = "emojis_dataset"
    else:
        export_dir = EXPORT_DIR.joinpath("data/embeddings/word2vec/e2v")
        export_dir.mkdir(exist_ok=True, parents=True)
        word2vec_path = str(W2V_PATH)
        # data src dir
        data_dir = str(E2V_DATA_DIR.joinpath("training/"))
        # where to store the mapping path
        mapping_path = str(export_dir.joinpath("mapping.pk"))
        embeddings_file = str(export_dir.joinpath("embeddings.pk"))
        dataset_name = "unicode"
    in_dim = 300  # Length of word2vec vectors
    out_dim = 300  # Desired dimension of output vectors
    pos_ex = 4
    neg_ratio = 1
    max_epochs = 40

    # debug mode
    if os.environ.get("DEBUG") is not None:
        max_epochs = 2

    dropout = 0.0

    params = ModelParams(
        in_dim=in_dim,
        out_dim=out_dim,
        pos_ex=pos_ex,
        max_epochs=max_epochs,
        neg_ratio=neg_ratio,
        learning_rate=0.001,
        dropout=dropout,
        class_threshold=0.5,
    )

    # Build knowledge base
    train_kb, ind2phr, ind2emoji = build_kb(data_dir)
    pk.dump(ind2emoji, open(mapping_path, "wb"))

    # Get the embeddings for each phrase in the training set
    embeddings_array = generate_embeddings(
        ind2phr=ind2phr,
        kb=train_kb,
        embeddings_file=embeddings_file,
        word2vec_file=word2vec_path,
    )

    # Get examples of each example type in two sets. This is just a reprocessing of the knowledge base for efficiency,
    # so we don't have to generate the train and dev set on each train
    train_set = get_examples_from_kb(kb=train_kb, example_type="train")
    dev_set = get_examples_from_kb(kb=train_kb, example_type="dev")

    train_save_evaluate(
        params=params,
        kb=train_kb,
        train_set=train_set,
        dev_set=dev_set,
        ind2emoji=ind2emoji,
        embeddings_array=embeddings_array,
        dataset_name=dataset_name,
        export_dir=str(export_dir),
    )
