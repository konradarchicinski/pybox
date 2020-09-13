#!/usr/bin/env python
from analyticspy.tools.task import TaskInit

from sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer
from sklearn.decomposition import NMF, LatentDirichletAllocation
import numpy as np
import pandas as pd
import re


def prepare_textual_data(data, processed_column):
    """
    [summary]

    Args:
        data ([type]): [description]
        processed_column ([type]): [description]
    """
    data[f"{processed_column}Processed"] = data[processed_column].map(
        lambda row: re.sub(r'[,\.!?]', '', row)
    )
    data[f"{processed_column}Processed"] = data[processed_column].map(
        lambda row: row.lower()
    )


def prepare_results_table(feature_names, model_components):
    """
    [summary]

    Args:
        feature_names ([type]): [description]
        model_components ([type]): [description]

    Returns:
        [type]: [description]
    """
    model_scores = pd.DataFrame(
        model_components.transpose(),
        columns=[f"ScoreTopic{i}" for i in range(len(model_components))]
    )
    model_words = pd.DataFrame(
        feature_names,
        columns=["Word"]
    )

    return model_words.join(model_scores)


def latent_dirichlet_allocation(data, settings):
    """
    [summary]

    Args:
        data ([type]): [description]
        settings ([type]): [description]

    Returns:
        [type]: [description]
    """
    vectorizer_settings = settings["Vectorizer"]
    processed_column = settings["ProcessedColumn"]
    lda_params = settings["LDAparams"]

    prepare_textual_data(data, processed_column)

    tf_vectorizer = CountVectorizer(
        max_df=vectorizer_settings["max_df"],
        min_df=vectorizer_settings["min_df"],
        max_features=vectorizer_settings["max_features"],
        stop_words=vectorizer_settings["stop_words"]
    )
    tf = tf_vectorizer.fit_transform(data[f"{processed_column}Processed"])
    lda = LatentDirichletAllocation(
        n_components=lda_params["ComponentsNumber"],
        doc_topic_prior=lda_params["Theta"],
        topic_word_prior=lda_params["Beta"],
        max_iter=lda_params["MaxIterations"],
        max_doc_update_iter=lda_params["MaxDocumentUpdatingIterations"]
    ).fit(tf)

    return prepare_results_table(
        tf_vectorizer.get_feature_names(), lda.components_)


def non_negative_matrix_factorization(data, settings):
    """
    [summary]

    Args:
        data ([type]): [description]
        settings ([type]): [description]

    Returns:
        [type]: [description]
    """
    vectorizer_settings = settings["Vectorizer"]
    processed_column = settings["ProcessedColumn"]
    nmf_params = settings["NMFparams"]

    prepare_textual_data(data, processed_column)

    tfidf_vectorizer = TfidfVectorizer(
        max_df=vectorizer_settings["max_df"],
        min_df=vectorizer_settings["min_df"],
        max_features=vectorizer_settings["max_features"],
        stop_words=vectorizer_settings["stop_words"]
    )

    tfidf = tfidf_vectorizer.fit_transform(
        data[f"{processed_column}Processed"])
    nmf = NMF(
        n_components=nmf_params["ComponentsNumber"],
        init=nmf_params["InitializeMethod"],
        solver=nmf_params["Solver"],
        beta_loss=nmf_params["BetaLoss"],
        max_iter=nmf_params["MaxIterations"],
        alpha=nmf_params["Alpha"],
        l1_ratio=nmf_params["l1Ratio"]
    ).fit(tfidf)

    return prepare_results_table(
        tfidf_vectorizer.get_feature_names(), nmf.components_)


task_lda = TaskInit(
    task_name="TopicModel(LDA)",
    task_info="""
    The task is used for...
    """)
task_lda.add_setting(
    name="Vectorizer",
    value={
        "max_df": 0.95,
        "min_df": 2,
        "max_features": 1000,
        "stop_words": "english"
    },
    info="""
    Defines...
    """)
task_lda.add_setting(
    name="LDAparams",
    value={
        "ComponentsNumber": 10,
        "Theta": None,
        "Beta": None,
        "MaxIterations": 10,
        "MaxDocumentUpdatingIterations": 1000
    },
    info="""
    Defines...
    """)
task_lda.add_setting(
    name="ProcessedColumn",
    value="Abstract",
    info="""
    Defines...
    """)
task_lda.run(
    main_function=latent_dirichlet_allocation,
    task_inputs=["PapersFiltered"],
    task_outputs=["TopicDataLDA"])


task_nmf = TaskInit(
    task_name="TopicModel(NMF)",
    task_info="""
    The task is used for...
    """)
task_nmf.add_setting(
    name="Vectorizer",
    value={
        "max_df": 0.95,
        "min_df": 2,
        "max_features": 1000,
        "stop_words": "english"
    },
    info="""
    Defines...
    """)
task_nmf.add_setting(
    name="NMFparams",
    value={
        "ComponentsNumber": 10,
        "InitializeMethod": "nndsvd",
        "Solver": "mu",
        "BetaLoss": "kullback-leibler",
        "MaxIterations": 1000,
        "Alpha": 0.1,
        "l1Ratio": 0.5
    },
    info="""
    Defines...
    """)
task_nmf.add_setting(
    name="ProcessedColumn",
    value="Abstract",
    info="""
    Defines...
    """)
task_nmf.run(
    main_function=non_negative_matrix_factorization,
    task_inputs=["PapersFiltered"],
    task_outputs=["TopicDataNMF"])
