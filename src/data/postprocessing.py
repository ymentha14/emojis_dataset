"""
Post processing analysis of the .csv files from the gforms
"""
from IPython.display import display
import pandas as pd
from tqdm import tqdm
from src.constants import SELECTED_EMOJIS2INDEXES_PATH
from src.constants import EMOJIS
from src.constants import HONEYPOTS
import pickle as pk

def get_emojis_voc_counts(path):
    """
    Generate a value count of words for all emojis present in csv files of the path
    provided in parameter

    Args:
        path (pathlib.Path): parent path of the csv files

    Return:
        em2vocab [dict of dict]: a dict associating each word to its count is mapped for each emoji
    """
    em2vocab = {}
    for path in path.glob("**/[0-9]*.csv"):
        df = pd.read_csv(path)
        emojis = [col for col in df.columns if col not in ["Timestamp", "Worker ID","Feedback"]]
        for em in emojis:
            vocab = em2vocab.get(em,{})
            for word,count in df[em].value_counts().iteritems():
                pre_count = vocab.get(word,0)
                pre_count += count
                vocab[word] = pre_count
            em2vocab[em] = vocab
    return em2vocab

def write_emojis_voc_counts(em2vocab,path):
    """
    write the dict of dict as generated by get_emojis_voc_counts

    Args:
        em2vocab (dict of dict): dict associating each word to its count is mapped for each emoji
        path (str/pathlib.Path): path where to write the file
    """
    with open(path,"w") as f:
        for em,wordcounts in em2vocab.items():
            f.write(em+ "\n")
            # sort by count value
            wordcounts = {k: v for k, v in sorted(wordcounts.items(), key=lambda item: item[1],reverse=True)}
            for word,count in wordcounts.items():
                f.write(f"\t{word}:{count}\n")

def display_whole_dir(directory):
    """
    display all df present in a subdirectory of directory

    Args:
        directory (pathlib.Path): path to the directory
    """
    for path in directory.glob("**/[0-9]*.csv"):
        df = pd.read_csv(path)
        display(df)

def generate_production_format(path):
    """
    Generate the production format from a csv file/ a parent directory
    whose children contain csv files

    Args:
        path (pathlib.Path): path to the csv file/parent directory

    Return:
        [pd.Dataframe]: the equivalent df(s) in production format
    """
    if path.suffix == ".csv":
        dfs = [pd.read_csv(path)]
    else:
        dfs = []
        for path in path.glob("**/[0-9]*.csv"):
            form_id = int(path.stem)
            df = pd.read_csv(path)
            df['FormId'] = form_id
            df.rename(columns={'Worker ID':'WorkerId'},inplace=True)
            winfo_path = path.parent.joinpath("workers_info.csv")
            winfo = pd.read_csv(winfo_path)
            df = pd.merge(df,winfo,how='left',on=['WorkerId','FormId'])
            dfs.append(df)
        if len(dfs) == 0:
            raise ValueError(f"No .csv file was found in the subdirectories of {path}")

    selem2indx = pk.load(open(SELECTED_EMOJIS2INDEXES_PATH,"rb"))
    data = []
    for df in tqdm(dfs):
        em_cols = [col for col in df.columns if col in EMOJIS]
        honey_col_idx = len(em_cols) // 2
        assert(em_cols[honey_col_idx] in HONEYPOTS.keys())
        # get rid of the honeypot
        del em_cols[honey_col_idx]
        for _,row in df.iterrows():
            wid = row['WorkerId']
            formid = row['FormId']
            duration = row['AnswerDurationInSeconds']
            for em,word in row[em_cols].iteritems():
                # we add the selected emojis index
                emoji_index = selem2indx[em]
                data.append((wid,formid,duration,emoji_index,em,word))
    data = (pd.DataFrame(data,columns=['Worker ID','FormId','Duration','emoji_index','emoji','word'])
                .sort_values('emoji_index'))

    return data