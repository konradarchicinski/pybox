#!/usr/bin/env python
from pybox.tools.task import Task

from gensim.models import Word2Vec
from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.corpus import stopwords
import string


def prepare_initial_data_to_model(initial_text_data, processed_column):
    """
    [summary]

    Args:
        initial_text_data ([type]): [description]
        processed_column ([type]): [description]

    Returns:
        [type]: [description]
    """
    stop_words = stopwords.words('english') + \
        list(string.punctuation) + ['’', '”', '“']

    text_data_string = str()
    for abstract in initial_text_data[processed_column]:
        text_data_string += abstract.replace("- \r\n", "").replace("\r\n", "")

    data_to_model = []
    for sentence in sent_tokenize(text_data_string):
        word_tokenized_sentence = []
        for word in word_tokenize(sentence.lower()):
            if word not in stop_words:
                word_tokenized_sentence.append(word)
        data_to_model.append(word_tokenized_sentence)

    return data_to_model


def continuous_bag_of_words(initial_text_data):
    """
    [summary]

    Args:
        initial_text_data ([type]): [description]

    Returns:
        [type]: [description]
    """
    data_model = prepare_initial_data_to_model(initial_text_data, "Abstract")

    model = Word2Vec(sentences=data_model, min_count=50, size=100)

    return model.mv


def forecast_topics(text_data, lda_topics, nmf_topics, settings):
    """
    [summary]

    Args:
        text_data ([type]): [description]
        lda_topics ([type]): [description]
        nmf_topics ([type]): [description]
        settings ([type]): [description]

    Returns:
        [type]: [description]
    """
    number_of_topic_representatives = settings["NumberOfTopicRepresentatives"]

    topics_dict = {"NMF": {}, "LDA": {}}
    for method, method_table in [("NMF", nmf_topics), ("LDA", lda_topics)]:
        for i in range(len(method_table.columns) - 1):
            topic_table = method_table[["Word", f"ScoreTopic{i}"]].nlargest(
                number_of_topic_representatives, f"ScoreTopic{i}"
            )
            topics_dict[method][f"Topic{i}"] = list(topic_table["Word"])

    cbow_model = continuous_bag_of_words(text_data)

    return topics_dict


task = Task(
    task_name="ArticleTopics",
    task_info="""
    The task is used for...
    """)
task.add_setting(
    name="NumberOfTopicRepresentatives",
    default_value=10,
    info="""
    Defines...
    """)
task.run(
    main_function=forecast_topics,
    task_inputs=[
        "PapersFiltered",
        "TopicDataLDA",
        "TopicDataNMF"
    ],
    task_outputs=["ArticleTopics"])
