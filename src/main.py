"""
Main file to generate all figures and results as described in the paper
"""
from src.selection.selection import main as selection
from src.selection.distribution import main as distribution
from src.analysis.postprocessing import main as dataset_generation
def print_sep(title):
    print("\n\n" + "=" * 15 +f" {title} "+ "=" * 15)

if __name__ == '__main__':
    # print_sep("Selection")
    # selection()
    # print_sep("Distribution")
    # distribution()
    print_sep("Dataset generation")
    dataset_generation()

