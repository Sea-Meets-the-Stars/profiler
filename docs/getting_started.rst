Getting Started
===============

Basic Installation
----------------

To install Profiler, you'll need Python 3.7 or later. The package can be installed using pip:

.. code-block:: bash

   pip install profiler

Dependencies will be automatically installed, including:

- numpy
- gsw-python
- pymatreader
- pandas
- xarray

Basic Usage
----------

Loading Data
~~~~~~~~~~~

The most common way to load data is using the `from_binned_file` method:

.. code-block:: python

   from profiler import gliderdata
   
   # Load a Spray glider dataset
   spray = gliderdata.SprayData.from_binned_file(
       'data.mat',
       'my_dataset',
       in_field=True
   )

   # Print basic information about the dataset
   print(spray)

Working with Profiles
~~~~~~~~~~~~~~~~~~~

Profile data is organized in arrays indexed by profile number and depth:

.. code-block:: python

   # Access temperature data
   temperatures = spray.t  # Shape: (n_profiles, n_depths)
   
   # Access metadata
   times = spray.time
   lats = spray.lat
   lons = spray.lon

Processing Data
~~~~~~~~~~~~~

Common processing tasks include:

.. code-block:: python

   # Calculate geographic distances
   spray.calc_dist()

   # Bin data to standard depth levels
   from profiler import binning
   binned_data = binning.bin_profilerdata(
       spray,
       pmin=10,
       pstep=10,
       pmax=200
   )

Pairing Profiles
~~~~~~~~~~~~~~

For analyzing spatial and temporal correlations:

.. code-block:: python

   from profiler import profilepairs

   # Create pairs of profiles within time/distance constraints
   pairs = profilepairs.ProfilerPairs(
       [spray],
       max_time=10,  # hours
       max_dist=100  # km
   )

   # Calculate statistics on the pairs
   pairs.calc_delta(0, ['dT'])
   pairs.calc_Sn('dTdTdT')

Working with Different Instruments
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The same interface works across different instrument types:

.. code-block:: python

   from profiler import floatdata, vmpdata

   # Load an EM-APEX float
   emapex = floatdata.EMApexData.from_binned_file(
       'emapex.mat',
       'my_dataset'
   )

   # Load a VMP
   vmp = vmpdata.VMPData.from_binned_file(
       'vmp.nc',
       'my_dataset'
   )

Next Steps
---------

- Review the :doc:`basic_usage` guide for more detailed examples
- Check the :doc:`api/core` documentation for complete API reference
- See :doc:`data_formats` for information about supported file formats
