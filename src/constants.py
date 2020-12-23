from pathlib import Path
import emoji

def get_fe0f_dict():
    """
    Compute a dict mapping every emoji to its "colored" fe0f version
    """
    emojis = {key:key for key in EMOJIS}
    for em in emojis.keys():
        if '\ufe0f' in em:
            short_em = "".join([char for char in em if char != '\ufe0f'])
            if short_em in emojis.keys():
                emojis[short_em] = em
            if em[-1] == '\ufe0f':
                short_em_end = em[:-1]
                if short_em_end in emojis:
                    emojis[short_em_end] = em
    assert(all([key in EMOJIS for key in emojis.keys()]))
    assert(all([key in EMOJIS for key in emojis.values()]))
    return emojis

EMOJIS = list(emoji.UNICODE_EMOJI.keys()) + ['⛩']
FE0F_DICT = get_fe0f_dict()

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


man_woman = ["🧑","👩","👨"]
em_letters = ['🇦', '🇧', '🇨', '🇩', '🇪', '🇫', '🇬', '🇭', '🇮', '🇯', '🇰',
              '🇱', '🇲', '🇳', '🇴', '🇵', '🇶', '🇷', '🇸', '🇹', '🇺', '🇻',
              '🇼', '🇽', '🇾', '🇿']
em_numbers = ["0️⃣","1️⃣","2️⃣","3️⃣","4️⃣","5️⃣","6️⃣","7️⃣","8️⃣","9️⃣",
              "8⃣","5⃣","4⃣","9⃣","1⃣","7⃣","6⃣","3⃣","2⃣","0⃣"]
