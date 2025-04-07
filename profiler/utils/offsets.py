""" Python functions for calculating offsets and distances
    from a line 
"""

import numpy as np

from IPython import embed

def calc_dist_offset(lons:np.ndarray, lats:np.ndarray,
                     endpoints:tuple):
    """ Calculate the distnace from shore and offset from a line
      for a given line 

    Args:
        line (str): line name
        lons (np.ndarray): longitudes
        lats (np.ndarray): latitudes
        endpoints (tuple, optional): endpoints of the line. Defaults to None.
            lonendpts
            latendpts

    Returns:
        tuple: dist, offset
    """

    # Endpoints
    if endpoints is None:
        lonendpts, latendpts = line_endpoints(line)
    else:
        lonendpts, latendpts = endpoints
    # Unpack
    lon0, lon1 = lonendpts
    lat0, lat1 = latendpts

    # Constants
    nm2km = 1.852
    deg2min = 60.
    deg2rad = np.pi/180
    deg2km=deg2min*nm2km

    # Calculate angle of new coordinate system relative to east
    dyy = (lat1-lat0)
    dxx = np.cos(1/2*(lat1+lat0)*deg2rad)*(lon1-lon0)
    theta = np.arctan2(dyy,dxx)

    # Calculate x, y of lon, lat relative to start of line
    dy = (lats-lat0)*deg2km;
    dx = np.cos(1/2*(lat1+lat0)*deg2rad)*(lons-lon0)*deg2km

    # Calculate dist, offset in new coordinate system by rotating
    z=dx+1j*dy
    zhat=z*np.exp(-1j*theta)

    if np.any(np.isnan(zhat)):
        embed(header='NaN in zhat')
        raise ValueError('calc_dist_offset: NaN in zhat')

    # Finish
    dist=np.real(zhat)
    offset=np.imag(zhat)

    # Return
    return dist, offset


def jsonify(obj, debug=False):
    """ Recursively process an object so it can be serialised in json
    format. Taken from linetools.

    WARNING - the input object may be modified if it's a dictionary or
    list!

    Parameters
    ----------
    obj : any object
    debug : bool, optional

    Returns
    -------
    obj - the same obj is json_friendly format (arrays turned to
    lists, np.int64 converted to int, np.float64 to float, and so on).

    """
    if isinstance(obj, np.float64):
        obj = float(obj)
    elif isinstance(obj, np.float32):
        obj = float(obj)
    elif isinstance(obj, np.int32):
        obj = int(obj)
    elif isinstance(obj, np.int64):
        obj = int(obj)
    elif isinstance(obj, np.int16):
        obj = int(obj)
    elif isinstance(obj, np.bool_):
        obj = bool(obj)
    elif isinstance(obj, np.str_):
        obj = str(obj)
    elif isinstance(obj, np.ndarray):  # Must come after Quantity
        obj = obj.tolist()
    elif isinstance(obj, dict):
        for key, value in obj.items():
            obj[key] = jsonify(value, debug=debug)
    elif isinstance(obj, list):
        for i,item in enumerate(obj):
            obj[i] = jsonify(item, debug=debug)
    elif isinstance(obj, tuple):
        obj = list(obj)
        for i,item in enumerate(obj):
            obj[i] = jsonify(item, debug=debug)
        obj = tuple(obj)

    if debug:
        print(type(obj))
    return obj


def savejson(filename:str, obj:dict, overwrite=False, indent=None, easy_to_read=False,
             **kwargs):
    """ Save a python object to filename using the JSON encoder.

    Parameters
    ----------
    filename : str
    obj : object
      Frequently a dict
    overwrite : bool, optional
    indent : int, optional
      Input to json.dump
    easy_to_read : bool, optional
      Another approach and obj must be a dict
    kwargs : optional
      Passed to json.dump

    Returns
    -------

    """

    if os.path.lexists(filename) and not overwrite:
        raise IOError('%s exists' % filename)
    if easy_to_read:
        if not isinstance(obj, dict):
            raise IOError("This approach requires obj to be a dict")
        with io.open(filename, 'w', encoding='utf-8') as f:
            f.write(json.dumps(obj, sort_keys=True, indent=4,
                               separators=(',', ': '), **kwargs))
    else:
        if filename.endswith('.gz'):
            with gzip.open(filename, 'wt') as fh:
                json.dump(obj, fh, indent=indent, **kwargs)
        else:
            with open(filename, 'wt') as fh:
                json.dump(obj, fh, indent=indent, **kwargs)


def loadjson(filename):
    """Load a python object saved with savejson.

    Args:
        filename (str): The path to the JSON file.

    Returns:
        obj: The loaded Python object.

    """
    if filename.endswith('.gz'):
        with gzip.open(filename, "rb") as f:
            obj = json.loads(f.read().decode("ascii"))
    else:
        with open(filename, 'rt') as fh:
            obj = json.load(fh)

    return obj

def merge_dicts(dict_list:list):
    result = {}
    for d in dict_list:
        result.update(d)
    return result

def match_ids(IDs, match_IDs, require_in_match=True):
    """ Match input IDs to another array of IDs (usually in a table)
    Return the rows aligned with input IDs

    Parameters
    ----------
    IDs : ndarray
        IDs that are to be found in match_IDs
    match_IDs : ndarray
        IDs to be searched
    require_in_match : bool, optional
        Require that each of the input IDs occurs within the match_IDs

    Returns
    -------
    rows : ndarray
      Rows in match_IDs that match to IDs, aligned
      -1 if there is no match
    """
    rows = -1 * np.ones_like(IDs).astype(int)
    # Find which IDs are in match_IDs
    in_match = np.in1d(IDs, match_IDs)
    if require_in_match:
        if np.sum(~in_match) > 0:
            raise IOError("qcat.match_ids: One or more input IDs not in match_IDs")
    rows[~in_match] = -1
    #
    IDs_inmatch = IDs[in_match]
    # Find indices of input IDs in meta table -- first instance in meta only!
    xsorted = np.argsort(match_IDs)
    ypos = np.searchsorted(match_IDs, IDs_inmatch, sorter=xsorted)
    indices = xsorted[ypos]
    rows[in_match] = indices
    return rows

def round_to_day(dt):
    # Convert to unix timestamp in nanoseconds
    ts = dt.astype('datetime64[ns]').astype('int64')
    # Get number of nanoseconds in a day
    day_ns = 24 * 60 * 60 * 1_000_000_000
    # Round to nearest day
    rounded_ts = ((ts + day_ns//2) // day_ns) * day_ns
    # Convert back to datetime64
    return np.array(rounded_ts, dtype='datetime64[ns]')