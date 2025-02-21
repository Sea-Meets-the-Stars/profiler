Profiler
========

.. image:: https://readthedocs.org/projects/profiler/badge/?version=latest
    :target: https://profiler.readthedocs.io/en/latest/?badge=latest
    :alt: Documentation Status

.. image:: https://img.shields.io/pypi/v/profiler.svg
    :target: https://pypi.python.org/pypi/profiler
    :alt: PyPI version

.. image:: https://img.shields.io/pypi/pyversions/profiler.svg
    :target: https://pypi.python.org/pypi/profiler
    :alt: Python versions

A Python package for analyzing oceanographic profiler data from various instruments including gliders, floats, and vertical microstructure profilers (VMPs).

Features
--------

* Support for multiple oceanographic instruments:
    * Spray Gliders
    * Solo Floats
    * EM-APEX Floats
    * Vertical Microstructure Profilers (VMPs)
    * Triaxus
* Robust data loading and processing capabilities
* Profile pairing and statistical analysis tools
* Integration with GSW-Python for seawater calculations
* Geographic coordinate transformations
* Quality control handling

Quick Install
------------

.. code-block:: bash

    pip install profiler

Requirements
-----------

* Python ≥ 3.7
* numpy
* gsw-python
* pymatreader
* pandas
* xarray

Quick Start
----------

Loading and analyzing glider data:

.. code-block:: python

    from profiler import gliderdata
    
    # Load a Spray glider dataset
    spray = gliderdata.SprayData.from_binned_file(
        'data.mat',
        'my_dataset',
        in_field=True
    )
    
    # Print basic information
    print(f"Number of profiles: {spray.Nprof}")
    print(f"Time range: {spray.ptime.min()} to {spray.ptime.max()}")

Pairing profiles for analysis:

.. code-block:: python

    from profiler import profilepairs
    
    # Create pairs within time constraints
    pairs = profilepairs.ProfilerPairs(
        [spray],
        max_time=10,  # hours
        avoid_same_glider=True
    )
    
    # Calculate statistics
    pairs.calc_delta(0, ['dT'])
    pairs.calc_Sn('dTdTdT')

Documentation
------------

Full documentation is available at `Read the Docs <https://profiler.readthedocs.io/>`_.

Development
----------

To install the development version:

.. code-block:: bash

    git clone https://github.com/your-org/profiler.git
    cd profiler
    pip install -e .

Contributing
-----------

Contributions are welcome! Please feel free to submit a Pull Request.

License
-------

This project is licensed under the MIT License - see the LICENSE file for details.

Citation
--------

If you use this package in your research, please cite:

.. code-block:: text

    Author, A. et al. (2024). Profiler: A Python package for oceanographic
    profiler data analysis. Journal of Open Source Software, X(XX), XXX.
    https://doi.org/10.xxxx/xxxx

Contact
-------

* Issue Tracker: https://github.com/your-org/profiler/issues
* Documentation: https://profiler.readthedocs.io/
