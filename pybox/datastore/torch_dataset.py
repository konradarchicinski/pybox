#!/usr/bin/env python
import pybox.datastore.database as pbdsdb

import random
import logging
from tqdm import tqdm
from torch import tensor
from torch.utils.data import Dataset
from torchtext.vocab import Vocab, build_vocab_from_iterator
from torchtext.data.utils import ngrams_iterator, get_tokenizer


class TextClassificationDataset(Dataset):
    """Defines an abstract text classification datasets."""

    def __init__(self, vocab, data, labels):
        """Initiate text-classification dataset.

        Arguments:
            vocab: Vocabulary object used for dataset.
            data: a list of label/tokens tuple. tokens are a tensor after
                numericalizing the string tokens. label is an integer.
                [(label1, tokens1), (label2, tokens2), (label2, tokens3)]
            label: a set of the labels.
                {label1, label2}
        """

        super(TextClassificationDataset, self).__init__()
        self._data = data
        self._labels = labels
        self._vocab = vocab

    def __getitem__(self, i):
        return self._data[i]

    def __len__(self):
        return len(self._data)

    def __iter__(self):
        for x in self._data:
            yield x

    def get_labels(self):
        return self._labels

    def get_vocab(self):
        return self._vocab


def setup_datasets(ngrams, vocabulary=None, include_unk=False):
    """[summary]

    Args:
        ngrams ([type]): [description]
        vocabulary ([type], optional): [description]. Defaults to None.
        include_unk (bool, optional): [description]. Defaults to False.

    Raises:
        TypeError: [description]
        ValueError: [description]

    Returns:
        [type]: [description]
    """
    connection = pbdsdb.create_connection("AGNEWS")
    with connection:
        cur = connection.cursor()
        cur.execute("SELECT Classification,Lead,Body FROM NewsClassification")
        data_rows_list = cur.fetchall()

    random.seed(2020)
    random.shuffle(data_rows_list)

    split_index = int(len(data_rows_list) * 0.1)
    test_data_rows = data_rows_list[:split_index]
    train_data_rows = data_rows_list[split_index:]

    if vocabulary is None:
        logging.info("Building Vocab based on Training Dataset")
        vocabulary = build_vocab_from_iterator(
            _data_iterator(train_data_rows, ngrams))
    else:
        if not isinstance(vocabulary, Vocab):
            raise TypeError("Passed vocabulary is not of type `Vocab`")

    logging.info(f"Vocab has {len(vocabulary)} entries")

    logging.info("Creating training data")
    train_data, train_labels = _create_data_from_iterator(
        vocabulary, _data_iterator(train_data_rows, ngrams, yield_cls=True),
        include_unk)

    logging.info("Creating testing data")
    test_data, test_labels = _create_data_from_iterator(
        vocabulary, _data_iterator(test_data_rows, ngrams, yield_cls=True),
        include_unk)

    if len(train_labels ^ test_labels) > 0:
        raise ValueError("Training and test labels don't match")

    return (TextClassificationDataset(vocabulary, train_data, train_labels),
            TextClassificationDataset(vocabulary, test_data, test_labels))


def _data_iterator(data_rows, ngrams, yield_cls=False):
    """[summary]

    Args:
        data_rows ([type]): [description]
        ngrams ([type]): [description]
        yield_cls (bool, optional): [description]. Defaults to False.

    Yields:
        [type]: [description]
    """
    tokenizer = get_tokenizer("basic_english")

    for row in data_rows:
        tokens = ' '.join(row[1:])
        tokens = tokenizer(tokens)
        if yield_cls:
            yield int(row[0]) - 1, ngrams_iterator(tokens, ngrams)
        else:
            yield ngrams_iterator(tokens, ngrams)


def _create_data_from_iterator(vocabulary, iterator, include_unk):
    """[summary]

    Args:
        vocabulary ([type]): [description]
        iterator ([type]): [description]
        include_unk ([type]): [description]

    Returns:
        [type]: [description]
    """
    data = []
    labels = []
    with tqdm(unit_scale=0, unit='lines') as t:
        for cls, tokens in iterator:
            if include_unk:
                tokens = tensor([vocabulary[token] for token in tokens])
            else:
                token_ids = list(
                    filter(lambda x: x is not Vocab.UNK,
                           [vocabulary[token] for token in tokens]))
                tokens = tensor(token_ids)
            if len(tokens) == 0:
                logging.info('Row contains no tokens.')
            data.append((cls, tokens))
            labels.append(cls)
            t.update(1)

    return data, set(labels)
