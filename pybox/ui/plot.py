#!/usr/bin/env python
from pybox.ui import chrome, flask_server, plotly_figures

from plotly.utils import PlotlyJSONEncoder
from flask import Flask, render_template
import logging
import json


log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)


def show(data, figure_type):
    """Displays plot created from provided data in the new
    app window.

    Args:

        data (array-like): points to be transformed into plot.
        figure_type (str): type of the figure to be created.
    """
    if figure_type == "surface":
        figure = plotly_figures.surface(data)
    else:
        raise ValueError

    graph = json.dumps(figure, cls=PlotlyJSONEncoder)
    app = Flask(__name__)

    @app.route('/')
    def _():
        return render_template('plot_template.html', plot=graph)

    chrome.run(["http://localhost:5000/"])
    flask_server.disable_print()
    app.run()
    flask_server.enable_print()
    flask_server.shutdown()
