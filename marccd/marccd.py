import os
import warnings

import numpy as np

from ._io import mccd


class MarCCD:
    """
    Container for diffraction images that use MarCCD format.

    The diffraction image is represented by a numpy ndarray
    that can facilitate analyzing and manipulating the underlying
    data. Experimental metadata can also be stored/changed using the
    object's attributes.

    MarCCD objects can be initialized by reading an image from disk, or
    by directly providing a numpy ndarray.

    Examples
    --------
    >>> # Initialize empty MarCCD object
    >>> from marccd import MarCCD
    >>> MarCCD()
    <marccd.MarCCD with 0x0 pixels at 0x4635073552>

    >>> # Initialize MarCCD from image file and print X-ray wavelength
    >>> img = MarCCD("image.mccd")
    >>> print(img)
    <marccd.MarCCD with 3840x3840 pixels at 0x4688828304>
    >>> print(img.wavelength)
    1.0264

    >>> # Initialize MarCCD from numpy array
    >>> import numpy as np
    >>> image = np.random.randint(0, 100, size=(1000, 1000), dtype=np.uint16)
    >>> MarCCD(image)
    <marccd.MarCCD with 1000x1000 pixels at 0x4646535440>

    Parameters
    ----------
    data : str or ndarray
        MarCCD image to read or np.ndarray of image. If np.ndarray,
        dtype should be np.uint16; if not, they will be coerced to
        np.uint16 and a warning will be generated.
    name : str
        Name of image. If a filename is provided as data argument,
        name defaults to the filename.
    distance : float
        Crystal-to-detector distance in millimeters
    center : (float, float)
        Beam center in pixels
    pixelsize : (float, float)
        Pixel size in microns
    timestamp: str
        Time the image was acquired
    wavelength : float
        Wavelength of incident X-ray in angstroms

    Notes
    -----
    If arguments are given in addition to an MCCD image, priority
    is given to the provided argument values. The class attributes
    will be set using the argument values instead of those indicated
    in the MCCD header.
    """

    def __init__(
        self,
        data=None,
        name=None,
        distance=None,
        center=None,
        pixelsize=None,
        timestamp=None,
        wavelength=None,
    ):
        """
        Initialize MarCCD from file or np.ndarray. If no data argument
        is given, an empty MarCCD object is returned.
        """
        # Initialize all attributes in empty MarCCD object
        self.image = np.empty((0, 0))
        self.name = None
        self.distance = None
        self.center = None
        self.pixelsize = None
        self.timestamp = None
        self.wavelength = None
        self._parsedheader = None
        self._mccdheader = b"\x00" * 3072

        # Initialize from np.ndarray
        if isinstance(data, np.ndarray):
            if data.dtype.type is not np.uint16:
                warnings.warn(
                    f"Data ndarray is of type {data.dtype.type}. "
                    f"This will be coerced to type np.uint16.",
                    UserWarning,
                )
                self.image = data.astype(np.uint16)
            else:
                self.image = data

        # Initialize from file path
        elif isinstance(data, str):
            self.read(data)

        elif data is not None:
            raise ValueError(
                f"Argument is of type: {type(data)}. "
                f"Expected argument of type str or "
                f"np.ndarray."
            )

        # Set attributes if values are provided
        if name is not None:
            self.name = name
        if distance is not None:
            self.distance = distance
        if center is not None:
            self.center = center
        if pixelsize is not None:
            self.pixelsize = pixelsize
        if timestamp is not None:
            self.timestamp = timestamp
        if wavelength is not None:
            self.wavelength = wavelength

        return

    @property
    def image(self):
        """
        MarCCD image as a numpy array

        Returns
        -------
        image : ndarray
            The MarCCD image as a numpy array
        """
        return self.__image

    @image.setter
    def image(self, value):
        """Sets the MarCCD image to provided numpy array"""
        self.__image = value

    @property
    def name(self):
        """
        Name of image

        Returns
        -------
        name : str
            The name of the image
        """
        return self.__name

    @name.setter
    def name(self, value):
        """Sets the name of image to provided value"""
        self.__name = value

    @property
    def dimensions(self):
        """
        Dimensions of MarCCD image in pixels

        Returns
        -------
        dimensions : (int, int)
            The dimensions of the MarCCD image in pixels
        """
        return self.__image.shape

    @property
    def distance(self):
        """
        Crystal-to-detector distance in millimeters

        Returns
        -------
        distance : float
            The crystal-to-detector distance in mm
        """
        return self.__distance

    @distance.setter
    def distance(self, value):
        """Sets the crystal-to-detector distance to provided value"""
        self.__distance = value

    @property
    def center(self):
        """
        Beam center in pixels

        Returns
        -------
        center : (float, float)
            The beam center in pixels
        """
        return self.__center

    @center.setter
    def center(self, value):
        """Sets the beam center to provided value"""
        self.__center = value

    @property
    def pixelsize(self):
        """
        Pixel size in microns

        Returns
        -------
        pixelsize : (float, float)
            The pixel size in microns
        """
        return self.__pixelsize

    @pixelsize.setter
    def pixelsize(self, value):
        """Sets the pixel size to provided value"""
        self.__pixelsize = value

    @property
    def timestamp(self):
        """
        Pixel size in microns

        Returns
        -------
        timestamp : str
            The acquired timestamp of the image formatted
            as YYYY-MMDD-HHmm-ss-nanoseconds
        """
        return self.__timestamp

    @timestamp.setter
    def timestamp(self, value):
        """Sets the pixel size to provided value"""
        self.__timestamp = value

    @property
    def wavelength(self):
        """
        Wavelength of incident X-ray in angstroms

        Returns
        -------
        wavelength : float
            The wavelength of incident X-ray source in angstroms
        """
        return self.__wavelength

    @wavelength.setter
    def wavelength(self, value):
        """Sets the wavelength to provided value"""
        self.__wavelength = value

    def __repr__(self):
        dims = self.dimensions
        return f"<marccd.MarCCD with {dims[0]}x{dims[1]} pixels at 0x{id(self)}>"

    def read(self, path_to_image):
        """
        Read MCCD image from file, populating fields in MarCCD

        Parameters
        ----------
        path_to_image : str
            Path to MCCD image to read
        """
        # Read image
        image, parsed_header, metadata, mccdheader = mccd.read(path_to_image)

        # Set standard attributes
        self.name = os.path.basename(path_to_image)
        self._mccdheader = mccdheader
        self._parsedheader = parsed_header
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
