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

        Notes
        -----
        If arguments are given in addition to an MCCD image, priority
        is given to the provided argument values. The class attributes 
        will be set using the argument values instead of those indicated
        in the MCCD header. 

        Parameters
        ----------
        data : str or ndarray
            MarCCD image to read or np.ndarray of image. If np.ndarray,
            dtype should be np.uint16.
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
        # Initialize all attributes in empty MarCCD object
        self.image       = np.empty((0, 0))
        self.name        = None
        self.distance    = None
        self.center      = None
        self.pixelsize   = None
        self.wavelength  = None
        self._mccdheader = b'\x00'*3072

        # Initialize from np.ndarray
        if isinstance(data, np.ndarray):
            self.image = data.astype(np.uint16)

        # Initialize from file path
        elif isinstance(data, str):
            self.read(data)
            
        elif data is not None:
            raise ValueError(f"Argument is of type: {type(data)}. "
                             f"Expected argument of type str or "
                             f"np.ndarray.")

        # Set attributes if values are provided
        if name is not None:
            self.name = name
        if distance is not None:
            self.distance = distance
        if center is not None:
            self.center = center
        if pixelsize is not None:
            self.pixelsize = pixelsize
        if wavelength is not None:
            self.wavelength = wavelength

        return

    @property
    def dimensions(self):
        return self.image.shape
    
    def read(self, path_to_image):
        """
        Read MCCD image from file, populating fields in MarCCD

        Parameters
        ----------
        path_to_image : str
            Path to MCCD image to read
        """
        # Read image
        image, metadata, mccdheader = mccd.read(path_to_image)

        # Set standard attributes
        self.name = os.path.basename(path_to_image)
        self._mccdheader = mccdheader
        self.image = image

        # Set experimental metadata attributes
        for key in metadata:
            setattr(self, key, metadata[key])

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
