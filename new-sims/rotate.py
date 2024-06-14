from astropy.io import fits
import numpy as np
import sys

filepath, ext, newfile = sys.argv

given_fits = fits.open(file)

given_fits[1].data = np.rot90(given_fits[ext].data)
given_fits.writeto(newfile, overwrite=True)