import os
import struct
import numpy as np
from .io import mccd

class MarCCD:
    """
    Read, write, and manipulate images that use the MarCCD format
    """

    def __init__(self, data=None, name=None):
        """
        Initialize MarCCD from file or np.ndarray. If no data argument 
        is given, an empty MarCCD object is returned

        Attributes
        ----------
        image : ndarray
            MarCCD image stored as a numpy array
        name : str
            Name of image

        Parameters
        ----------
        data : str or ndarray
            MarCCD image to read or np.ndarray of image
        name : str
            Name of image. If a filename is provided as data argument,
            name defaults to the filename.
        """
        # Set name if provided
        self.name = name
        
        # Initialize empty MarCCD object
        if data is None:
            self._mccdheader = None
            self.image       = None
            
        # Initialize from file path
        elif isinstance(data, str):
            self.read(data)
            
        # Initialize from np.ndarray
        elif isinstance(data, np.ndarray):
            self._mccdheader = None
            self.image = data

        else:
            raise ValueError(f"Argument is of type: {type(data)}. "
                             f"Expected argument of type str or "
                             f"np.ndarray.")
            
        return

    def read(self, path_to_image):
        """
        Read MCCD image from file, populating fields in MarCCD

        Parameters
        ----------
        path_to_image : str
            Path to MCCD image to read
        """
        mccdheader, image = mccd.read(path_to_image)
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
