from astropy.io import fits
import numpy as np
import sys

ext = [1, 2, 3]

_, filepath, newfile = sys.argv


given_fits = fits.open("%s" %filepath)

for ii in ext:
    given_fits[ii].data = given_fits[ii].data[2000:4000]

given_fits.writeto(newfile, overwrite=True)