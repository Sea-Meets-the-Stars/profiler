Profiler Documentation
=====================

Oceanographic Profiler Data Analysis Tools
----------------------------------------

.. image:: https://readthedocs.org/projects/profiler/badge/?version=latest
    :target: https://profiler.readthedocs.io/en/latest/?badge=latest
    :alt: Documentation Status

Overview
--------
Profiler is a Python package for analyzing and processing oceanographic profiler data from various instruments including gliders, floats, and vertical microstructure profilers (VMPs).

Key Features
-----------
* Support for multiple oceanographic instruments including:
    * Spray Gliders
    * Solo Floats  
    * EM-APEX Floats
    * VMPs
    * Triaxus
* Data loading and processing capabilities
* Profile pairing and analysis tools
* Integration with GSW-Python for seawater calculations
* Geographic coordinate transformations and calculations

Installation
------------
.. code-block:: bash

   pip install profiler

Quick Start
----------
.. code-block:: python

   from profiler import gliderdata
   
   # Load a Spray glider dataset
   spray = gliderdata.SprayData.from_binned_file('data.mat', 'my_dataset')

   # Process and analyze the data
   spray.calc_dist()

Contents
--------

.. toctree::
   :maxdepth: 2
   :caption: User Guide

   installation
   getting_started
   basic_usage
   data_formats
   data_model

.. toctree::
   :maxdepth: 2
   :caption: API Reference

   api/core
   api/instruments
   api/processing
   api/analysis
   api/data_model

.. toctree::
   :maxdepth: 2
   :caption: File Formats

   data_formats
   file_specifications

.. toctree::
   :maxdepth: 1
   :caption: Development

   contributing
   changelog

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
