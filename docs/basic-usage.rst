Basic Usage
===========

This guide provides examples of common tasks using the Profiler package.

Loading Different Data Types
--------------------------

Spray Glider Data
~~~~~~~~~~~~~~~~

.. code-block:: python

   from profiler import gliderdata
   
   # Load a single Spray glider file
   spray = gliderdata.SprayData.from_binned_file(
       'data.mat',
       'my_dataset',
       in_field=True,
       adcp_on=False
   )

   # Load multiple files
   import glob
   datafiles = glob.glob('*.mat')
   sprays = gliderdata.SprayData.from_list(
       datafiles,
       'my_dataset',
       adcp_on=False,
       in_field=True
   )

Float Data
~~~~~~~~~

.. code-block:: python

   from profiler import floatdata
   
   # Load Solo float
   solo = floatdata.SoloData.from_binned_file(
       'solo.mat',
       'my_dataset',
       in_field=True
   )

   # Load EM-APEX float
   emapex = floatdata.EMApexData.from_binned_file(
       'emapex.mat',
       'my_dataset',
       in_field=True
   )

VMP Data
~~~~~~~~

.. code-block:: python

   from profiler import vmpdata
   
   vmp = vmpdata.VMPData.from_binned_file(
       'vmp.nc',
       'cusack',
       'my_dataset',
       in_field=True,
       missid=20000
   )

Data Processing Examples
----------------------

Binning Data
~~~~~~~~~~~

.. code-block:: python

   from profiler import binning
   
   # Bin data to standard depth levels
   binned_data = binning.bin_profilerdata(
       spray,
       pmin=10,      # Minimum pressure/depth
       pstep=10,     # Bin size
       pmax=200,     # Maximum pressure/depth
       pd='d',       # 'd' for depth, 'p' for pressure
       exclude='bad' # Exclude bad data points
   )

Calculating Geographic Distances
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from profiler.utils import offsets
   
   # Calculate distance and offset from a reference line
   dist, offset = offsets.calc_dist_offset(
       spray.lon,
       spray.lat,
       endpoints=((lon0, lon1), (lat0, lat1))
   )

Working with Profile Pairs
------------------------

Creating Pairs
~~~~~~~~~~~~

.. code-block:: python

   from profiler import profilepairs
   
   # Create pairs based on time separation
   pairs = profilepairs.ProfilerPairs(
       [spray],
       max_time=10,  # Maximum time separation in hours
       avoid_same_glider=True
   )

   # Calculate statistics on pairs
   pairs.calc_delta(0, ['dT'])  # Temperature differences
   pairs.calc_Sn('dTdTdT')      # Structure functions

Accessing Data Arrays
-------------------

Standard Arrays
~~~~~~~~~~~~~

.. code-block:: python

   # Time series
   times = spray.time     # Unix timestamps
   
   # Geographic coordinates
   lats = spray.lat      # Latitudes
   lons = spray.lon      # Longitudes
   
   # Profile data
   temp = spray.t        # Temperature
   sal = spray.s         # Salinity
   dens = spray.sigma    # Density

Subsetting Data
~~~~~~~~~~~~~

.. code-block:: python

   # Select specific profiles
   subset = spray.profile_subset(
       profiles=np.array([0, 1, 2])
   )

   # Cut based on time
   timecut = spray.cut_on_reltime(
       timecut=(0.2, 0.8)  # Keep middle 60% of time range
   )

GSW Calculations
--------------

.. code-block:: python

   from profiler.processing import gsw
   
   # Process a dictionary of data with GSW
   gsw.process_dict(data_dict)
   
   # This calculates:
   # - Absolute Salinity
   # - Conservative Temperature
   # - Potential Density
   # - In-situ Density
