import os
import struct
import numpy as np

def read(path_to_image):
    """
    Read MCCD image from file.

    Parameters
    ----------
    path_to_image : str
        Path to MCCD image to read

    Returns
    -------
    (mccdheader, image) : tuple
        Returns tuple containing the mccd header and an ndarray of the 
        image
    """
    
    if not os.path.exists(path_to_image):
        raise ValueError(f"{path} does not exist")

    with open(path_to_image, 'rb') as mccd:

        # Read headers
        tiffheader = mccd.read(1024)
        mccdheader = mccd.read(3072)

        # Read image
        byte2int = struct.Struct("<I")
        dims = (byte2int.unpack(mccdheader[80:84])[0],
                byte2int.unpack(mccdheader[84:88])[0])
        image = np.frombuffer(mccd.read(), dtype=np.int16).reshape(dims)

    return mccdheader, image

def write(marccd, outfile):
    """
    Write MarCCD object to a .mccd file.

    Parameters
    ----------
    marccd : MarCCD
        MarCCD object to write to file
    outfile : str
        File to which MarCCD image will be written
    """
    with open(outfile, "wb") as out:

        # Write TIFF header
        out.write(_getTIFFHeader())

        # Write MarCCD header
        if marccd._mccdheader is not None:
            # header = list(marccd._mccdheader)
            # int2byte = struct.Struct('<I')
            # header[80:84] = int2byte.pack(marccd.image.shape[0])
            # header[84:88] = int2byte.pack(marccd.image.shape[1])
            # out.write(bytes(header))
            out.write(marccd._mccdheader)
        else:
            raise AttributeError("_mccdheader attribute was not found")

        # Write image
        out.write(marccd.image.flatten().reshape(1,-1))
            
    return

def _getTIFFHeader():
    """
    Get the default 1024 byte TIFF header for MCCD images

    Returns
    -------
    tiffheader : bytes
        1024 byte TIFF header
    """
    tiffheader = (b'II*\x00\x08\x00\x00\x00\r\x00\x00\x01\x04\x00\x01'
                  b'\x00\x00\x00\x00\x0f\x00\x00\x01\x01\x04\x00\x01\x00'
                  b'\x00\x00\x00\x0f\x00\x00\x02\x01\x03\x00\x01\x00\x00'
                  b'\x00\x10\x00\x00\x00\x03\x01\x03\x00\x01\x00\x00\x00'
                  b'\x01\x00\x00\x00\x06\x01\x03\x00\x01\x00\x00\x00\x01'
                  b'\x00\x00\x00\x11\x01\x04\x00\x01\x00\x00\x00\x00\x10'
                  b'\x00\x00\x12\x01\x03\x00\x01\x00\x00\x00\x01\x00\x00'
                  b'\x00\x16\x01\x04\x00\x01\x00\x00\x00\x00\x0f\x00\x00'
                  b'\x17\x01\x04\x00\x01\x00\x00\x00\x00\x00\xc2\x01\x1a'
                  b'\x01\x05\x00\x01\x00\x00\x00\xaa\x00\x00\x00\x1b\x01'
                  b'\x05\x00\x01\x00\x00\x00\xb2\x00\x00\x00(\x01\x03\x00'
                  b'\x01\x00\x00\x00\x03\x00\x00\x00\x96\x87\x04\x00\x01'
                  b'\x00\x00\x00\x00\x04\x00\x00\x00\x00\x00\x00\x80\x96'
                  b'\x98\x00\x18Z\x01\x00\x80\x96\x98\x00\x18Z\x01'
                  b'\x00'*839)
    return tiffheader
