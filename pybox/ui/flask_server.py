#!/usr/bin/env python
import os
import sys
from flask import request


def shutdown():
    """Shutdowns flask app server"""
    func = request.environ.get('werkzeug.server.shutdown')
    if func is None:
        raise RuntimeError('Not running with the Werkzeug Server')
    func()


def disable_print():
    """Disables console to print messages."""
    sys.stdout = open(os.devnull, 'w')


def enable_print():
    """Enables console to print messages."""
    sys.stdout = sys.__stdout__
