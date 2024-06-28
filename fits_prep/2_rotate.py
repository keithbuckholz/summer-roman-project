from astropy.io import fits
import numpy as np
import sys

ext = 1

if len(sys.argv) == 4:
    _, filepath, newfile, k = sys.argv
else:
    _. filepath, ext, newfile, k = sys.argv


given_fits = fits.open("%s" %filepath)

given_fits[ext].data = np.rot90(given_fits[ext].data, k=int(k))
given_fits.writeto(newfile, overwrite=True)