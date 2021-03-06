from pathlib import Path
import emoji
import os


def get_fe0f_dict():
    """
    Compute a dict mapping every emoji to its "colored" fe0f version
    """
    emojis = {key: key for key in EMOJIS}
    for em in emojis.keys():
        if "\ufe0f" in em:
            short_em = "".join([char for char in em if char != "\ufe0f"])
            if short_em in emojis.keys():
                emojis[short_em] = em
            if em[-1] == "\ufe0f":
                short_em_end = em[:-1]
                if short_em_end in emojis:
                    emojis[short_em_end] = em
    assert all([key in EMOJIS for key in emojis.keys()])
    assert all([key in EMOJIS for key in emojis.values()])
    return emojis


EMOJIS = list(emoji.UNICODE_EMOJI.keys()) + ["⛩"]
FE0F_DICT = get_fe0f_dict()


# Honeypots
HONEYPOTS = {
    "☂️": ["rain", "umbrella", "weather"],
    "⭐": [
        "star",
        "superstar",
        "excellent",
        "success",
        "awesome",
        "best",
        "christmas",
        "shining",
        "winner",
    ],
    "☀️": [
        "sun",
        "sunny",
        "bright",
        "brightness",
        "daylight",
        "shine",
        "shining",
        "sunlight",
        "sunshine",
    ],
    "🥜": ["peanut", "peanuts", "nut", "groundnut", "food"],
    "🏀": ["basket", "basketball", "ball", "sport"],
    "🍑": ["peach", "fruit", "apple", "apricot", "berry", "fresh", "ripe"],
    "🍒": ["cherry", "cherries", "fruit"],
    "🥑": ["avocado", "guacamole", "vegetable"],
    "🥒": ["pickle", "cucumber", "vegetable"],
    "🥕": ["carrot"],
    "🦆": ["duck", "penguin"],
    "🍉": ["watermelon", "melon"],
    "🍋": ["lemon", "lime", "mango", "lemonade"],
    "🍌": ["banana", "potassium"],
    "🍍": ["ananas", "pineapple"],
    "🍎": ["apple", "fruit", "health"],
    "🍓": ["strawberry", "strawberries"],
    "🍔": ["burger", "hamburger", "cheeseburger", "food"],
    "🍕": ["pizza", "food"],
    "🍩": ["donut", "donuts", "doughnut", "sweet"],
    "🍪": ["cookie", "cookies", "biscuit", "dessert"],
}

#################### Plots ####################
COLOR1 = "#549aab"
COLOR2 = "#d03161"
COLOR3 = "#f6a90f"
COLOR4 = "#8359a3"
COLOR_TRUE = "#549aab"
COLOR_FRAUD = "#d03161"
COLOR_PLOT = "#50C878"
#################### Data Constants ####################
emotions_faces = [
    "😊",
    "😴",
    "🤓",
    "😥",
    "🤢",
    "😰",
    "🙂",
    "😂",
    "😖",
    "😞",
    "😧",
    "😱",
    "😔",
    "😲",
    "😳",
    "😮",
    "😋",
    "😪",
    "🤠",
    "🙄",
    "😄",
    "😚",
    "😷",
    "😍",
    "😟",
    "😭",
    "😃",
    "😨",
    "😐",
    "🤣",
    "😙",
    "😝",
    "😩",
    "😓",
    "🤔",
    "😣",
    "😘",
    "😎",
    "😇",
    "😡",
    "😢",
    "🤑",
    "😉",
    "🤕",
    "🤒",
    "😅",
    "🤐",
    "🤧",
    "😁",
    "😬",
    "😑",
    "☹",
    "👿",
    "😤",
    "😀",
    "🙁",
    "😯",
    "😶",
    "🤤",
    "😦",
    "😗",
    "😒",
    "😛",
    "😕",
    "😆",
    "😏",
    "😵",
    "🤗",
    "😌",
    "😜",
    "🤥",
    "🙃",
    "😠",
    "😫",
    "😈",
]


