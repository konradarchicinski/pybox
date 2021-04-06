#!/usr/bin/env python
import setuptools

with open("README.md", "r", encoding="utf-8") as readme:
    LONG_DESCRIPTION = readme.read()

setuptools.setup(
    name="pybox",
    version="0.0.1",
    author="Konrad Archiciński",
    author_email="konrad.archicinski@gmail.com",
    description="PyBox application",
    long_description=LONG_DESCRIPTION,
    long_description_content_type="docs/index",
    license="MIT",
    project_urls={
        "Source": "https://github.com/konradarchicinski/pybox/"
    },
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
    install_requires=[
        "ipython",
        "numpy",
        "numba",
        "pyarrow",
        "torch",
        "plotly",
        "scikit-learn",
        "gensim",
        "scipy",
        "nltk",
        "flask",
        "selenium",
        "tqdm",
        "pyyaml",
        "lxml",
        "spacy[cuda111]==2.3.5",
        "spacy-lookups-data",
        "torchtext",
        "xmltodict",
        "msedge-selenium-tools",
        "pybind11",
        "cppimport",
        "arch",
        "numdifftools",
        "tabulate",
        ("en_core_web_sm @ https://github.com/explosion/spacy-models/releases"
         "/download/en_core_web_sm-2.3.1/en_core_web_sm-2.3.1.tar.gz"
         "#egg=en_core_web_sm")
    ]
)
