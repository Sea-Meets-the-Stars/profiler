Data Formats
============

This document describes the data formats supported by the Profiler package.

Supported File Types
------------------

MATLAB Files (.mat)
~~~~~~~~~~~~~~~~~

Used primarily for:
- Spray glider data
- Solo float data
- EM-APEX float data
- Triaxus data

Required Structure:
^^^^^^^^^^^^^^^^^^

For binned data:

.. code-block:: python

   {
       'bindata': {  # or 'ctd' for non-field data
           'time': [...],    # Unix timestamps
           'lat': [...],     # Latitudes
           'lon': [...],     # Longitudes
           't': [...],       # Temperature
           's': [...],       # Salinity
           'p': [...],       # Pressure
           'depth': [...]    # Depth
       }
   }

For raw data:

.. code-block:: python

   {
       'data': {
           'time': [...],
           'lat': [...],
           'lon': [...],
           't': [[...], ...],  # List of arrays
           's': [[...], ...],
           'qual': {
               't': [...],     # Quality flags
               's': [...]
           }
       }
   }

NetCDF Files (.nc)
~~~~~~~~~~~~~~~~

Used primarily for:
- VMP data
- Slocum glider data

Required Variables:
^^^^^^^^^^^^^^^^^

.. code-block:: python

   dimensions:
       time
       depth
   
   variables:
       time(time)
       lat(time)
       lon(time)
       temperature(time, depth)
       salinity(time, depth)
       pressure(time, depth)

Quality Control Flags
-------------------

Standard Flags:
~~~~~~~~~~~~~

.. code-block:: python

   CTD_SENSOR_OFF = 9     # Sensor not recording
   CTD_BAD = 7           # Bad data
   CTD_QUESTIONABLE = 3  # Questionable data
   GPS_GOOD = 0         # Good GPS fix

Data Array Types
--------------

Profile Arrays
~~~~~~~~~~~~
Arrays indexed by profile number:

- time
- lat
- lon
- dist
- offset

Depth Arrays
~~~~~~~~~~
Arrays indexed by depth level:

- depth
- p (pressure)

Profile-Depth Arrays
~~~~~~~~~~~~~~~~~
2D arrays indexed by both profile and depth:

- t (temperature)
- s (salinity)
- theta (potential temperature)
- sigma (potential density)
- SA (absolute salinity)
- rho (in-situ density)

ADCP Arrays
~~~~~~~~~~
For instruments with ADCP capability:

- udop
- vdop
- udopacross
- udopalong

File Naming Conventions
---------------------

Spray Gliders
~~~~~~~~~~~
``NNNN.mat`` where NNNN is the glider number

Solo Floats
~~~~~~~~~~
``NNNN.mat`` where NNNN is the float number

EM-APEX Floats
~~~~~~~~~~~~
``FNNNN.mat`` where NNNN is the float number

VMP
~~~
Standard naming: ``vmp_YYYYMMDD.nc``
