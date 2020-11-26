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
REF_PATH = Path("/home/ymentha/Documents/Cours/dlab_project/emoji2vec_working/")
MAPPING_PATH = str(REF_PATH.joinpath('emoji_mapping.p'))
E2V_PATH = str(REF_PATH.joinpath("pre-trained/emoji2vec.bin"))
W2V_PATH = str(REF_PATH.joinpath('data/word2vec/GoogleNews-vectors-negative300.bin'))
DATA_PATH = str(REF_PATH.joinpath("data/raw_training_data/emoji_joined.txt"))

REPO_PATH = Path("/home/ymentha/Documents/Cours/dlab_project/emojivec")
TWEET_PATH = REPO_PATH.joinpath("data/raw/tweets/big_tweet.csv")
TWEET_PATHS_PATH = REPO_PATH.joinpath("data/external/tweet_paths.pk")


# Credentials Directory
CREDS_PATH = REPO_PATH.joinpath("creds")
AWS_KEYS_PATH = CREDS_PATH.joinpath("aws.txt")  # keys for AWS
TOKEN_PATH = CREDS_PATH.joinpath("token.pk")  # token for drive API

# path to the downloaded urls form
URL_INDEX_PATH = REPO_PATH.joinpath("data/processed/auto_mturk/url_index.txt")
FORMS_RESULTS_DIR = REPO_PATH.joinpath("data/processed/auto_mturk/forms_results/")
HIT2FORM_PATH = REPO_PATH.joinpath("data/processed/auto_mturk/hit2form.pk")

# Em2Png
PNG_PATH = REPO_PATH.joinpath("data/processed/emojis_png/all/")

########################################################


# Honeypots
HONEYPOTS = {"☂️":["rain","umbrella"],
             "⭐":["star"],
             "☀️":["sun","sunny"],
             "🥝":["kiwi"],
             "🥜":["peanut","peanuts"],
             "🏀":["basket","basketball"],
             "🍐":["pear"],
             "🍑":["peach"],
             "🍒":["cherry"],
             "🥑":["avocado"],
             "🥒":["pickle"],
             "🥓":["bacon"],
             "🥕":["carrot"],
             "🍉":["watermelon"],
             "🍋":["lemon","lime"],
             "🍌":["banana"],
             "🍍":["ananas"],
             "🍎":["apple"],
             "🍓":["strawberry"],
             "🍔":["burger"],
             "🍕":["pizza"],
             "🍩":["donut","donuts"],
             "🍪":["cookie","cookies"],
             "™️":['tm'],
             "‼️":['surprised']
            }