em_hours = ["🕐","🕑","🕒","🕓","🕔","🕕","🕖","🕗","🕘","🕙","🕚","🕛","🕜","🕝","🕞","🕟","🕠","🕡","🕢","🕣","🕤","🕥","🕦","🕧"]
flags = ["🇦🇨","🇦🇩","🇦🇪","🇦🇫","🇦🇬","🇦🇮","🇦🇱","🇦🇲","🇦🇴","🇦🇶","🇦🇷","🇦🇸","🇦🇹",
"🇦🇺","🇦🇼","🇦🇽","🇦🇿","🇧🇦","🇧🇧","🇧🇩","🇧🇪","🇧🇫","🇧🇬","🇧🇭","🇧🇮","🇧🇯","🇧🇱","🇧🇲",
"🇧🇳","🇧🇴","🇧🇶","🇧🇷","🇧🇸","🇧🇹","🇧🇻","🇧🇼","🇧🇾","🇧🇿","🇨🇦","🇨🇨","🇨🇩","🇨🇫","🇨🇬",
"🇨🇭","🇨🇮","🇨🇰","🇨🇱","🇨🇲","🇨🇳","🇨🇴","🇨🇵","🇨🇷","🇨🇺","🇨🇻","🇨🇼","🇨🇽","🇨🇾","🇨🇿",
"🇩🇪","🇩🇬","🇩🇯","🇩🇰","🇩🇲","🇩🇴","🇩🇿","🇪🇦","🇪🇨","🇪🇪","🇪🇬","🇪🇭","🇪🇷","🇪🇸","🇪🇹",
"🇪🇺","🇫🇮","🇫🇯","🇫🇰","🇫🇲","🇫🇴","🇫🇷","🇬🇦","🇬🇧","🇬🇩","🇬🇪","🇬🇫","🇬🇬","🇬🇭","🇬🇮",
"🇬🇱","🇬🇲","🇬🇳","🇬🇵","🇬🇶","🇬🇷","🇬🇸","🇬🇹","🇬🇺","🇬🇼","🇬🇾","🇭🇰","🇭🇲","🇭🇳",
"🇭🇷","🇭🇹","🇭🇺","🇮🇨","🇮🇩","🇮🇪","🇮🇱","🇮🇲","🇮🇳","🇮🇴","🇮🇶","🇮🇷","🇮🇸","🇮🇹","🇯🇪",
"🇯🇲","🇯🇴","🇯🇵","🇰🇪","🇰🇬","🇰🇭","🇰🇮","🇰🇲","🇰🇳","🇰🇵","🇰🇷","🇰🇼","🇰🇾","🇰🇿",
"🇱🇦","🇱🇧","🇱🇨","🇱🇮","🇱🇰","🇱🇷","🇱🇸","🇱🇹","🇱🇺","🇱🇻","🇱🇾","🇲🇦","🇲🇨","🇲🇩",
"🇲🇪","🇲🇫","🇲🇬","🇲🇭","🇲🇰","🇲🇱","🇲🇲","🇲🇳","🇲🇴","🇲🇵","🇲🇶","🇲🇷","🇲🇸",
"🇲🇹","🇲🇺","🇲🇻","🇲🇼","🇲🇽","🇲🇾","🇲🇿","🇳🇦","🇳🇨","🇳🇪","🇳🇫","🇳🇬","🇳🇮",
"🇳🇱","🇳🇴","🇳🇵","🇳🇷","🇳🇺","🇳🇿","🇴🇲","🇵🇦","🇵🇪","🇵🇫","🇵🇬","🇵🇭","🇵🇰","🇵🇱",
"🇵🇲","🇵🇳","🇵🇷","🇵🇸","🇵🇹","🇵🇼","🇵🇾","🇶🇦","🇷🇪","🇷🇴","🇷🇸","🇷🇺","🇷🇼","🇸🇦",
"🇸🇧","🇸🇨","🇸🇩","🇸🇪","🇸🇬","🇸🇭","🇸🇮","🇸🇯","🇸🇰","🇸🇱","🇸🇲","🇸🇳","🇸🇴","🇸🇷","🇸🇸",
"🇸🇹","🇸🇻","🇸🇽","🇸🇾","🇸🇿","🇹🇦","🇹🇨","🇹🇩","🇹🇫","🇹🇬","🇹🇭","🇹🇯","🇹🇰","🇹🇱","🇹🇲",
"🇹🇳","🇹🇴","🇹🇷","🇹🇹","🇹🇻","🇹🇼","🇹🇿","🇺🇦","🇺🇬","🇺🇲","🇺🇳","🇺🇸","🇺🇾","🇺🇿",
"🇻🇦","🇻🇨","🇻🇪","🇻🇬","🇻🇮","🇻🇳","🇻🇺","🇼🇫","🇼🇸","🇽🇰","🇾🇪","🇾🇹","🇿🇦","🇿🇲","🇿🇼",
"🎌","🏁","🏳","🏳‍🌈","🏴","🏴‍☠","🚩"]

skin_tones = ["🏻","🏼","🏽","🏾","🏿"]
sex_symbols = ["\u2640","\u2642","\u2640\ufe0f","\u2642\ufe0f"]


#################### Path Constants ####################
REF_PATH = Path("/home/ymentha/Documents/Cours/dlab_project/emoji_dataset/emoji2vec/emoji2vec/")
MAPPING_PATH = str(REF_PATH.joinpath('emoji_mapping.p'))
E2V_PATH = str(REF_PATH.joinpath("pre-trained/emoji2vec.bin"))
W2V_PATH = str(REF_PATH.joinpath('data/word2vec/GoogleNews-vectors-negative300.bin'))
DATA_PATH = str(REF_PATH.joinpath("data/raw_training_data/emoji_joined.txt"))

REPO_PATH = Path("/home/ymentha/Documents/Cours/dlab_project/emoji_dataset")
if not REPO_PATH.exists():
    REPO_PATH = Path("/home/ymentha/emojivec")


############################## MT2GF ##############################

# Drive id of the gmap object
GMAP_DRIVE_ID = "1o_7rRLn48ZRHlo0x_8gNILbae_4q-DbB1WneuKaRFI0"
GFORM_MAP_PATH = REPO_PATH.joinpath("data/raw/forms/dataset/gform_map.txt")

# QualityCheck Directory
QUALITY_CHECK_DIR = REPO_PATH.joinpath("data//mt2gf_cache/quality_check")

