""" Define data model, options, etc. for SSL models and analysis"""
import numpy as np
import pandas

# SSL options
tbl_dmodel = {
    's': dict(dtype=np.floating,
                help='Salinity (psu)'),
    't': dict(dtype=np.floating,
                help='Temperature (C)'),
    'depth': dict(dtype=np.floating,
                help='Depth (m)'),
    'SA': dict(dtype=np.floating,
                help='Absolute Salinity (g/kg)'),
    'theta': dict(dtype=np.floating,
                help='Potential Temperature (C)'),
    'sigma': dict(dtype=np.floating,
                help='Potential Density (kg/m^3)'),
    'rho': dict(dtype=np.floating,
                help='In-situ Density (kg/m^3)'),
    'p': dict(dtype=np.floating,
                help='Pressure (dbar)'),
    'qual': dict(dtype=np.int,
                help='Quality flag'),
    'lat': dict(dtype=(float,np.floating),
                help='Latitude of the center of the cutout (deg)'),
    'lon': dict(dtype=(float,np.floating),
                help='Longitude of the center of the cutout (deg)'),
    'filename': dict(dtype=str,
                help='Filename of the original data file from which the cutout was extracted'),
    'datetime': dict(dtype=pandas.Timestamp,
                help='Timestamp of the cutout'),
    'required': ('lat', 'lon', 
                 #'row', 'col',  # ADD THESE BACK!!!!
                 'datetime'),
}
