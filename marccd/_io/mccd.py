import ctypes
import os
import re
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

    with open(path_to_image, "rb") as mccd:
        tiffheader = mccd.seek(1024)
        header_size = ctypes.sizeof(FrameHeader)
        mccdheader = mccd.read(header_size)

        parsed_header, metadata = _parseMCCDHeader(mccdheader)
        image = np.frombuffer(mccd.read(), dtype=np.uint16)
        image = image.reshape(parsed_header["nfast"], parsed_header["nslow"])

    # Remove dimensions from metadata because it will be determined from
    # the image shape
    metadata.pop("dimensions")

    return image, parsed_header, metadata, mccdheader


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
        out.write(marccd.image.flatten().reshape(1, -1))

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
    parsed_header = {}
    metadata = {}

    for name, fieldtype in FrameHeader._fields_:
        info = getattr(FrameHeader, name)
        offset = info.offset
        size = info.size
        raw = header[offset : offset + size]

        # Parse based on type
        if issubclass(fieldtype, ctypes.Array) and issubclass(
            fieldtype._type_, ctypes.c_char
        ):
            # C-style string
            val = raw.rstrip(b"\x00").decode("ascii", "ignore")
        elif issubclass(fieldtype, ctypes.Array):
            # Array of numbers (e.g. c_uint32 * 2)
            basetype = fieldtype._type_
            count = fieldtype._length_
            val = list(ctypes.cast(raw, ctypes.POINTER(basetype * count)).contents)
        elif issubclass(fieldtype, ctypes.c_uint32):
            val = int.from_bytes(raw, "little")
            # print('3')
        elif issubclass(fieldtype, ctypes.c_int32):
            val = int.from_bytes(raw, "little", signed=True)
            # print('4')
        else:
            val = raw  # fallback
            # print('5')
        parsed_header[name] = val

    metadata["dimensions"] = (
        parsed_header["nfast"],
        parsed_header["nslow"],
    )
    metadata["distance"] = float(parsed_header["xtal_to_detector"]) / 1e3
    metadata["center"] = (
        parsed_header["beam_x"] / 1e3,
        parsed_header["beam_y"] / 1e3,
    )
    metadata["pixelsize"] = (
        float(parsed_header["pixelsize_x"]) / 1e3,
        float(parsed_header["pixelsize_y"]) / 1e3,
    )

    metadata["wavelength"] = float(parsed_header["source_wavelength"]) / 1e5

    pattern = r"(\d{4})(\d{4})(\d{4})\.(\d{2}).(\d{9})"
    mmdd, hhmm, yyyy, ss, ns = re.match(
        pattern, parsed_header["acquire_timestamp"]
    ).groups()
    metadata["timestamp"] = f"{yyyy}-{mmdd}-{hhmm}-{ss}-{ns}"
    return parsed_header, metadata


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
    int2byte = struct.Struct("<I")

    # Write image dimensions
    header[80:84] = int2byte.pack(marccd.dimensions[0])
    header[84:88] = int2byte.pack(marccd.dimensions[1])

    # Write detector distance (two places)
    if marccd.distance is not None:
        dist = int(marccd.distance * 1e3)
        header[640:644] = int2byte.pack(dist)
        header[696:700] = int2byte.pack(dist)

    # Write beam center
    if marccd.center is not None:
        centerx = int(marccd.center[0] * 1e3)
        centery = int(marccd.center[1] * 1e3)
        header[644:648] = int2byte.pack(centerx)
        header[648:652] = int2byte.pack(centery)

    # Write pixel size
    if marccd.pixelsize is not None:
        pixelx = int(marccd.pixelsize[0] * 1e3)
        pixely = int(marccd.pixelsize[1] * 1e3)
        header[772:776] = int2byte.pack(pixelx)
        header[776:780] = int2byte.pack(pixely)

    # Write X-ray wavelength
    if marccd.wavelength is not None:
        wavelength = int(np.round(marccd.wavelength * 1e5))
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
    tiffheader = (
        b"II*\x00\x08\x00\x00\x00\r\x00\x00\x01\x04\x00\x01"
        b"\x00\x00\x00\x00\x0f\x00\x00\x01\x01\x04\x00\x01\x00"
        b"\x00\x00\x00\x0f\x00\x00\x02\x01\x03\x00\x01\x00\x00"
        b"\x00\x10\x00\x00\x00\x03\x01\x03\x00\x01\x00\x00\x00"
        b"\x01\x00\x00\x00\x06\x01\x03\x00\x01\x00\x00\x00\x01"
        b"\x00\x00\x00\x11\x01\x04\x00\x01\x00\x00\x00\x00\x10"
        b"\x00\x00\x12\x01\x03\x00\x01\x00\x00\x00\x01\x00\x00"
        b"\x00\x16\x01\x04\x00\x01\x00\x00\x00\x00\x0f\x00\x00"
        b"\x17\x01\x04\x00\x01\x00\x00\x00\x00\x00\xc2\x01\x1a"
        b"\x01\x05\x00\x01\x00\x00\x00\xaa\x00\x00\x00\x1b\x01"
        b"\x05\x00\x01\x00\x00\x00\xb2\x00\x00\x00(\x01\x03\x00"
        b"\x01\x00\x00\x00\x03\x00\x00\x00\x96\x87\x04\x00\x01"
        b"\x00\x00\x00\x00\x04\x00\x00\x00\x00\x00\x00\x80\x96"
        b"\x98\x00\x18Z\x01\x00\x80\x96\x98\x00\x18Z\x01"
    )
    tiffheader += b"\x00" * 839
    return tiffheader