# Credentials Directory
CREDS_PATH = REPO_PATH.joinpath("creds")
AWS_KEYS_PATH = CREDS_PATH.joinpath("aws.txt")  # keys for AWS
TOKEN_PATH = CREDS_PATH.joinpath("token.pk")  # token for drive API

# Path to the downloaded urls form
# FORMS_RESULTS_DIR = REPO_PATH.joinpath("data/raw/forms/dataset") # real dataset path
FORMS_RESULTS_DIR = REPO_PATH.joinpath("data/raw/forms/pilots/test_runs")

if not FORMS_RESULTS_DIR.exists():
    FORMS_RESULTS_DIR = REPO_PATH.joinpath("data/processed/auto_mturk/forms_results/")
WATCHER_FORMS_RESULTS_DIR = REPO_PATH.joinpath("data/mt2gf_cache/watcher")
HIT2FORM_PATH_SANDBOX = REPO_PATH.joinpath("data/processed/auto_mturk/hit2formsandbox.pk")
HIT2FORM_PATH = REPO_PATH.joinpath("data/processed/auto_mturk/hit2form.pk")
LOG_FORMS_RESULTS_DIR = REPO_PATH.joinpath("data/processed/auto_mturk/forms_log_results")
##################################################################






# Em2Png

PNG_DIR = REPO_PATH.joinpath("data/raw/emojis_png/")

# Extracted images for all emojis
PNG_PATH = PNG_DIR.joinpath("all")
# List of selected emojis for dataset collection
SELECTED_EMOJIS_PATH = PNG_DIR.joinpath("pickles/selected_emojis.pk")
# Mapping of all emojis to a global index
EMOJI_2_GLOBAL_INDEX_PATH = PNG_DIR.joinpath("pickles/emojis_2_global_index.pk")
# Global indexes of selected emojis for dataset collection
SELECTED_GLOBAL_INDEXES_PATH = PNG_DIR.joinpath("pickles/selected_global_indexes.pk")
# Mapping of selected emojis to a selected index
EMOJI_2_TOP_INDEX_PATH = PNG_DIR.joinpath("pickles/emojis_2_top_indexes.pk")
########################################################

# Tweeter Data
TWEET_DIR = REPO_PATH.joinpath("data/raw/tweets/")
# Directory where to find all the tweeter samples
TWEET_SAMPLES_DIR = Path("/dlabdata1/gligoric/spritzer/tweets_pritzer_sample/")
TWEET_EM_COUNT_PATH = TWEET_DIR.joinpath("em_counts.csv")
TWEET_PATH = TWEET_DIR.joinpath("tweet_600.csv")
TWEET_PATHS_PATH = REPO_PATH.joinpath("data/external/tweet_paths.pk")


# Google Forms Data
FORMS_DIR = REPO_PATH.joinpath("data/raw/forms")
PILOTS_DIR = FORMS_DIR.joinpath("pilots")
PILOT_0_DIR = PILOTS_DIR.joinpath("0_emoji10")
PILOT_1_DIR = PILOTS_DIR.joinpath("1_asymptotic")


# AutoMTurk
NMB_FORMS_THRESHOLD = 2

# Honeypots
HONEYPOTS = {"☂️":["rain","umbrella"],
             "⭐":["star"],
             "☀️":["sun","sunny"],
             "🥜":["peanut","peanuts","nut"],
             "🏀":["basket","basketball","ball"],
             "🍑":["peach"],
             "🍒":["cherry","cherries"],
             "🥑":["avocado"],
             "🥒":["pickle","cucumber"],
             "🥕":["carrot"],
             "🦆":["duck","penguin"],
             "🍉":["watermelon","melon"],
             "🍋":["lemon","lime","mango"],
             "🍌":["banana"],
             "🍍":["ananas"],
             "🍎":["apple"],
             "🍓":["strawberry"],
             "🍔":["burger","hamburger"],
             "🍕":["pizza"],
             "🍩":["donut","donuts"],
             "🍪":["cookie","cookies","biscuit"]
            }