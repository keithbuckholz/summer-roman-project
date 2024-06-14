from astropy.io import fits
import sys

_, file, key, value, newfile = sys.argv

direct_file = file
direct_fits = fits.open(direct_file)
direct_fits[0].header["INSTRUME"] = "ROMAN"
direct_fits[0].header["FILTER"] = "det1"

direct_fits.writeto(newfile, overwrite=True)