man_woman = ["🧑", "👩", "👨"]
em_letters = [
    "🇦",
    "🇧",
    "🇨",
    "🇩",
    "🇪",
    "🇫",
    "🇬",
    "🇭",
    "🇮",
    "🇯",
    "🇰",
    "🇱",
    "🇲",
    "🇳",
    "🇴",
    "🇵",
    "🇶",
    "🇷",
    "🇸",
    "🇹",
    "🇺",
    "🇻",
    "🇼",
    "🇽",
    "🇾",
    "🇿",
]
em_numbers = [
    "0️⃣",
    "1️⃣",
    "2️⃣",
    "3️⃣",
    "4️⃣",
    "5️⃣",
    "6️⃣",
    "7️⃣",
    "8️⃣",
    "9️⃣",
    "8⃣",
    "5⃣",
    "4⃣",
    "9⃣",
    "1⃣",
    "7⃣",
    "6⃣",
    "3⃣",
    "2⃣",
    "0⃣",
]
em_hours = [
    "🕐",
    "🕑",
    "🕒",
    "🕓",
    "🕔",
    "🕕",
    "🕖",
    "🕗",
    "🕘",
    "🕙",
    "🕚",
    "🕛",
    "🕜",
    "🕝",
    "🕞",
    "🕟",
    "🕠",
    "🕡",
    "🕢",
    "🕣",
    "🕤",
    "🕥",
    "🕦",
    "🕧",
]
flags = [
    "🇦🇨",
    "🇦🇩",
    "🇦🇪",
    "🇦🇫",
    "🇦🇬",
    "🇦🇮",
    "🇦🇱",
    "🇦🇲",
    "🇦🇴",
    "🇦🇶",
    "🇦🇷",
    "🇦🇸",
    "🇦🇹",
    "🇦🇺",
    "🇦🇼",
    "🇦🇽",
    "🇦🇿",
    "🇧🇦",
    "🇧🇧",
    "🇧🇩",
    "🇧🇪",
    "🇧🇫",
    "🇧🇬",
    "🇧🇭",
    "🇧🇮",
    "🇧🇯",
    "🇧🇱",
    "🇧🇲",
    "🇧🇳",
    "🇧🇴",
    "🇧🇶",
    "🇧🇷",
    "🇧🇸",
    "🇧🇹",
    "🇧🇻",
    "🇧🇼",
    "🇧🇾",
    "🇧🇿",
    "🇨🇦",
    "🇨🇨",
    "🇨🇩",
    "🇨🇫",
    "🇨🇬",
    "🇨🇭",
    "🇨🇮",
    "🇨🇰",
    "🇨🇱",
    "🇨🇲",
    "🇨🇳",
    "🇨🇴",
    "🇨🇵",
    "🇨🇷",
    "🇨🇺",
    "🇨🇻",
    "🇨🇼",
    "🇨🇽",
    "🇨🇾",
    "🇨🇿",
    "🇩🇪",
    "🇩🇬",
    "🇩🇯",
    "🇩🇰",
    "🇩🇲",
    "🇩🇴",
    "🇩🇿",
    "🇪🇦",
    "🇪🇨",
    "🇪🇪",
    "🇪🇬",
    "🇪🇭",
    "🇪🇷",
    "🇪🇸",
    "🇪🇹",
    "🇪🇺",
    "🇫🇮",
    "🇫🇯",
    "🇫🇰",
    "🇫🇲",
    "🇫🇴",
    "🇫🇷",
    "🇬🇦",
    "🇬🇧",
    "🇬🇩",
    "🇬🇪",
    "🇬🇫",
    "🇬🇬",
    "🇬🇭",
    "🇬🇮",
    "🇬🇱",
    "🇬🇲",
    "🇬🇳",
    "🇬🇵",
    "🇬🇶",
    "🇬🇷",
    "🇬🇸",
    "🇬🇹",
    "🇬🇺",
    "🇬🇼",
    "🇬🇾",
    "🇭🇰",
    "🇭🇲",
    "🇭🇳",
    "🇭🇷",
    "🇭🇹",
    "🇭🇺",
    "🇮🇨",
    "🇮🇩",
    "🇮🇪",
    "🇮🇱",
    "🇮🇲",
    "🇮🇳",
    "🇮🇴",
    "🇮🇶",
    "🇮🇷",
    "🇮🇸",
    "🇮🇹",
    "🇯🇪",
    "🇯🇲",
    "🇯🇴",
    "🇯🇵",
    "🇰🇪",
    "🇰🇬",
    "🇰🇭",
    "🇰🇮",
    "🇰🇲",
    "🇰🇳",
    "🇰🇵",
    "🇰🇷",
    "🇰🇼",
    "🇰🇾",
    "🇰🇿",
    "🇱🇦",
    "🇱🇧",
    "🇱🇨",
    "🇱🇮",
    "🇱🇰",
    "🇱🇷",
    "🇱🇸",
    "🇱🇹",
    "🇱🇺",
    "🇱🇻",
    "🇱🇾",
    "🇲🇦",
    "🇲🇨",
    "🇲🇩",
    "🇲🇪",
    "🇲🇫",
    "🇲🇬",
    "🇲🇭",
    "🇲🇰",
    "🇲🇱",
    "🇲🇲",
    "🇲🇳",
    "🇲🇴",
    "🇲🇵",
    "🇲🇶",
    "🇲🇷",
    "🇲🇸",
    "🇲🇹",
    "🇲🇺",
    "🇲🇻",
    "🇲🇼",
    "🇲🇽",
    "🇲🇾",
    "🇲🇿",
    "🇳🇦",
    "🇳🇨",
    "🇳🇪",
    "🇳🇫",
    "🇳🇬",
    "🇳🇮",
    "🇳🇱",
    "🇳🇴",
    "🇳🇵",
    "🇳🇷",
    "🇳🇺",
    "🇳🇿",
    "🇴🇲",
    "🇵🇦",
    "🇵🇪",
    "🇵🇫",
    "🇵🇬",
    "🇵🇭",
    "🇵🇰",
    "🇵🇱",
    "🇵🇲",
    "🇵🇳",
    "🇵🇷",
    "🇵🇸",
    "🇵🇹",
    "🇵🇼",
    "🇵🇾",
    "🇶🇦",
    "🇷🇪",
    "🇷🇴",
    "🇷🇸",
    "🇷🇺",
    "🇷🇼",
    "🇸🇦",
    "🇸🇧",
    "🇸🇨",
    "🇸🇩",
    "🇸🇪",
    "🇸🇬",
    "🇸🇭",
    "🇸🇮",
    "🇸🇯",
    "🇸🇰",
    "🇸🇱",
    "🇸🇲",
    "🇸🇳",
    "🇸🇴",
    "🇸🇷",
    "🇸🇸",
    "🇸🇹",
    "🇸🇻",
    "🇸🇽",
    "🇸🇾",
    "🇸🇿",
    "🇹🇦",
    "🇹🇨",
    "🇹🇩",
    "🇹🇫",
    "🇹🇬",
    "🇹🇭",
    "🇹🇯",
    "🇹🇰",
    "🇹🇱",
    "🇹🇲",
    "🇹🇳",
    "🇹🇴",
    "🇹🇷",
    "🇹🇹",
    "🇹🇻",
    "🇹🇼",
    "🇹🇿",
    "🇺🇦",
    "🇺🇬",
    "🇺🇲",
    "🇺🇳",
    "🇺🇸",
    "🇺🇾",
    "🇺🇿",
    "🇻🇦",
    "🇻🇨",
    "🇻🇪",
    "🇻🇬",
    "🇻🇮",
    "🇻🇳",
    "🇻🇺",
    "🇼🇫",
    "🇼🇸",
    "🇽🇰",
    "🇾🇪",
    "🇾🇹",
    "🇿🇦",
    "🇿🇲",
    "🇿🇼",
    "🎌",
    "🏁",
    "🏳",
    "🏳‍🌈",
    "🏴",
    "🏴‍☠",
    "🚩",
]

