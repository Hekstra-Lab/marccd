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
    (image, metadata, mccdheader) : tuple
        Returns tuple containing the ndarray of the image, experimental 
        metadata and the mccdheader
    """
    
    if not os.path.exists(path_to_image):
        raise ValueError(f"{path_to_image} does not exist")

    with open(path_to_image, 'rb') as mccd:

        # Read headers
        tiffheader = mccd.read(1024)
        mccdheader = mccd.read(3072)

        # Parse experimental metadata
        metadata = _parseMCCDHeader(mccdheader)
        
        # Read image
        image = np.frombuffer(mccd.read(), dtype=np.int16)
        image = image.reshape(metadata["dimensions"])

    # Remove dimensions from metadata because it will be determined from
    # the image shape
    metadata.pop("dimensions")
        
    return image, metadata, mccdheader

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
            out.write(_writeMCCDHeader(marccd))
        else:
            raise AttributeError("_mccdheader attribute was not found")

        # Write image
        out.write(marccd.image.flatten().reshape(1,-1))
            
    return

def _parseMCCDHeader(header):
    """
    Parse experimental metadata from MCCD header. Byte-offsets of 
    experimental parameters are based on this `reference 
    <http://www.sb.fsu.edu/~xray/Manuals/marCCD165header.html>`_

    Parameters
    ----------
    header : bytes
        MCCD header
    """
    byte2int = struct.Struct("<I")
    metadata = {}
    metadata["dimensions"] = (byte2int.unpack(header[80:84])[0],
                              byte2int.unpack(header[84:88])[0])
    metadata["distance"] = float(byte2int.unpack(header[640:644])[0])/1e3
    metadata["center"] = (float(byte2int.unpack(header[644:648])[0])/1e3,
                          float(byte2int.unpack(header[648:652])[0])/1e3)
    metadata["pixelsize"] = (float(byte2int.unpack(header[772:776])[0])/1e3,
                             float(byte2int.unpack(header[776:780])[0])/1e3)
    metadata["wavelength"] = float(byte2int.unpack(header[908:912])[0])/1e5
    return metadata

def _writeMCCDHeader(marccd):
    """
    Write the MCCD header using the experimental metadata from the MarCCD
    object.

    Parameters
    ----------
    marccd : MarCCD
        MarCCD object from which to get experimental metadata
    """
    # Set up header for indexing 
    header = list(marccd._mccdheader)
    int2byte = struct.Struct('<I')

    # Write image dimensions
    header[80:84] = int2byte.pack(marccd.dimensions[0])
    header[84:88] = int2byte.pack(marccd.dimensions[1])

    # Write detector distance (two places)
    if marccd.distance is not None:
        dist = int(marccd.distance*1e3)
        header[640:644] = int2byte.pack(dist)
        header[696:700] = int2byte.pack(dist)

    # Write beam center
    if marccd.center is not None:
        centerx = int(marccd.center[0]*1e3)
        centery = int(marccd.center[1]*1e3)
        header[644:648] = int2byte.pack(centerx)
        header[648:652] = int2byte.pack(centery)    
        
    # Write pixel size
    if marccd.pixelsize is not None:
        pixelx = int(marccd.pixelsize[0]*1e3)
        pixely = int(marccd.pixelsize[1]*1e3)
        header[772:776] = int2byte.pack(pixelx)
        header[776:780] = int2byte.pack(pixely)

    # Write X-ray wavelength
    if marccd.wavelength is not None:
        wavelength = int(np.round(marccd.wavelength*1e5))
        header[908:912] = int2byte.pack(wavelength)
    
    return bytes(header)
    
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
                  b'\x98\x00\x18Z\x01\x00\x80\x96\x98\x00\x18Z\x01')
    tiffheader += b'\x00'*839
    return tiffheader
