""" Define data model, options, etc. for SSL models and analysis"""
import numpy as np
import pandas

# SSL options
tbl_dmodel = {
    's': dict(dtype=np.floating,
                help='Salinity (psu)'),
    't': dict(dtype=np.floating,
                help='Temperature (C)'),
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