skin_tones = ["🏻", "🏼", "🏽", "🏾", "🏿"]
sex_symbols = ["\u2640", "\u2642", "\u2640\ufe0f", "\u2642\ufe0f"]


#################### Path Constants ####################
REPO_PATH = Path(
    os.getenv("REPO_DIR", "/home/ymentha/Documents/Cours/dlab_project/emoji_dataset")
)
E2V_REPO_PATH = REPO_PATH.joinpath("emoji2vec/emoji2vec/")
E2V_MODEL_PATH = str(E2V_REPO_PATH.joinpath("pre-trained/emoji2vec.bin"))
E2V_DATA_DIR = REPO_PATH.joinpath("data/raw/e2v")
E2V_MAPPING_PATH = str(E2V_DATA_DIR.joinpath("word2vec/emoji_mapping.p"))
W2V_PATH = str(E2V_DATA_DIR.joinpath(
    "word2vec/GoogleNews-vectors-negative300.bin"))
E2V_DATA_PATH = str(E2V_DATA_DIR.joinpath(
    "raw_training_data/emoji_joined.txt"))


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

# Directory where to download the data from the forms
FORMS_RESULTS_DIR = REPO_PATH.joinpath("data/raw/forms/pilots/test_runs")
# Directory where the watcher can store the downloaded csv files
WATCHER_FORMS_RESULTS_DIR = REPO_PATH.joinpath("data/mt2gf_cache/watcher")
##################################################################

# Em2Png
PNG_DIR = REPO_PATH.joinpath("data/raw/emojis_png/")

# Extracted images for all emojis
PNG_PATH = PNG_DIR.joinpath("all")
# List of selected emojis for dataset collection
SELECTED_EMOJIS_PATH = PNG_DIR.joinpath("pickles/selected_emojis.pk")
# Mapping of all emojis to a global index
EMOJI_2_GLOBAL_INDEX_PATH = PNG_DIR.joinpath(
    "pickles/emojis_2_global_index.pk")
# Global indexes of selected emojis for dataset collection
SELECTED_GLOBAL_INDEXES_PATH = PNG_DIR.joinpath(
    "pickles/selected_global_indexes.pk")
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


# Dataset Analysis
# Path to the raw data of the collected emoji dataset
EMOJI_DATASET_DIR = REPO_PATH.joinpath("data/raw/forms/dataset")
# training data formatted for w2v embeddings
EMBEDDING_TRAINING_DATA_DIR = REPO_PATH.joinpath(
    "data/processed/embed_training")
EM_VOC_COUNT = REPO_PATH.joinpath("data/processed/dataset/stats/em_voc.txt")
# List of languages from http://www2.harpercollege.edu/mhealy/g101ilec/intro/clt/cltclt/top100.html
LANGUAGES_PATH = REPO_PATH.joinpath("data/external/languages.csv")
EXPORT_DIR = REPO_PATH.joinpath("results")

# TSNE Results
EMOJI_FONT_PATH = REPO_PATH.joinpath("data/external/Apple Color Emoji.ttf")
TITLE_SIZE = 23
LABEL_SIZE = 19
