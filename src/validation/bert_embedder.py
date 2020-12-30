from transformers import AutoTokenizer, BertForMaskedLM
import pickle as pk
from transformers import BertTokenizer
from transformers import BertModel
import torch

class BertEmbedder():
    def __init__(self):
        self.tokenizer = BertTokenizer.from_pretrained('bert-base-uncased')
        self.model = BertModel.from_pretrained('bert-base-uncased',output_hidden_states=True)

    def get_embedding(self,text,embed_dim=1):
        # Add the special tokens.
        marked_text = "[CLS] " + text + " [SEP]"
        # Split the sentence into tokens.
        tokenized_text = self.tokenizer.tokenize(marked_text)
        # Map the token strings to their vocabulary indeces.
        indexed_tokens = self.tokenizer.convert_tokens_to_ids(tokenized_text)

        # Convert inputs to PyTorch tensors
        tokens_tensor = torch.tensor([indexed_tokens])
        # Put the model in "evaluation" mode,meaning feed-forward operation.
        self.model.eval()

        #Run the text through BERT, get the output and collect all of the hidden states produced from all 12 layers.
        with torch.no_grad():
            outputs = self.model(tokens_tensor)
        # can use last hidden state as word embeddings
        last_hidden_state = outputs[0]
        # Evaluating the model will return a different number of objects               based on how it's  configured in the `from_pretrained` call earlier. In this case, becase we set `output_hidden_states = True`, the third item will be the hidden states from all layers. See the documentation for more details:https://huggingface.co/transformers/model_doc/bert.html#bertmodel
        hidden_states = outputs[2]
        word_embeddings = {1: last_hidden_state,
                           2: hidden_states[0],
                           3: torch.stack(hidden_states).sum(0),
                           4: torch.stack(hidden_states[2:]).sum(0),
                           5: torch.stack(hidden_states[-4:]).sum(0),
                           6: torch.cat([hidden_states[i] for i in [-1,-2,-3,-4]], dim=-1)}

        embedding = word_embeddings[embed_dim].sum(axis=0).numpy()
        return embedding

class BertWrapper():
    def __init__(self,bert_vec_path):
        self.vectors = pk.load(open(bert_vec_path,"rb"))

    def get_vector(self,em):
        """
        Args:
            em (str): emoji to obtain a vector for
        """
        return self.vectors[em]