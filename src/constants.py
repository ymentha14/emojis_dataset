from pathlib import Path
#################### Data Constants ####################
emotions_faces = ["😊","😴","🤓",
"😥","🤢","😰","🙂","😂","😖","😞","😧","😱","😔","😲","😳","😮",
"😋","😪","🤠","🙄","😄","😚","😷","😍","😟",
"😭","😃","😨","😐","🤣","😙","😝","😩","😓","🤔","😣","😘",
"😎","😇","😡","😢","🤑","😉","🤕","🤒","😅","🤐",
"🤧","😁","😬","😑","☹","👿","😤","😀","🙁","😯","😶","🤤","😦",
"😗","😒","😛","😕","😆","😏","😵","🤗","😌",
"😜","🤥","🙃","😠","😫","😈"]


#################### Path Constants ####################
REF_PATH = Path("/home/ymentha/Documents/Cours/dlab_project/emoji2vec_working/")
MAPPING_PATH = str(REF_PATH.joinpath('emoji_mapping.p'))
E2V_PATH = str(REF_PATH.joinpath("pre-trained/emoji2vec.bin"))
W2V_PATH = str(REF_PATH.joinpath('data/word2vec/GoogleNews-vectors-negative300.bin'))
DATA_PATH = str(REF_PATH.joinpath("data/raw_training_data/emoji_joined.txt"))
########################################################