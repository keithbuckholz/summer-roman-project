from astropy.io import fits
import sys

file, key, value, newfile = sys.argv

direct_file = file
direct_fits = fits.open(direct_file)
direct_fits[0].header[key] = value


direct_fits.writeto(newfile, overwrite=True)