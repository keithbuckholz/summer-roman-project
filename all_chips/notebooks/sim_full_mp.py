
# General imports
import os
import numpy as np
import matplotlib.pyplot as plt

# Segmentation
from astropy.io import fits
from photutils.segmentation import SourceFinder, make_2dgaussian_kernel, SourceCatalog
from photutils.background import Background2D, MedianBackground
from astropy.convolution import convolve

# grizli
from grizli.model import GrismFLT
import grizli

############################ roman_fits_utils
from astropy.io import fits
import numpy as np

def fix_hdr(filename, new_filename, hdr_dict, overwrite=True):
    """
    Function that adds/changes header information according to a supplied dictionary.

    Parameters
	----------
	filename: str
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
    assert isinstance(filename, str) and isinstance(new_filename, str), "Filenames must be strings"
    assert isinstance(hdr_dict, dict), 'Must supply a dictionary of header changes with format: {"key": "ext;value"}'
    assert isinstance(overwrite, bool), "overwrite argument must be boolean"

    # Open fits file
    direct_fits = fits.open(filename)

    # Iterate through the dictionary keys, setting keys = to matching values
    for key in hdr_dict.keys():
        try:
            ext, value = hdr_dict[key].split(";") # split "ext;value" into seperate variables
            ext = int(ext)
        except ValueError as e:
            msg = 'Dictionary values must have format "ext;hdr_value"'
            raise ValueError(msg)

        # Set the key=value in appropriate header
        direct_fits[ext].header[key] = value

    # Save the altered fits file
    direct_fits.writeto(new_filename, overwrite=overwrite)
    return 0

def rotate_img(filename, new_filename, k=3, ext=1, overwrite=True):
    """
    Roman grism disperses in y, but aXeSim only disperses in x. This function rotates an image array 90-degrees clockwise. 
    Perform this three times before dispersion and once after for proper dispersion pattern (I think).

        Parameters
        ----------
        filename: str
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
    assert isinstance(filename, str) and isinstance(new_filename, str), "Filenames must be strings"
    assert isinstance(k, int) and isinstance(ext, int), "number of rotations (k) and fits extension (ext) must be type int"

    # Open fits file
    given_fits = fits.open(filename)

    # Rotate image array
    given_fits[ext].data = np.rot90(given_fits[ext].data, k=k)

    # Save altered fits file
    given_fits.writeto(new_filename, overwrite=overwrite)
    return 0
#################### END roman_fits_utils

#################### roman_seg_map
# Segmentation
from astropy.io import fits
from photutils.segmentation import SourceFinder, make_2dgaussian_kernel
from photutils.background import Background2D, MedianBackground
from astropy.convolution import convolve

def produce_seg_map(direct_file, seg_file, ext=1, **kwargs):
    """
    Function that produces and returns a segmentation map of a provided fits.

    Parameters
        ----------
        direct_file: str
            filepath to fits file containing direct image you need a segmentation map for
        ext: int, optional
            extenension of the fits file you would like to access. Default: 1
        
        Returns
        -------
        seg_map: np.array
            Segmentation map of objects in supplied direct image.

    """

    # Parse kwargs
    kwarg_keys = kwargs.keys()

    # Default args for Background2D() and SourceFinder()
    default_bkg_args = {"box_size":    (511, 511),
                        "filter_size": (3, 3)}

    default_finder_args = {"npixels":  7, 
                           "nlevels":  32, 
                           "contrast": 0.001}

    # Background_args
    bwargs = {}
    for arg in default_bkg_args.keys():
        # if argument in kwargs: use kwargs value
        # else: use default values
        if arg in kwarg_keys:
            bwargs[arg] = kwargs[arg]
        else:
            bwargs[arg] = default_bkg_args[arg]

    # Background_args
    sfwargs = {}
    for arg in default_finder_args.keys():
        # if argument in kwargs: use kwargs value
        # else: use default values
        if arg in kwarg_keys:
            sfwargs[arg] = kwargs[arg]
        else:
            sfwargs[arg] = default_finder_args[arg]
    
    # Open image
    direct_fits = fits.open(direct_file)
    data, header = (direct_fits[ext].data, direct_fits[ext].header)

    # Subtract background
    bkg_estimator = MedianBackground()
    bkg = Background2D(data, **bwargs)
    data -= bkg.background

    # Convolve image
    kernel = make_2dgaussian_kernel(3.0, 5)
    convolved_data = convolve(data, kernel)

    # Instantiate the SourceFinder and set threshold
    finder = SourceFinder(**sfwargs)
    threshold = 2 * bkg.background_rms

    seg_map = finder(convolved_data, threshold)

    # Save seg_map as fits
    fits.writeto(seg_file, seg_map, header=header,overwrite=True)
    return seg_map
###################### END roman_seg_map

os.chdir("/Users/keith/astr/research_astr/all_chip_fits")

# Functions for dynamic filenaming
file = lambda ii: "GRS_FOV0_roll0_dx0_dy0_SCA%i_direct_final.fits" %ii
newfile = lambda ii: "./ready_fits/rotated_img_%i.fits" %ii
seg_file = lambda ii: "seg_%i.fits" %ii

# Set variables and initiate sims dictionary
pad = 200
det_sizes = {"det1": 77,
            "det2": 80,
            "det3": 88,
            "det4": 180,
            "det5": 195,
            "det6": 209,
            "det7": 279,
            "det8": 302,
            "det9": 328,
            "det10": 98,
            "det11": 101,
            "det12": 110,
            "det13": 203,
            "det14": 217,
            "det15": 232,
            "det16": 303,
            "det17": 326,
            "det18": 353
            }

# Prepare fits
def modify_and_rotate(ii):
    filename = file(ii)
    modified_hdr_name = "modified_hdr_%i.fits" %ii
    rotated_img_name = newfile(ii)

    hdr_dict = {"INSTRUME": "0;ROMAN",
                "FILTER":   "0;det%i" %ii,
                "CONFFILE": "1;/Users/keith/astr/research_astr/FOV0/Roman.det%i.07242020.conf" %ii}

    fix_hdr(filename, modified_hdr_name, hdr_dict)

    rotate_img(modified_hdr_name, rotated_img_name)

    print("Fits %i prepared" %ii)

    return None

# Produce segmentation map
def segmentation_map(ii):
    filename = newfile(ii)
    seg_filename = seg_file(ii)

    produce_seg_map(filename, seg_filename)

    print("Seg map %i made" %ii)

    return None

# Produce model
def run_sim(ii):
    size = det_sizes["det%i" %ii]
    foo = GrismFLT(direct_file=newfile(ii), seg_file=seg_file(ii), pad=pad)

    print("Model %i instantiated" %ii)

    foo.compute_full_model(mag_limit=28, compute_size=False, size=size)
    
    print("Model %i completed" %ii)

    return None

# Run all functions
def run_full_sim(ii):
    modify_and_rotate(ii)
    segmentation_map(ii)
    foo = run_sim(ii)

    return foo
