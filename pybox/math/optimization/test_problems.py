#!/usr/bin/env python
import numpy as np


def eggholder_function(x):
    """https://www.sfu.ca/~ssurjano/egg.html"""
    return (
        -(x[1]+47)*np.sin(np.sqrt(np.absolute(x[1]+x[0]/2+47))) -
        x[0]*np.sin(np.sqrt(np.absolute(x[0]-x[1]-47)))
    )


def eggholder_function_values(domain=None, samples=300):
    dimension = 2
    if domain is None:
        domain = [(-512, 512)]*dimension
    x = _prepare_function_arguments(dimension, domain, samples)

    return np.array([*x, eggholder_function(x)])


def shwefel_function(x, dimension=2):
    """https://www.sfu.ca/~ssurjano/schwef.html"""
    fx = 418.9829*dimension
    for i in range(dimension):
        fx -= x[i]*np.sin(np.sqrt(np.absolute(x[i])))
    return fx


def shwefel_function_values(dimension=2, domain=None, samples=300):
    if domain is None:
        domain = [(-500, 500)]*dimension
    x = _prepare_function_arguments(dimension, domain, samples)

    return np.array([*x, shwefel_function(x, dimension)])


def goldstein_price_function(x):
    """https://www.sfu.ca/~ssurjano/goldpr.html"""
    return (
        (1+(19-14*x[0]+3*x[0]**2-14*x[1]+6*x[0]*x[1]+3*x[1]**2)*(x[0]+x[1]+1)**2) *
        (30+(18-32*x[0]+12*x[0]**2+48*x[1]-36 *
             x[0]*x[1]+27*x[1]**2)*(2*x[0]-3*x[1])**2)
    )


def goldstein_price_function_values(domain=None, samples=300):
    dimension = 2
    if domain is None:
        domain = [(-2, 2)]*dimension
    x = _prepare_function_arguments(dimension, domain, samples)

    return np.array([*x, goldstein_price_function(x)])


def log_goldstein_price_function(x):
    """https://www.sfu.ca/~ssurjano/goldpr.html"""
    return (np.log(goldstein_price_function(4*x-2)) - 8.693)/2.427


def log_goldstein_price_function_values(domain=None, samples=300):
    dimension = 2
    if domain is None:
        domain = [(-2, 2)]*dimension
    x = _prepare_function_arguments(dimension, domain, samples)

    return np.array([*x, log_goldstein_price_function(x)])


def langermann_function(x, array_a=None, array_c=None):
    """https://www.sfu.ca/~ssurjano/langer.html"""
    if array_a is None:
        array_a = np.array([[3, 5], [5, 2], [2, 1], [1, 4], [7, 9]])
    if array_c is None:
        array_c = np.array([1, 2, 5, 2, 3])

    m, d = array_a.shape
    fx = 0
    for i in range(m):
        run_sum = 0
        for j in range(d):
            run_sum += (x[j] - array_a[i, j])**2
        fx += array_c[i]*np.exp(-run_sum/np.pi)*np.cos(run_sum*np.pi)
    return fx


def langermann_function_values(domain=None, samples=300, array_a=None, array_c=None):
    if array_a is None:
        array_a = np.array([[3, 5], [5, 2], [2, 1], [1, 4], [7, 9]])
    if array_c is None:
        array_c = np.array([1, 2, 5, 2, 3])
    _, d = array_a.shape
    if domain is None:
        domain = [(0, 10)]*d
    x = _prepare_function_arguments(d, domain, samples)

    return np.array([*x, langermann_function(x, array_a, array_c)])


def _prepare_function_arguments(argument_numbers, domain, samples):
    arguments = list()
    for i in range(argument_numbers):
        arguments.append(np.linspace(domain[i][0], domain[i][1], samples))

    return np.array(np.meshgrid(*arguments))
