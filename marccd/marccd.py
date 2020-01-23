import os
import struct
import numpy as np
from .io import mccd

class MarCCD:
    """
    Read, write, and manipulate images that use the MarCCD format
    """

    def __init__(self, data=None):
        """
        Initialize MarCCD from file or np.ndarray. If no data argument 
        is given, an empty MarCCD object is returned

        Parameters
        ----------
        data : str or ndarray (optional)
            MarCCD image to read or np.ndarray of image
        """
        # Initialize empty MarCCD object
        if not data:
            self._tiffheader = None
            self._mccdheader = None
            self.image       = None
        
        # Initialize from file path
        elif isinstance(data, str):
            self.read(data)
            
        # Initialize from np.ndarray
        elif isinstance(data, np.ndarray):
            self.image = data
            
        return

    def read(self, path_to_image):
        """
        Read MCCD image from file, populating fields in MarCCD

        Parameters
        ----------
        path_to_image : str
            Path to MCCD image to read
        """
        tiffheader, mccdheader, image = mccd.read(path_to_image)
        self._tiffheader = tiffheader
        self._mccdheader = mccdheader
        self.image = image
        self.name = os.path.basename(path_to_image)
        return
        
    def write(self, outfile):
        """
        Write MarCCD file of image.

        Parameters
        ----------
        outfile : str
            File to which MarCCD image will be written
        """
        return mccd.write(self, outfile)
