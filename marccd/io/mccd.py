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
    (tiffheader, mccdheader, image) : tuple
        Returns tuple containing the two headers and an ndarray of the 
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

    return tiffheader, mccdheader, image

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
        if marccd._tiffheader:
            out.write(marccd._tiffheader)
        else:
            out.write(b'\x00'*1024)

        # Write MarCCD header
        if marccd._mccdheader:
            header = list(self._mccdheader)
            int2byte = struct.Struct('<I')
            header[80:84] = int2byte.pack(marccd.image.shape[0])
            header[84:88] = int2byte.pack(marccd.image.shape[1])
            out.write(bytes(header))
        else:
            raise AttributeError("_mccdheader attribute was not found")

        # Write image
        out.write(marccd.image.flatten().reshape(1,-1))
            
    return

    
