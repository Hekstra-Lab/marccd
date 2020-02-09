import os
import struct
import numpy as np
from ._io import mccd

class MarCCD:
    """
    Read, write, and manipulate images that use the MarCCD format

    Attributes
    ----------
    image : ndarray
        MarCCD image stored as a numpy array
    name : str
        Name of image
    dimensions : (int, int)
        Dimensions of MarCCD image in pixels
    distance : float
        Crystal-to-detector distance in millimeters
    center : (float, float)
        Beam center in pixels
    pixelsize : (float, float)
        Pixel size in microns
    wavelength : float
        Wavelength of incident X-ray in angstroms
    """

    def __init__(self, data=None, name=None, distance=None,
                 center=None, pixelsize=None, wavelength=None):
        """
        Initialize MarCCD from file or np.ndarray. If no data argument 
        is given, an empty MarCCD object is returned.

        Parameters
        ----------
        data : str or ndarray
            MarCCD image to read or np.ndarray of image
        name : str
            Name of image. If a filename is provided as data argument,
            name defaults to the filename.
        distance : float
            Crystal-to-detector distance in millimeters
        center : (float, float)
            Beam center in pixels
        pixelsize : (float, float)
            Pixel size in microns
        wavelength : float
            Wavelength of incident X-ray in angstroms
        """
        # Set name if provided
        self.name = name
        
        # Initialize empty MarCCD object
        if data is None:
            self._mccdheader = b'\x00'*3072
            self.image       = None
            
        # Initialize from file path
        elif isinstance(data, str):
            self.read(data)
            
        # Initialize from np.ndarray
        elif isinstance(data, np.ndarray):
            self._mccdheader = b'\x00'*3072
            self.image = data

        else:
            raise ValueError(f"Argument is of type: {type(data)}. "
                             f"Expected argument of type str or "
                             f"np.ndarray.")

        return

    @property
    def dimensions(self):
        if self.image is None:
            return (0, 0)
        else:
            return self.image.shape
    
    def read(self, path_to_image):
        """
        Read MCCD image from file, populating fields in MarCCD

        Parameters
        ----------
        path_to_image : str
            Path to MCCD image to read
        """
        image, metadata, mccdheader = mccd.read(path_to_image)
        self._mccdheader = mccdheader
        self.image = image
        self.metadata = metadata
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
