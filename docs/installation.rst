Installation
============

Requirements
-----------

Profiler requires:

* Python 3.7 or later
* numpy
* gsw-python (for seawater calculations)
* pymatreader (for reading .mat files)
* pandas
* xarray (for netCDF handling)

Basic Installation
----------------

The recommended way to install Profiler is using pip:

.. code-block:: bash

   pip install profiler

Development Installation
----------------------

For development work, clone the repository and install in editable mode:

.. code-block:: bash

   git clone https://github.com/your-org/profiler.git
   cd profiler
   pip install -e .

Optional Dependencies
-------------------

Additional functionality is available with these optional packages:

* recharts - For visualization capabilities
* lucide-react - For UI components
* shadcn/ui - For enhanced UI elements

Install optional dependencies using:

.. code-block:: bash

   pip install profiler[full]

Troubleshooting
-------------

Common Issues
~~~~~~~~~~~

1. GSW Installation Issues
   If you encounter problems with gsw-python installation:

   .. code-block:: bash

      pip install gsw --no-cache-dir

2. MATLAB File Reading
   If pymatreader fails to read certain .mat files:

   .. code-block:: bash

      pip install -U scipy h5py

3. NetCDF Support
   For proper netCDF support, ensure you have:

   .. code-block:: bash

      pip install netCDF4

Environment Setup
---------------

For optimal performance, we recommend using a dedicated virtual environment:

.. code-block:: bash

   python -m venv profiler-env
   source profiler-env/bin/activate  # Linux/Mac
   profiler-env\Scripts\activate  # Windows
   pip install profiler
