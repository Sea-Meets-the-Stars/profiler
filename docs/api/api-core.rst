Core API Reference
=================

ProfilerData Base Class
----------------------

.. automodule:: profiler.profilerdata
   :members:
   :undoc-members:
   :show-inheritance:

.. autoclass:: profiler.profilerdata.ProfilerData
   :members:
   :undoc-members:
   :special-members: __init__
   :show-inheritance:

ADCPData Class
-------------

.. autoclass:: profiler.profilerdata.ADCPData
   :members:
   :undoc-members:
   :special-members: __init__
   :show-inheritance:

Key Properties
~~~~~~~~~~~~~
- **has_adcp**: bool - Indicates if ADCP capabilities are present
- **adcp_on**: bool - Current state of ADCP functionality

Core Data Arrays
~~~~~~~~~~~~~~
Standard arrays present in ProfilerData objects:

Profile Arrays
^^^^^^^^^^^^^
- time: Unix timestamp array
- lat: Latitude array 
- lon: Longitude array

Depth Arrays 
^^^^^^^^^^^
- depth: Depth levels

Profile-Depth Arrays
^^^^^^^^^^^^^^^^^^
- t: Temperature
- s: Salinity
- p: Pressure
- theta: Potential temperature
- sigma: Potential density
