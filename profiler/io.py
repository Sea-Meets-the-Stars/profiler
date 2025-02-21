
import os



def grab_ext(filename:str):
    """ Simple method to rturn the file extension

    Args:
        filename (str): filename

    Returns:
        str: filename extension
    """

    return os.path.splitext(filename)[1][1:]