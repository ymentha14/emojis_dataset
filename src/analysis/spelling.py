from nltk.corpus import brown
import pkg_resources
from symspellpy import SymSpell, Verbosity
from collections import Counter
import numpy as np
import torch
from transformers import AutoTokenizer, BertForMaskedLM
from tqdm import tqdm
import logging
logging.getLogger("transformers").setLevel(logging.ERROR)
import enchant
import operator
from pdb import set_trace


class WordSuggester:
    """
    Suggest words when the input is mispelled
    """

    def __init__(
        self,
    ):
        print("Initializing the vocabulary set..")
        #self.word_set = set(brown.words())
        self.d = enchant.Dict("en_US")
        print("Initializing BERT pipeline..")

        self.tok = AutoTokenizer.from_pretrained("bert-base-uncased")
        self.bert = BertForMaskedLM.from_pretrained("bert-base-uncased")
        self.sym_spell = SymSpell(max_dictionary_edit_distance=2, prefix_length=7)
        self.sym_spell_cut = SymSpell(max_dictionary_edit_distance=0, prefix_length=7)
        dictionary_path = pkg_resources.resource_filename(
            "symspellpy", "frequency_dictionary_en_82_765.txt"
        )
        # term_index is the column of the term and count_index is the
        # column of the term frequency
        self.sym_spell.load_dictionary(dictionary_path, term_index=0, count_index=1)
        self.sym_spell_cut.load_dictionary(dictionary_path, term_index=0, count_index=1)

    def cross_word_validate(self, word, word_counts, min_counts=2):
        """
        A word is considered valid if it occures many times or
        """
        tot = sum(word_counts.values())
        return word_counts[word] >= min_counts

    def is_multiword(self,word):
        suggestions = self.d.suggest(word)
        for sugg in suggestions:
            if "".join(sugg.split(" ")) == word:
                return True,sugg
            if "".join(sugg.split("-")) == word:
                return True,sugg.replace("-"," ")
        return False,""

    def cross_sugg_validate(self,word,word_counts):
        suggestions = [s.term for s in self.sym_spell.lookup(
            word, Verbosity.CLOSEST, max_edit_distance=2
        )]
        present_words = {word:count for word,count in word_counts.items() if word in suggestions}
        if len(present_words) == 0:
            return False,""
        corr_word = max(present_words.items(), key=operator.itemgetter(1))[0]
        return True,corr_word
    def get_word_suggestions(self, word, word_counts):
        """
        Return the suggestions for the word passed in parameter. If the
        word passed in parameter is valid, return a list of len 1 with the
        word inside.

        Args:
            word (str): the word to find suggestions for
            word_counts (dict): value counts of word for a given emoji (context)
        """
        # if the word appears many times we keep it
        if self.cross_word_validate(word, word_counts):
            return {"status": "present", "words": [word]}

        # if the word is part of the vocabulary we keep it
        if self.d.check(word):
            return {"status": "exist", "words": [word]}

        cross_sugg,corr_word = self.cross_sugg_validate(word,word_counts)
        if cross_sugg:
            return {"status": "cross_suggested", "words": [corr_word]}

        # if it is a combinaison of many words
        result = self.sym_spell_cut.word_segmentation(word)
        log_confidence = result.log_prob_sum / len(result.corrected_string)
        if log_confidence > -1:
            suggestions = result.corrected_string
            return {"status": "disassembled1", "words": [result.corrected_string]}

        # if combination of many words
        is_multi,corr_word = self.is_multiword(word)
        if is_multi:
            return {"status": "disassembled2", "words": [corr_word]}

        # otherwise we correct it
        suggestions = self.sym_spell.lookup(
            word, Verbosity.CLOSEST, max_edit_distance=2
        )
        # display suggestion term, term frequency, and edit distance
        if len(suggestions) == 0:
            return {"status": "notfound", "words": [word]}
        return {"status": "corrected", "words": [sugg.term for sugg in suggestions]}

    def get_context_suggestions(self, word_list):
        """
        Applies get_word_suggestions for every word of an emoji's vocabulary (context)

        Args:
            word_list (list of str): words to describe the emoji

        Returns:
            [list of list of str]: list of suggestions: each word receives suggestions (list of str)
        """
        word_counts = Counter(word_list)
        context_suggestions = [
            self.get_word_suggestions(word, word_counts) for word in word_list
        ]
        return context_suggestions

    def find_best_word(self, context, suggestions):
        """
        Find the most appropriate word in suggestions given the context

        Args:
            context (list of str): words defining the context
            suggestions (list of str): suggestions for the word to find

        Returns:
            [str]: the word of suggestions that matches the best the context
            according to BERT output
        """
        # We place the word of interest in the middle of the context
        n = len(context) // 2
        pre_context = " ".join(context[:n])
        post_context = " ".join(context[n:])
        sentence = f"{pre_context} {self.tok.mask_token} {post_context}"

        input_tokens = self.tok.encode(sentence)
        answer_pos = input_tokens.index(self.tok.mask_token_id)

        logits = self.bert(torch.tensor([input_tokens]))[0][0]
        logits = logits[answer_pos]
        suggestions_tokens = [self.tok.encode(word)[1:-1] for word in suggestions]
        scores = [
            np.mean([logits[i].item() for i in tokens]) for tokens in suggestions_tokens
        ]
        best_sugg_idx = np.argmax(scores)
        return suggestions[best_sugg_idx]

    def extract_context_suggestions(self, context_suggestions):
        """
        Extract best words for each suggestions in the context suggestions

        Args:
            context_suggestions (list of list of str): list of suggestions

        Returns:
            [list of str]: most appropriate words

        """
        # we don't need the status in the current function
        context_suggestions = [sugg["words"] for sugg in context_suggestions]
        ret_words = []
        for suggestions in context_suggestions:
            # single suggestion: the word is not ambiguous
            if len(suggestions) == 1:
                ret_words.append(suggestions[0])
            else:
                # we gather the single words considered as healthy
                context = [
                    word_list[0]
                    for word_list in context_suggestions
                    if word_list != suggestions and len(word_list) == 1
                ]
                word = self.find_best_word(context, suggestions)

                ret_words.append(word)
        return ret_words

    def process_context(self, context, verbose=False):
        """
        Args:
            context (list of str): words

        Returns:
            [list of str]: corrected words
        """
        context_suggestions = self.get_context_suggestions(context)
        corr_words = self.extract_context_suggestions(context_suggestions)
        if verbose:
            for word, suggestions, corr_word in zip(
                context, context_suggestions, corr_words
            ):
                status  = suggestions["status"]
                if status == "notfound":
                    print(f"Nof found:  {word}")
                elif status not in ["present","exist"] and word != corr_word:
                    print(f"Modified:  {word} --> {corr_word} ({status})")

        return corr_words

    def correct_prod_df(self,form_df,debug=False):
        """
        Correct inplace mispelled words of a dataframe in productions format
        """
        grouped_df = form_df.groupby('emoji')
        # TODO: remove the limitation
        em_indexes = [(key,val) for key,val in grouped_df.groups.items()]
        if debug:
            em_indexes = em_indexes[:30]

        for emoji,indexes in tqdm(em_indexes):
            group = grouped_df.get_group(emoji)['word']
            words = group.to_list()
            corr_words = self.process_context(words,verbose=True)
            form_df['word'].loc[indexes] = corr_words