"""
Main file to generate all figures and results as described in the paper
"""
from src.selection.selection import main as selection
from src.selection.distribution import main as distribution
from src.analysis.postprocessing import main as dataset_generation
from src.visualization.tsne_viz import main as tsne
from src.validation.w2v import main as w2v
from src.validation.bert_embedder import main as bert_embedder
import pdb
import sys
import traceback

def print_sep(title):
    print("\n\n" + "=" * 15 +f" {title} "+ "=" * 15)

if __name__ == '__main__':
    try:
        print_sep("Selection")
        selection()

        print_sep("Distribution")
        distribution()

        print_sep("Dataset generation")
        dataset_generation()

        print_sep("Word2vec training")
        w2v("e2v")
        w2v("em_dataset")

        print_sep("BERT embedding")
        bert_embedder("e2v")
        bert_embedder("em_dataset")

        print_sep("TSNE plot computation")
        tsne("e2v",embedding_type="w2v")
        tsne("em_dataset",embedding_type="w2v")
        tsne("e2v",embedding_type="bert")
        tsne("em_dataset",embedding_type="bert")
    except:
        # debugger
        extype, value, tb = sys.exc_info()
        traceback.print_exc()
        pdb.post_mortem()




