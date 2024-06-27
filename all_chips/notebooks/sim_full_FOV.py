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

os.chdir("/Users/keith/astr/research_astr/summer-roman-project/all_chips/fits_scripts")

from roman_fits_utils import fix_hdr, rotate_img
from roman_seg_map import produce_seg_map


os.chdir("/Users/keith/astr/research_astr/all_chip_fits")

# Functions for dynamic filenaming
file = lambda ii: "GRS_FOV0_roll0_dx0_dy0_SCA%i_direct_final.fits" %ii
newfile = lambda ii: "./ready_fits/rotated_img_%i.fits" %ii
seg_file = lambda ii: "seg_%i.fits" %ii

# Set variables and initiate sims dictionary
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

pad = 100
sims = {}

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

    return None

# Produce segmentation map
def segmentation_map(ii):
    filename = newfile(ii)
    seg_filename = seg_file(ii)

    produce_seg_map(filename, seg_filename)

    return None

# Produce model
def run_sim(ii):
    size = det_sizes["det%i" %ii]
    sims["%i_sim" %ii] = GrismFLT(direct_file=newfile(ii), seg_file=seg_file(ii), pad=pad)
    sims["%i_sim" %ii].compute_full_model(mag_limit=28, compute_size=False, size=size)
    
    return None

# Run all functions
def run_full_sim(ii):
    modify_and_rotate(ii)
    segmentation_map(ii)
    run_sim(ii)

    return None