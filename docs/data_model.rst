Data Model
==========

The Profiler package uses a standardized data model defined in ``defs.py``. This document describes the core data types and their specifications.

Core Data Types
-------------

.. code-block:: python

   tbl_dmodel = {
       's': {
           'dtype': np.floating,
           'help': 'Salinity (psu)'
       },
       't': {
           'dtype': np.floating,
           'help': 'Temperature (C)'
       },
       'depth': {
           'dtype': np.floating,
           'help': 'Depth (m)'
       },
       'SA': {
           'dtype': np.floating,
           'help': 'Absolute Salinity (g/kg)'
       },
       'theta': {
           'dtype': np.floating,
           'help': 'Potential Temperature (C)'
       },
       'sigma': {
           'dtype': np.floating,
           'help': 'Potential Density (kg/m^3)'
       },
       'rho': {
           'dtype': np.floating,
           'help': 'In-situ Density (kg/m^3)'
       },
       'p': {
           'dtype': np.floating,
           'help': 'Pressure (dbar)'
       }
   }

Required Fields
-------------

The following fields are required for all profiles:

- lat: Latitude (degrees)
- lon: Longitude (degrees)
- datetime: Timestamp of measurement

Geographic Information
-------------------

Position Data
~~~~~~~~~~~

.. code-block:: python

   'lat': {
       'dtype': (float, np.floating),
       'help': 'Latitude of the center of the cutout (deg)'
   },
   'lon': {
       'dtype': (float, np.floating),
       'help': 'Longitude of the center of the cutout (deg)'
   }

Temporal Information
------------------

.. code-block:: python

   'datetime': {
       'dtype': pandas.Timestamp,
       'help': 'Timestamp of the cutout'
   }

Quality Control
-------------

.. code-block:: python

   'qual': {
       'dtype': np.int,
       'help': 'Quality flag'
   }

Metadata
-------

File Information
~~~~~~~~~~~~~~

.. code-block:: python

   'filename': {
       'dtype': str,
       'help': 'Filename of the original data file'
   }

Usage in Code
-----------

Example of validating data against the model:

.. code-block:: python

   from profiler.defs import tbl_dmodel
   
   def validate_data(data_dict):
       """Validate data against the model."""
       for field in tbl_dmodel['required']:
           if field not in data_dict:
               raise ValueError(f"Required field {field} missing")
           
           expected_type = tbl_dmodel[field]['dtype']
           if not isinstance(data_dict[field], expected_type):
               raise TypeError(f"Field {field} has wrong type")
