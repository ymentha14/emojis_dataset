"""
Preprocessing functions before mturk data gathering
"""
import pandas as pd
from src.constants import EMOJIS,HONEYPOTS,FORMS_RESULTS_DIR,SELECTED_EMOJIS2INDEXES_PATH
import pickle as pk


def batchnumber2formidxes(batch_number,batch_size):
    """
    Convert a batch number to its respective form indexes
    """
    start_idx = batch_number * batch_size
    forms_idxes = list(range(start_idx,start_idx+batch_size))
    return forms_idxes

def check_previous_batches(recent_batch_number,parent_dir,MaxAssignments,batch_size):
    """
    Check the number of files and their size in all previous batches up to 
    current batch

    Args:
        recent_bach_number (int): most recent batch (not included)
        parent_dir (pathlib.Path): parent directory in containing the batches
        MaxAssignments (int): number of rows expected
        batch_size (int): number of files expected per batch
    """
    # we check up to the most recent batch
    for batch_number in range(recent_batch_number):
        batch_path = parent_dir.joinpath(str(batch_number))
        valid,msg = check_is_complete(batch_path,MaxAssignments,batch_size)
        if not valid:
            raise ValueError(msg)
    print(f"All batches clean up to batch {recent_batch_number}")

def check_is_complete(batch_path,MaxAssignments,batch_size):
    """
    check that the batch present at batch_path follows our guidelines
    (has batch_size files and  each file has MaxAssignments rows)
    """
    # form indexes we expect in this batch
    batch_number = int(batch_path.stem)

    form_idxes = batchnumber2formidxes(batch_number,batch_size)
    # extract the paths to the form files
    form_paths = [path for path in batch_path.glob("[0-9]*.csv")]

    # check for expected number of files
    if len(form_paths) != batch_size:
        raise ValueError(f"Problem of downloading: unexpected number of csv files in batch {batch_number}")

    for form_path in form_paths:
        form_idx = form_path.stem

        # check the files are at the correct place
        if int(form_idx) not in form_idxes:
            raise ValueError(f"Form index {form_idx} should not be present in batch {batch_number}")
        df = pd.read_csv(form_path)
        # check the files have the correct number of row
        if df.shape[0] < MaxAssignments:
            return False,f"Form {form_idx} in batch {batch_number} is missing some entries."
    return True,""

def get_batch_indexes(parent_dir,batch_number=None,batch_size=7,MaxAssignments=30):
    """
    Function to batch formidx2gid and formidx2url

    Args:
        batch_size(int): number of forms per batch
        batch_number(int): number of the batch to get indexes for

    Return:
        [list of int]: indexes of the forms to run the analysis for
    """
    if batch_number is None:
        batch_paths = [path.parent for path in FORMS_RESULTS_DIR.glob("**/[0-9]*.csv")]
        if len(batch_paths) == 0:
            batch_number = 0
        else:
            recent_batch_dir = max(batch_paths,key = lambda x:int(x.stem))
            recent_batch_number = int(recent_batch_dir.stem)
            check_previous_batches(recent_batch_number,parent_dir,MaxAssignments,batch_size)

            complete,_ = check_is_complete(recent_batch_dir,MaxAssignments,batch_size)
            if complete:
                batch_number = recent_batch_number + 1
            else:
                print("Resuming previous incomplete batch")
                batch_number = recent_batch_number
    form_idxes = batchnumber2formidxes(batch_number,batch_size)
    batch_dir = parent_dir.joinpath(str(batch_number))
    return batch_dir, batch_number, form_idxes

def quality_check(quality_check_dir):
    """
    Ensure that all forms are properly formed and displayed
    """
    paths = quality_check_dir.glob("[0-9]*.csv")
    paths = sorted(paths,key = lambda x: int(x.stem))
    em_retrieved = set()
    for path in paths:
        form_nmb = int(path.stem)
        df = pd.read_csv(path)
        cols = df.columns.tolist()
        assert(cols[0] == "Timestamp")
        assert(cols[1] == "Worker ID")
        assert(cols[2] == "Age")
        assert(cols[3] == "Gender")
        assert(cols[4] == "Mothertongue")
        assert(cols[-1] == "Feedback")


        start_idx = cols.index("Mothertongue") + 1
        end_idx = cols.index("Feedback")
        em_cols = cols[start_idx:end_idx]
        assert(all([em in EMOJIS for em in em_cols]))
        n = len(em_cols)
        honey_col_idx =  n // 2 - (n+1)%2
        honey_em = em_cols[honey_col_idx]
        if honey_em not in HONEYPOTS.keys():
            raise ValueError(f"Emoji {honey_em} not in honey!")
        em_retrieved.update(em_cols)

    # check whether we covered all emojis
    selected_emojis = pk.load(open(SELECTED_EMOJIS2INDEXES_PATH,"rb"))
    selected_emojis = set(selected_emojis.keys())

    if selected_emojis != em_retrieved:
        raise ValueError(f"Missing emojis: {selected_emojis - em_retrieved} ")
    else:
        print("All emojis are present")