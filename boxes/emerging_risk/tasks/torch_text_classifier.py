#!/usr/bin/env python
from pybox.task import Task
import pybox.datastore.torch_dataset as pbdstd

import time
import torch
from torch.utils.data import DataLoader
from torch.utils.data.dataset import random_split
from torchtext.data.utils import get_tokenizer, ngrams_iterator


class TextSentiment(torch.nn.Module):
    def __init__(self, vocabulary_size, embedding_dimension, num_class):
        super().__init__()
        self.embedding = torch.nn.EmbeddingBag(
            vocabulary_size, embedding_dimension, sparse=True)
        self.fc = torch.nn.Linear(embedding_dimension, num_class)
        self.init_weights()

    def init_weights(self):
        initrange = 0.5
        self.embedding.weight.data.uniform_(-initrange, initrange)
        self.fc.weight.data.uniform_(-initrange, initrange)
        self.fc.bias.data.zero_()

    def forward(self, text, offsets):
        embedded = self.embedding(text, offsets)
        return self.fc(embedded)


def generate_batch(batch):
    label = torch.tensor([entry[0] for entry in batch])
    text = [entry[1] for entry in batch]
    offsets = [0] + [len(entry) for entry in text]
    # torch.Tensor.cumsum returns the cumulative sum
    # of elements in the dimension dim.
    # torch.Tensor([1.0, 2.0, 3.0]).cumsum(dim=0)

    offsets = torch.tensor(offsets[:-1]).cumsum(dim=0)
    text = torch.cat(text)
    return text, offsets, label


def train_func(sub_train_, model, criterion, optimizer,
               scheduler, device, batch_size):
    # Train the model
    train_loss = 0
    train_acc = 0
    data = DataLoader(sub_train_, batch_size=batch_size, shuffle=True,
                      collate_fn=generate_batch)
    for i, (text, offsets, cls) in enumerate(data):
        optimizer.zero_grad()
        text, offsets, cls = text.to(
            device), offsets.to(device), cls.to(device)
        output = model(text, offsets)
        loss = criterion(output, cls)
        train_loss += loss.item()
        loss.backward()
        optimizer.step()
        train_acc += (output.argmax(1) == cls).sum().item()

    # Adjust the learning rate
    scheduler.step()

    return train_loss / len(sub_train_), train_acc / len(sub_train_)


def test(data_, model, criterion, device, batch_size):
    loss = 0
    acc = 0
    data = DataLoader(data_, batch_size=batch_size, collate_fn=generate_batch)
    for text, offsets, cls in data:
        text, offsets, cls = text.to(
            device), offsets.to(device), cls.to(device)
        with torch.no_grad():
            output = model(text, offsets)
            loss = criterion(output, cls)
            loss += loss.item()
            acc += (output.argmax(1) == cls).sum().item()

    return loss / len(data_), acc / len(data_)


def testing_predict(model, vocabulary, ngrams):
    tokenizer = get_tokenizer("basic_english")
    ag_news_label = {1: "World", 2: "Sports", 3: "Business", 4: "Sci/Tec"}
    ex_text_str = """
        MEMPHIS, Tenn. – Four days ago, Jon Rahm was enduring the
        season’s worst weather conditions on Sunday at The Open on
        his way to a closing 75 at Royal Portrush, which considering
        the wind and the rain was a respectable showing. Thursday’s
        first round at the WGC-FedEx St. Jude Invitational was another
        story. With temperatures in the mid-80s and hardly any wind,
        the Spaniard was 13 strokes better in a flawless round. Thanks
        to his best putting performance on the PGA Tour, Rahm finished
        with an 8-under 62 for a three-stroke lead, which was even more
        impressive considering he’d never played the front nine at TPC
        Southwind.
        """
    with torch.no_grad():
        text = torch.tensor(
            [vocabulary[token]
             for token in ngrams_iterator(tokenizer(ex_text_str), ngrams)])
        output = model(text, torch.tensor([0]))
        print("\nTesting the prediction of sample text:")
        print(ex_text_str)
        print("This is a %s news" % ag_news_label[output.argmax(1).item() + 1])


def run_model(settings):
    """
    [summary]

    Args:
        settings ([type]): [description]
    """
    ngrams = settings["NGrams"]
    batch_size = settings["BatchSize"]
    epochs_number = settings["EpochNumber"]
    embedding_dimension = settings["EmbeddingDimension"]

    train_dataset, test_dataset = pbdstd.setup_datasets(ngrams)
    vocabulary_size = len(train_dataset.get_vocab())
    class_number = len(train_dataset.get_labels())

    min_valid_loss = float('inf')
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model = TextSentiment(
        vocabulary_size,
        embedding_dimension,
        class_number).to(device)

    criterion = torch.nn.CrossEntropyLoss().to(device)
    optimizer = torch.optim.SGD(model.parameters(), lr=4.0)
    scheduler = torch.optim.lr_scheduler.StepLR(optimizer, 1, gamma=0.9)

    train_len = int(len(train_dataset) * 0.95)
    sub_train_, sub_valid_ = random_split(
        train_dataset, [train_len, len(train_dataset) - train_len])

    for epoch in range(epochs_number):

        start_time = time.time()
        train_loss, train_acc = train_func(
            sub_train_, model, criterion, optimizer, scheduler, device, batch_size)
        valid_loss, valid_acc = test(
            sub_valid_, model, criterion, device, batch_size)

        secs = int(time.time() - start_time)
        mins = secs / 60
        secs = secs % 60

        print(
            'Epoch: %d' %
            (epoch + 1), " | time in %d minutes, %d seconds" %
            (mins, secs))
        print(
            f'\t\tLoss: {train_loss:.4f}(train)\t|\tAcc: {train_acc * 100:.1f}%(train)')
        print(
            f'\t\tLoss: {valid_loss:.4f}(valid)\t|\tAcc: {valid_acc * 100:.1f}%(valid)')

    print('\nChecking the results of test dataset...')
    test_loss, test_acc = test(
        test_dataset, model, criterion, device, batch_size)
    print(
        f'\tLoss: {test_loss:.4f}(test)\t|\tAcc: {test_acc * 100:.1f}%(test)')

    testing_predict(model, train_dataset.get_vocab(), ngrams)


task = Task(
    task_name="TextClassification",
    task_info="""
    The task is used for thematic classification of the provided text.
    """)
task.add_setting(
    name="NGrams",
    default_value=2,
    info="""
    Defines contiguous sequence of items from a given sample of text or speech.
    """)
task.add_setting(
    name="BatchSize",
    default_value=16,
    info="""
    Defines the number of samples that will be propagated through the network.
    """)
task.add_setting(
    name="EpochNumber",
    default_value=5,
    info="""
    Defines the number times that the learning algorithm will work through
    the entire training dataset.
    """)
task.add_setting(
    name="EmbeddingDimension",
    default_value=32,
    info="""
    Defines the smallest dimension required to embed an object.
    """)
task.run(main_function=run_model)