class FrameHeader(ctypes.LittleEndianStructure):
    """
    Python representation of a MarCCD header.

    This class maps to the binary layout of a MarCCD image header,
    starting at byte 1024 in the file. MarCCD uses little-endian
    byte order and packed layout (set with `_pack_=1`). Byte-offsets
    are based on this `reference<https://marxperts.com/man/pdf/marccd_manual.v2.pdf>`
    """

    _pack_ = 1
    _fields_ = [
        # --- File/header format parameters (256 bytes) ---
        ("header_type", ctypes.c_uint32),
        ("header_name", ctypes.c_char * 16),
        ("header_major_version", ctypes.c_uint32),
        ("header_minor_version", ctypes.c_uint32),
        ("header_byte_order", ctypes.c_uint32),
        ("data_byte_order", ctypes.c_uint32),
        ("header_size", ctypes.c_uint32),
        ("frame_type", ctypes.c_uint32),
        ("magic_number", ctypes.c_int32),
        ("compression_type", ctypes.c_uint32),
        ("compression1", ctypes.c_uint32),
        ("compression2", ctypes.c_uint32),
        ("compression3", ctypes.c_uint32),
        ("compression4", ctypes.c_uint32),
        ("compression5", ctypes.c_uint32),
        ("compression6", ctypes.c_uint32),
        ("nheaders", ctypes.c_uint32),
        ("nfast", ctypes.c_uint32),
        ("nslow", ctypes.c_uint32),
        ("depth", ctypes.c_uint32),
        ("record_length", ctypes.c_uint32),
        ("signif_bits", ctypes.c_uint32),
        ("data_type", ctypes.c_uint32),
        ("saturated_value", ctypes.c_uint32),
        ("sequence", ctypes.c_uint32),
        ("nimages", ctypes.c_uint32),
        ("origin", ctypes.c_uint32),
        ("orientation", ctypes.c_uint32),
        ("view_direction", ctypes.c_uint32),
        ("overflow_location", ctypes.c_uint32),
        ("over_8_bits", ctypes.c_uint32),
        ("over_16_bits", ctypes.c_uint32),
        ("multiplexed", ctypes.c_uint32),
        ("nfastimages", ctypes.c_uint32),
        ("nslowimages", ctypes.c_uint32),
        ("darkcurrent_applied", ctypes.c_uint32),
        ("bias_applied", ctypes.c_uint32),
        ("flatfield_applied", ctypes.c_uint32),
        ("distortion_applied", ctypes.c_uint32),
        ("original_header_type", ctypes.c_uint32),
        ("file_saved", ctypes.c_uint32),
        ("n_valid_pixels", ctypes.c_uint32),
        ("defectmap_applied", ctypes.c_uint32),
        ("subimage_nfast", ctypes.c_uint32),
        ("subimage_nslow", ctypes.c_uint32),
        ("subimage_origin_fast", ctypes.c_uint32),
        ("subimage_origin_slow", ctypes.c_uint32),
        ("readout_pattern", ctypes.c_uint32),
        ("saturation_level", ctypes.c_uint32),
        ("orientation_code", ctypes.c_uint32),
        ("frameshift_multiplexed", ctypes.c_uint32),
        ("prescan_nfast", ctypes.c_uint32),
        ("prescan_nslow", ctypes.c_uint32),
        ("postscan_nfast", ctypes.c_uint32),
        ("postscan_nslow", ctypes.c_uint32),
        ("prepost_trimmed", ctypes.c_uint32),
        ("reserve1", ctypes.c_char * ((64 - 55) * 4 - 16)),
        # --- Data statistics (128 bytes) ---
        ("total_counts", ctypes.c_uint32 * 2),
        ("special_counts1", ctypes.c_uint32 * 2),
        ("special_counts2", ctypes.c_uint32 * 2),
        ("min", ctypes.c_uint32),
        ("max", ctypes.c_uint32),
        ("mean", ctypes.c_int32),
        ("rms", ctypes.c_uint32),
        ("n_zeros", ctypes.c_uint32),
        ("n_saturated", ctypes.c_uint32),
        ("stats_uptodate", ctypes.c_uint32),
        ("pixel_noise", ctypes.c_uint32 * 9),
        ("reserve2", ctypes.c_char * ((32 - 13 - 9) * 4)),
        # --- Sample Changer info (256 bytes) ---
        ("barcode", ctypes.c_char * 16),
        ("barcode_angle", ctypes.c_uint32),
        ("barcode_status", ctypes.c_uint32),
        ("reserve2a", ctypes.c_char * ((64 - 6) * 4)),
        # --- Goniostat parameters (128 bytes) ---
        ("xtal_to_detector", ctypes.c_int32),
        ("beam_x", ctypes.c_int32),
        ("beam_y", ctypes.c_int32),
        ("integration_time", ctypes.c_int32),
        ("exposure_time", ctypes.c_int32),
        ("readout_time", ctypes.c_int32),
        ("nreads", ctypes.c_int32),
        ("start_twotheta", ctypes.c_int32),
        ("start_omega", ctypes.c_int32),
        ("start_chi", ctypes.c_int32),
        ("start_kappa", ctypes.c_int32),
        ("start_phi", ctypes.c_int32),
        ("start_delta", ctypes.c_int32),
        ("start_gamma", ctypes.c_int32),
        ("start_xtal_to_detector", ctypes.c_int32),
        ("end_twotheta", ctypes.c_int32),
        ("end_omega", ctypes.c_int32),
        ("end_chi", ctypes.c_int32),
        ("end_kappa", ctypes.c_int32),
        ("end_phi", ctypes.c_int32),
        ("end_delta", ctypes.c_int32),
        ("end_gamma", ctypes.c_int32),
        ("end_xtal_to_detector", ctypes.c_int32),
        ("rotation_axis", ctypes.c_int32),
        ("rotation_range", ctypes.c_int32),
        ("detector_rotx", ctypes.c_int32),
        ("detector_roty", ctypes.c_int32),
        ("detector_rotz", ctypes.c_int32),
        ("total_dose", ctypes.c_int32),
        ("reserve3", ctypes.c_char * ((32 - 29) * 4)),
        # --- Detector parameters (128 bytes) ---
        ("detector_type", ctypes.c_int32),
        ("pixelsize_x", ctypes.c_int32),
        ("pixelsize_y", ctypes.c_int32),
        ("mean_bias", ctypes.c_int32),
        ("photons_per_100adu", ctypes.c_int32),
        ("measured_bias", ctypes.c_int32 * 9),
        ("measured_temperature", ctypes.c_int32 * 9),
        ("measured_pressure", ctypes.c_int32 * 9),
        # --- X-ray source parameters (64 bytes) ---
        ("source_type", ctypes.c_int32),
        ("source_dx", ctypes.c_int32),
        ("source_dy", ctypes.c_int32),
        ("source_wavelength", ctypes.c_int32),
        ("source_power", ctypes.c_int32),
        ("source_voltage", ctypes.c_int32),
        ("source_current", ctypes.c_int32),
        ("source_bias", ctypes.c_int32),
        ("source_polarization_x", ctypes.c_int32),
        ("source_polarization_y", ctypes.c_int32),
        ("source_intensity_0", ctypes.c_int32),
        ("source_intensity_1", ctypes.c_int32),
        ("reserve_source", ctypes.c_char * (2 * 4)),
        # --- X-ray optics parameters (128 bytes) ---
        ("optics_type", ctypes.c_int32),
        ("optics_dx", ctypes.c_int32),
        ("optics_dy", ctypes.c_int32),
        ("optics_wavelength", ctypes.c_int32),
        ("optics_dispersion", ctypes.c_int32),
        ("optics_crossfire_x", ctypes.c_int32),
        ("optics_crossfire_y", ctypes.c_int32),
        ("optics_angle", ctypes.c_int32),
        ("optics_polarization_x", ctypes.c_int32),
        ("optics_polarization_y", ctypes.c_int32),
        ("reserve_optics", ctypes.c_char * (4 * 4)),
        ("reserve5", ctypes.c_char * ((32 - 28) * 4)),
        # --- File parameters (1024 bytes) ---
        ("filetitle", ctypes.c_char * 128),
        ("filepath", ctypes.c_char * 128),
        ("filename", ctypes.c_char * 64),
        ("acquire_timestamp", ctypes.c_char * 32),
        ("header_timestamp", ctypes.c_char * 32),
        ("save_timestamp", ctypes.c_char * 32),
        ("file_comment", ctypes.c_char * 512),
        ("reserve6", ctypes.c_char * (1024 - (128 + 128 + 64 + (3 * 32) + 512))),
        # --- Dataset parameters (512 bytes) ---
        ("dataset_comment", ctypes.c_char * 512),
        # --- User-definable data (512 bytes) ---
        ("user_data", ctypes.c_char * 512),
    ]
