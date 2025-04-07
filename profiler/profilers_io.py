""" I/O for multiple profilers """

from profiler import io as p_io

from IPython import embed

def write_profilers(profilers:list, outfile:str):

    big_dict = {}

    # Loop me
    for profiler in profilers:
        odict = profiler.to_dict()
        # init?
        if profiler.dataset not in big_dict.keys():
            big_dict[profiler.dataset]= {}
        # Add
        if profiler.missid in big_dict[profiler.dataset].keys():
            raise IOError(f"missid={profiler.missid} already in the dict!!")
        big_dict[profiler.dataset][profiler.missid] = odict
        # Add the profiler platform
        big_dict[profiler.dataset]['platform'] = profiler.platform

    # Finish
    jdict = p_io.jsonify(big_dict, debug=True)
    p_io.savejson(outfile, jdict, overwrite=True)
    print(f'Wrote: {outfile}')