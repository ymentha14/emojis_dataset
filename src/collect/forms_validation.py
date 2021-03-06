"""
Preprocessing functions preceding data gathering

Functions to ensure that the Google forms generated by the Appscript are well
formed and useable
"""

import pandas as pd
from src.constants import EMOJIS, HONEYPOTS, FORMS_RESULTS_DIR, EMOJI_2_TOP_INDEX_PATH
import pickle as pk


def quality_check(quality_check_dir):
    """
    Ensure that all forms are properly formed and displayed
    """
    paths = quality_check_dir.glob("[0-9]*.csv")
    paths = sorted(paths, key=lambda x: int(x.stem))
    em_retrieved = set()
    for path in paths:
        form_nmb = int(path.stem)
        df = pd.read_csv(path)
        cols = df.columns.tolist()
        assert cols[0] == "Timestamp"
        assert cols[1] == "WorkerID"
        assert cols[2] == "Age"
        assert cols[3] == "Gender"
        assert cols[4] == "Mothertongue"
        assert cols[-1] == "Feedback"

        start_idx = cols.index("Mothertongue") + 1
        end_idx = cols.index("Feedback")
        em_cols = cols[start_idx:end_idx]
        assert all([em in EMOJIS for em in em_cols])
        n = len(em_cols)
        honey_col_idx = n // 2 - (n + 1) % 2
        honey_em = em_cols[honey_col_idx]
        if honey_em not in HONEYPOTS.keys():
            raise ValueError(f"Emoji {honey_em} not in honey!")
        em_retrieved.update(em_cols)

    # check whether we covered all emojis
    selected_emojis = pk.load(open(EMOJI_2_TOP_INDEX_PATH, "rb"))
    selected_emojis = set(selected_emojis.keys())

    if selected_emojis != em_retrieved:
        raise ValueError(f"Missing emojis: {selected_emojis - em_retrieved} ")
    else:
        print(
            "Forms in right format: \n**All emojis are present\n**Honeypots well placed"
        )
