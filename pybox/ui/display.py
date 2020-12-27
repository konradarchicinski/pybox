#!/usr/bin/env python
from pybox.helpers.html import create_datatable_header
from pybox.ui import chrome, plotly_figures
from flask import Flask, render_template, request
from plotly.utils import PlotlyJSONEncoder

import logging
import json
import sys
import os


def datatable(data, static=True, length_limit=None):
    """Displays DataTable object in the newly created window.

    Args:

        data (DataTable): DataTable object to be displayed.
        static (bool, optional): flag indicating if run app
            should be static or dynamic. Defaults to True.
        length_limit (int, optional): maximal observation number
            to display. Defauts to None.
    """
    if length_limit is None:
        length_limit = data.length
    html_table = data.as_string(rows_number=length_limit, text_format="html")
    # Stylistic improvement, headers section is removed from html
    # to create a space for a better looking one.
    html_table = html_table[
        html_table.index("<tbody>"):html_table.rindex("</table>")]

    html_head = create_datatable_header(data._data_map)

    app = _initiate_app("table_template.html",
                        dict(table_head=html_head,
                             table_body=html_table),
                        static)
    _run_app(app)


def surface(data, static=True):
    """Displays surface plot in the newly created window.

    Args:

        data (array-like): array containing data to be displayed.
        static (bool, optional): flag indicating if run app
            should be static or dynamic. Defaults to True.
    """
    plotly_surface = plotly_figures.surface(data)
    app = _initiate_app("plotly_template.html",
                        dict(figure=json.dumps(
                            plotly_surface, cls=PlotlyJSONEncoder)),
                        static)
    _run_app(app)


def _initiate_app(template, template_variables, static_type):
    app = Flask(__name__,
                static_url_path='',
                static_folder='static',
                template_folder='templates')

    @app.route('/')
    def _():
        # Checking whether user's dynamic requests can be expected in the app.
        if static_type:
            shutdown_hook = request.environ.get('werkzeug.server.shutdown')
            if shutdown_hook is not None:
                shutdown_hook()
        return render_template(template, **template_variables)

    return app


def _run_app(app):
    # Disable printing of information from the server.
    log = logging.getLogger('werkzeug')
    log.setLevel(logging.ERROR)

    # Disable printing any information in the console.
    sys.stdout = open(os.devnull, 'w')

    chrome.run(["http://localhost:5000/"])
    app.run()

    # Enable printing information in the console.
    sys.stdout = sys.__stdout__
