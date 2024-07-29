from astropy.io import fits
import numpy as np

def modify_hdr(original_filename, new_filename, hdr_dict, overwrite=True):
    """
    Function that adds/changes header information according to a supplied dictionary.

    Parameters
	----------
	original_filename: str
		Name of the fits file to be altered.

    new_filename: str
        Name the altered file will be saved as.
    
    hdr_dict: dict
        Python dictionary of new/altered header information. Should be formation as {hdr_key: ext;hdr_value}.
        This way the dictionary value can be split at the semi-colon into the fits extension where the header
        data is the be changed and the appropriate value for that change.

    overwrite: bool, optional
        If new_filename already exists, should it be overwritten? default=True
    """

    # Check that arguments are of appropriate type
    assert isinstance(original_filename, str) and isinstance(new_filename, str), "Filenames must be strings"
    assert isinstance(hdr_dict, dict), 'Must supply a dictionary of header changes with format: {"key": "ext;value"}'
    assert isinstance(overwrite, bool), "overwrite argument must be boolean"

    # Open fits file
    direct_fits = fits.open(original_filename)

    # Iterate through the dictionary keys, setting keys = to matching values
    for key in hdr_dict.keys():
        try:
            ext, value = hdr_dict[key].split(";") # split "ext;value" into seperate variables
            ext = int(ext)
        except ValueError as e:
            msg = 'Dictionary values must have format "ext;hdr_value"'
            raise ValueError(msg)

        # Set the key=value in appropriate header
        # try:
            # value = float(value)
        # except ValueError:
        #     pass
        direct_fits[ext].header[key] = value

    # Save the altered fits file
    direct_fits.writeto(new_filename, overwrite=overwrite)
    return 0

def rotate_img(original_filename, new_filename, k=3, ext=1, overwrite=True):
    """
    Roman grism disperses in y, but aXeSim only disperses in x. This function rotates an image array 90-degrees clockwise. 
    Perform this three times before dispersion and once after for proper dispersion pattern (I think).

        Parameters
        ----------
        original_filename: str
            Name of the fits file to be altered.

        new_filename: str
            Name the altered file will be saved as.
        
        k: int, optional
            Number of clockwise 90-degree rotations to be performed. Should be 3 prior to dispersion and 1 after. default=3
        
        ext: int, optional
            Fits extension of the image array to be rotated. default=1

        overwrite: bool, optional
            If new_filename already exists, should it be overwritten? default=True
    """

    # Check arguments are of expected type
    assert isinstance(original_filename, str) and isinstance(new_filename, str), "Filenames must be strings"
    assert isinstance(k, int) and isinstance(ext, int), "number of rotations (k) and fits extension (ext) must be type int"

    # Open fits file
    given_fits = fits.open(original_filename)

    # Rotate image array
    given_fits[ext].data = np.rot90(given_fits[ext].data, k=k)

    # Save altered fits file
    given_fits.writeto(new_filename, overwrite=overwrite)
    return 0