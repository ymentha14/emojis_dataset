from pathlib import Path
#################### Plots ####################
COLOR_TRUE = '#549aab'
COLOR_FRAUD = '#d03161'
COLOR_PLOT ='#50C878'
#################### Data Constants ####################
emotions_faces = ["😊","😴","🤓",
"😥","🤢","😰","🙂","😂","😖","😞","😧","😱","😔","😲","😳","😮",
"😋","😪","🤠","🙄","😄","😚","😷","😍","😟",
"😭","😃","😨","😐","🤣","😙","😝","😩","😓","🤔","😣","😘",
"😎","😇","😡","😢","🤑","😉","🤕","🤒","😅","🤐",
"🤧","😁","😬","😑","☹","👿","😤","😀","🙁","😯","😶","🤤","😦",
"😗","😒","😛","😕","😆","😏","😵","🤗","😌",
"😜","🤥","🙃","😠","😫","😈"]

skin_tones = ["🏻","🏼","🏽","🏾","🏿"]


#################### Path Constants ####################
REF_PATH = Path("/home/ymentha/Documents/Cours/dlab_project/emoji2vec_working/")
MAPPING_PATH = str(REF_PATH.joinpath('emoji_mapping.p'))
E2V_PATH = str(REF_PATH.joinpath("pre-trained/emoji2vec.bin"))
W2V_PATH = str(REF_PATH.joinpath('data/word2vec/GoogleNews-vectors-negative300.bin'))
DATA_PATH = str(REF_PATH.joinpath("data/raw_training_data/emoji_joined.txt"))
TWEET_PATH = "/home/ymentha/emojivec/data/raw/tweets/big_tweet.csv"
TWEET_PATHS_PATH = "/home/ymentha/emojivec/data/external/tweet_paths.pk"
########################################################