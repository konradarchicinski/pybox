#!/usr/bin/env python
from pybox.task import Task

from sklearn.decomposition import NMF, LatentDirichletAllocation


def latent_dirichlet_allocation(word_importance, settings):
    """[summary]

    Args:
        word_importance (DataTable): [description]
        settings (dict): [description]
    """
    lda = LatentDirichletAllocation(
        n_components=settings["ComponentsNumber"],
        doc_topic_prior=settings["Theta"],
        topic_word_prior=settings["Beta"],
        max_doc_update_iter=settings["MaxDocumentUpdatingIterations"],
        max_iter=settings["MaxIterations"]).fit(word_importance)

    return lda.components_


def non_negative_matrix_factorization(word_importance, settings):
    """[summary]

    Args:
        word_importance (DataTable): [description]
        settings (dict): [description]
    """
    nmf = NMF(
        n_components=settings["ComponentsNumber"],
        init=settings["InitializeMethod"],
        solver=settings["Solver"],
        beta_loss=settings["BetaLoss"],
        max_iter=settings["MaxIterations"],
        alpha=settings["Alpha"],
        l1_ratio=settings["l1Ratio"]).fit(word_importance)

    return nmf.components_


def performe_topic_modelling(word_importance, settings):
    """[summary]

    Args:
        word_importance (DataTable): [description]
        settings (dict): [description]
    """
    model_type = settings["Parameters"]["ModelType"]

    if model_type == "LDA":
        return latent_dirichlet_allocation(word_importance, settings)
    elif model_type == "NMF":
        return non_negative_matrix_factorization(word_importance, settings)


def _dynamic_inputs_creation(dynamic_io_settings):
    """Creates a list of inputs names, supplied to the Task class."""
    parameters = dynamic_io_settings["TaskSettings"]["Parameters"]

    if parameters["ModelType"] == "LDA":
        return [f"TF({parameters['DataSource']})"]
    elif parameters["ModelType"] == "NMF":
        return [f"TFIDF({parameters['DataSource']})"]


def _dynamic_outputs_creation(dynamic_io_settings):
    """Creates a list of outputs names, supplied to the Task class."""
    parameters = dynamic_io_settings["TaskSettings"]["Parameters"]

    return ["TopicData({},{})".format(*parameters.values())]


task = Task(
    task_name="TopicModel(?model_type,?data_source)",
    task_info="""""")
task.add_setting(
    name="ComponentsNumber",
    default_value=10,
    info="""""")
task.add_setting(
    name="MaxIterations",
    default_value=10,
    info="""""")
task.add_setting(
    name="Theta",
    default_value=None,
    info="""""",
    task_parameters=["LDA"])
task.add_setting(
    name="Beta",
    default_value=None,
    info="""""",
    task_parameters=["LDA"])
task.add_setting(
    name="InitializeMethod",
    default_value="nndsvd",
    info="""""",
    task_parameters=["NMF"])
task.add_setting(
    name="Solver",
    default_value="mu",
    info="""""",
    task_parameters=["NMF"])
task.add_setting(
    name="BetaLoss",
    default_value="kullback-leibler",
    info="""""",
    task_parameters=["NMF"])
task.add_setting(
    name="Alpha",
    default_value=0.1,
    info="""""",
    task_parameters=["NMF"])
task.add_setting(
    name="l1Ratio",
    default_value=0.5,
    info="""""",
    task_parameters=["NMF"])
task.run(
    main_function=performe_topic_modelling,
    task_inputs=_dynamic_inputs_creation,
    task_outputs=_dynamic_outputs_creation)
